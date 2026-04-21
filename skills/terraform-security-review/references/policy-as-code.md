# Policy-as-Code for Terraform

## Table of Contents
- [Policy Model Design](#policy-model-design)
- [OPA/Rego with Conftest](#oparego-with-conftest)
- [Understanding Plan JSON Structure](#understanding-plan-json-structure)
- [Real-World Policy Examples](#real-world-policy-examples)
- [Helper Library](#helper-library)
- [Unknown-Value Safe Patterns](#unknown-value-safe-patterns)
- [Sentinel](#sentinel)
- [Policy Testing](#policy-testing)
- [Policy Promotion Model](#policy-promotion-model)
- [CI/CD Integration](#cicd-integration)
- [Policy Failure Triage Fields](#policy-failure-triage-fields)

---

## Policy Model Design

Evaluate policy against Terraform/OpenTofu plan JSON (`terraform show -json` or `tofu show -json`) for highest signal:
- It includes expanded module addresses.
- Resolved variables/defaults.
- Pending resource actions (`create`, `update`, `delete`).

Policy result classes:
- **`deny`**: hard block for merge/apply.
- **`warn`**: visible risk accepted temporarily.
- **`advice`**: non-blocking optimization suggestions.

---

## OPA/Rego with Conftest

Open Policy Agent (OPA) evaluates policies written in Rego against JSON data. Conftest is a CLI wrapper around OPA optimized for structured files like Terraform plan JSON.

### Setup

```bash
# Install Conftest
brew install conftest
# or
curl -sfL https://raw.githubusercontent.com/open-policy-agent/conftest/master/install.sh | sh

# Install OPA (for policy testing)
brew install opa
```

### Workflow

```bash
# 1. Generate plan JSON
terraform plan -out=tfplan.binary
terraform show -json tfplan.binary > tfplan.json

# 2. Evaluate policies
conftest test tfplan.json --policy policy/ --all-namespaces

# 3. With specific output format
conftest test tfplan.json --policy policy/ -o json
conftest test tfplan.json --policy policy/ -o table
```

### Policy File Structure

```
policy/
├── main.rego           # General policies
├── aws/
│   ├── s3.rego         # S3-specific policies
│   ├── iam.rego        # IAM policies
│   ├── compute.rego    # EC2/instance policies
│   └── networking.rego # VPC/SG policies
├── azure/
│   ├── storage.rego
│   ├── tls.rego
│   └── regions.rego
├── gcp/
│   ├── storage.rego
│   └── compute.rego
├── lib/
│   └── helpers.rego    # Shared helper functions
└── tests/
    └── *_test.rego     # Policy tests
```

---

## Understanding Plan JSON Structure

The plan JSON has this structure — understanding it is essential for writing correct Rego policies:

```json
{
  "planned_values": {
    "root_module": {
      "resources": [
        {
          "type": "aws_s3_bucket",
          "name": "example",
          "values": { "bucket": "my-bucket", "tags": {} }
        }
      ]
    }
  },
  "resource_changes": [
    {
      "type": "aws_s3_bucket",
      "change": {
        "actions": ["create"],
        "after": { "bucket": "my-bucket" },
        "after_unknown": { "arn": true }
      }
    }
  ],
  "configuration": {
    "root_module": {
      "resources": [
        {
          "type": "aws_s3_bucket",
          "expressions": { "bucket": { "constant_value": "my-bucket" } }
        }
      ]
    }
  }
}
```

- Use `resource_changes` for evaluating what will change.
- Use `planned_values` for the final desired state.
- Use `configuration` for the raw HCL expressions.
- Use `after_unknown` to detect computed fields (see § Unknown-Value Safe Patterns).

---

## Real-World Policy Examples

### AWS: Enforce Required Tags

```rego
# policy/aws/tags.rego
package terraform.aws.tags

import rego.v1

required_tags := {"Owner", "Environment", "CostCenter", "Project"}

taggable_types := {
    "aws_instance", "aws_s3_bucket", "aws_db_instance",
    "aws_eks_cluster", "aws_lambda_function", "aws_vpc",
    "aws_subnet", "aws_security_group", "aws_rds_cluster",
    "aws_elasticache_cluster", "aws_sqs_queue", "aws_sns_topic",
}

deny contains msg if {
    resource := input.resource_changes[_]
    resource.change.actions[_] == "create"
    taggable_types[resource.type]
    tags := object.get(resource.change.after, "tags", {})
    tags_set := {t | tags[t]}
    missing := required_tags - tags_set
    count(missing) > 0
    msg := sprintf(
        "%s '%s' is missing required tags: %v",
        [resource.type, resource.name, missing]
    )
}
```

### AWS: Restrict Instance Types

```rego
# policy/aws/compute.rego
package terraform.aws.compute

import rego.v1

allowed_families := {"t3", "t3a", "m5", "m6i", "c5", "c6i", "r5", "r6i"}

deny contains msg if {
    resource := input.resource_changes[_]
    resource.type == "aws_instance"
    resource.change.actions[_] == "create"
    instance_type := resource.change.after.instance_type
    family := split(instance_type, ".")[0]
    not allowed_families[family]
    msg := sprintf(
        "Instance '%s' uses disallowed type '%s'. Allowed families: %v",
        [resource.name, instance_type, allowed_families]
    )
}
```

### AWS: Enforce S3 Encryption and Block Public Access

```rego
# policy/aws/s3.rego
package terraform.aws.s3

import rego.v1

deny contains msg if {
    resource := input.resource_changes[_]
    resource.type == "aws_s3_bucket"
    resource.change.actions[_] == "create"
    acl := object.get(resource.change.after, "acl", "private")
    acl != "private"
    msg := sprintf(
        "S3 bucket '%s' has non-private ACL '%s'. All buckets must be private.",
        [resource.name, acl]
    )
}

deny contains msg if {
    buckets := {r.name |
        r := input.resource_changes[_]
        r.type == "aws_s3_bucket"
        r.change.actions[_] == "create"
    }
    blocks := {r.change.after.bucket |
        r := input.resource_changes[_]
        r.type == "aws_s3_bucket_public_access_block"
    }
    missing := buckets - blocks
    count(missing) > 0
    some name in missing
    msg := sprintf(
        "S3 bucket '%s' is missing aws_s3_bucket_public_access_block",
        [name]
    )
}
```

### AWS: Enforce IMDSv2 for EC2

```rego
# policy/aws/imds.rego
package terraform.aws.imds

import rego.v1

deny contains msg if {
    resource := input.resource_changes[_]
    resource.type == "aws_instance"
    resource.change.actions[_] == "create"
    metadata := object.get(resource.change.after, "metadata_options", [])
    not metadata_enforced(metadata)
    msg := sprintf(
        "Instance '%s' must enforce IMDSv2 via metadata_options.http_tokens = 'required'",
        [resource.name]
    )
}

metadata_enforced(metadata) if {
    m := metadata[_]
    m.http_tokens == "required"
}

metadata_enforced(metadata) if {
    is_object(metadata)
    metadata.http_tokens == "required"
}
```

### Azure: Enforce HTTPS and TLS

```rego
# policy/azure/tls.rego
package terraform.azure.tls

import rego.v1

deny contains msg if {
    resource := input.resource_changes[_]
    resource.type == "azurerm_app_service"
    resource.change.actions[_] == "create"
    not resource.change.after.https_only == true
    msg := sprintf(
        "App Service '%s' must have https_only = true",
        [resource.name]
    )
}

deny contains msg if {
    resource := input.resource_changes[_]
    resource.type == "azurerm_storage_account"
    resource.change.actions[_] == "create"
    tls := object.get(resource.change.after, "min_tls_version", "TLS1_0")
    tls != "TLS1_2"
    msg := sprintf(
        "Storage account '%s' must use TLS 1.2 (has '%s')",
        [resource.name, tls]
    )
}
```

AzureRM v4 note: do not write policies against deprecated fields like `enable_https_traffic_only`; enforce current attributes and resource semantics instead.

### Azure: Restrict Regions

```rego
# policy/azure/regions.rego
package terraform.azure.regions

import rego.v1

allowed_regions := {"eastus", "eastus2", "westus2", "westeurope", "northeurope"}

deny contains msg if {
    resource := input.resource_changes[_]
    resource.change.actions[_] == "create"
    location := object.get(resource.change.after, "location", "")
    location != ""
    not allowed_regions[lower(location)]
    msg := sprintf(
        "%s '%s' uses disallowed region '%s'. Allowed: %v",
        [resource.type, resource.name, location, allowed_regions]
    )
}
```

### Azure: Block Public Network Access on Storage

```rego
# policy/azure/storage.rego
package terraform.azure.storage

import rego.v1

deny contains msg if {
    rc := input.resource_changes[_]
    rc.type == "azurerm_storage_account"
    rc.change.after.public_network_access_enabled == true
    msg := sprintf("%s allows public network access", [rc.address])
}
```

### GCP: Enforce Uniform Bucket-Level Access

```rego
# policy/gcp/storage.rego
package terraform.gcp.storage

import rego.v1

deny contains msg if {
    resource := input.resource_changes[_]
    resource.type == "google_storage_bucket"
    resource.change.actions[_] == "create"
    uba := object.get(resource.change.after, "uniform_bucket_level_access", false)
    uba != true
    msg := sprintf(
        "GCS bucket '%s' must enable uniform_bucket_level_access",
        [resource.name]
    )
}
```

### GCP: Require Private GKE Clusters

```rego
# policy/gcp/gke.rego
package terraform.gcp.gke

import rego.v1

deny contains msg if {
    resource := input.resource_changes[_]
    resource.type == "google_container_cluster"
    resource.change.actions[_] == "create"
    private_config := object.get(
        resource.change.after, "private_cluster_config", []
    )
    not is_private(private_config)
    msg := sprintf(
        "GKE cluster '%s' must use private_cluster_config with enable_private_nodes = true",
        [resource.name]
    )
}

is_private(config) if {
    c := config[_]
    c.enable_private_nodes == true
}

is_private(config) if {
    is_object(config)
    config.enable_private_nodes == true
}
```

### Cross-Cloud: Deny Overly Permissive CIDR Blocks

```rego
# policy/networking.rego
package terraform.networking

import rego.v1

sensitive_ports := {22, 3389, 5432, 3306, 1433, 27017, 6379, 9200}

deny contains msg if {
    resource := input.resource_changes[_]
    resource.type == "aws_security_group_rule"
    resource.change.actions[_] == "create"
    resource.change.after.type == "ingress"

    cidrs := object.get(resource.change.after, "cidr_blocks", [])
    cidrs[_] == "0.0.0.0/0"

    port := resource.change.after.from_port
    sensitive_ports[port]

    msg := sprintf(
        "Security group rule allows 0.0.0.0/0 ingress on port %d — restrict source CIDR",
        [port]
    )
}
```

---

## Helper Library

```rego
# policy/lib/helpers.rego
package terraform.helpers

import rego.v1

resources_by_type(type) := [r |
    r := input.resource_changes[_]
    r.type == type
]

is_create_or_update(resource) if {
    resource.change.actions[_] == "create"
}

is_create_or_update(resource) if {
    resource.change.actions[_] == "update"
}

managed_changes := [rc |
    rc := input.resource_changes[_]
    rc.mode == "managed"
    not rc.change.actions[_] == "delete"
]

get_default(obj, key, default_val) := val if {
    val := obj[key]
} else := default_val
```

---

## Unknown-Value Safe Patterns

Computed fields can be unknown at plan time. Treat unknown security-critical fields as deny or warn-by-default:

```rego
package terraform.security

import rego.v1

warn contains msg if {
    rc := input.resource_changes[_]
    rc.type == "aws_db_instance"
    rc.change.after.storage_encrypted == null
    rc.change.after_unknown.storage_encrypted == true
    msg := sprintf("%s encryption is unknown at plan time", [rc.address])
}
```

This pattern prevents silently passing resources whose security posture cannot be determined until apply time.

---

## Sentinel

Sentinel is HashiCorp's commercial policy-as-code framework for Terraform Cloud/Enterprise. Unlike OPA, it integrates natively with Terraform run workflows.

### Sentinel Policy Structure

```
sentinel/
├── sentinel.hcl         # Policy set configuration
├── policies/
│   ├── require-tags.sentinel
│   ├── restrict-instance-types.sentinel
│   └── deny-public-ingress.sentinel
└── test/
    ├── require-tags/
    │   ├── pass.hcl
    │   └── fail.hcl
    └── restrict-instance-types/
        ├── pass.hcl
        └── fail.hcl
```

### sentinel.hcl

```hcl
policy "require-tags" {
  source            = "./policies/require-tags.sentinel"
  enforcement_level = "hard-mandatory"  # Cannot be overridden
}

policy "restrict-instance-types" {
  source            = "./policies/restrict-instance-types.sentinel"
  enforcement_level = "soft-mandatory"  # Admins can override
}

policy "deny-public-ingress" {
  source            = "./policies/deny-public-ingress.sentinel"
  enforcement_level = "advisory"  # Warning only
}
```

### Enforcement Levels

| Level | Behavior | Use case |
|-------|----------|----------|
| `advisory` | Warn but allow | New policies being rolled out, low-risk checks |
| `soft-mandatory` | Block by default, admin can override | Important but with known exceptions |
| `hard-mandatory` | Block unconditionally | Security-critical, compliance requirements |

### Example: Require Tags

```python
# policies/require-tags.sentinel
import "tfplan/v2" as tfplan

required_tags = ["Owner", "Environment", "CostCenter"]

allResources = filter tfplan.resource_changes as _, rc {
    rc.mode is "managed" and
    (rc.change.actions contains "create" or rc.change.actions contains "update")
}

violations = []
for allResources as _, resource {
    tags = resource.change.after.tags else {}
    for required_tags as tag {
        if tag not in tags {
            append(violations, resource.address + " missing tag: " + tag)
        }
    }
}

main = rule {
    length(violations) is 0
}
```

### Example: Deny Public Ingress on Admin Ports

```sentinel
import "tfplan/v2" as tfplan

public_admin_ingress = func(rc) {
  rc.type is "aws_security_group_rule" and
  rc.change.actions contains "create" and
  rc.change.after.type is "ingress" and
  rc.change.after.cidr_blocks contains "0.0.0.0/0" and
  (
    (rc.change.after.from_port <= 22 and rc.change.after.to_port >= 22) or
    (rc.change.after.from_port <= 3389 and rc.change.after.to_port >= 3389)
  )
}

main = rule {
  all tfplan.resource_changes as _, rc {
    not public_admin_ingress(rc)
  }
}
```

### Example: Require Explicit Module Version Pinning

```sentinel
import "tfconfig/v2" as tfconfig

is_pinned = func(mc) {
  mc.version is not null and mc.version matches "^[0-9]+\\.[0-9]+\\.[0-9]+$"
}

main = rule {
  all tfconfig.module_calls as _, mc {
    is_pinned(mc)
  }
}
```

**Platform constraint**: Sentinel is available only in Terraform Cloud/Enterprise. For Terraform/OpenTofu parity, prefer OPA/Rego with Conftest.

---

## Policy Testing

### Testing OPA/Rego Policies

OPA has a built-in test framework. Test files use `_test.rego` suffix:

```rego
# policy/aws/tags_test.rego
package terraform.aws.tags_test

import rego.v1
import data.terraform.aws.tags

test_deny_missing_tags if {
    result := tags.deny with input as {
        "resource_changes": [{
            "type": "aws_instance",
            "name": "test",
            "change": {
                "actions": ["create"],
                "after": {
                    "tags": {"Owner": "team-x"}
                }
            }
        }]
    }
    count(result) > 0
}

test_allow_all_tags if {
    result := tags.deny with input as {
        "resource_changes": [{
            "type": "aws_instance",
            "name": "test",
            "change": {
                "actions": ["create"],
                "after": {
                    "tags": {
                        "Owner": "team-x",
                        "Environment": "prod",
                        "CostCenter": "eng-123",
                        "Project": "api"
                    }
                }
            }
        }]
    }
    count(result) == 0
}

test_skip_non_taggable if {
    result := tags.deny with input as {
        "resource_changes": [{
            "type": "aws_iam_policy",
            "name": "test",
            "change": {
                "actions": ["create"],
                "after": {}
            }
        }]
    }
    count(result) == 0
}
```

Run tests:

```bash
# Run all policy tests
opa test policy/ -v

# Run with coverage
opa test policy/ --coverage --format=json
```

### Testing Sentinel Policies

```hcl
# test/require-tags/fail.hcl
mock "tfplan/v2" {
  module {
    source = "testdata/mock-plan-no-tags.sentinel"
  }
}

test {
  rules = {
    main = false  # Expect policy to fail
  }
}
```

Run with `sentinel test`.

---

## Policy Promotion Model

- Start new rules in audit mode (`warn`) for 1-2 release cycles.
- Promote to hard deny only after false-positive review and exception process validation.
- Version policy bundles separately from IaC repos for independent rollback.
- Require unit tests for every deny rule and at least one bypass-attempt test fixture.

### Policy Versioning

Store policies in a separate Git repository and pin versions:

```bash
# Pull policies from a shared repo
conftest pull git::https://github.com/org/terraform-policies.git//policy
conftest test tfplan.json --policy policy/
```

This allows central policy management while individual repos consume specific versions.

---

## CI/CD Integration

For full platform-specific CI pipeline patterns, see `ci-cd-integration.md`. Brief Conftest invocation examples:

### GitHub Actions

```yaml
- name: Run OPA policies
  run: |
    conftest test tfplan.json \
      --policy policy/ \
      --all-namespaces
```

### GitLab CI

```yaml
policy-check:
  stage: validate
  image: openpolicyagent/conftest:latest
  script:
    - conftest test tfplan.json --policy policy/ --all-namespaces
```

---

## Policy Failure Triage Fields

Store these fields in normalized findings for fast remediation:

| Field | Purpose |
|-------|---------|
| `control_id` | Stable, org-owned identifier |
| `policy_engine` | `rego` or `sentinel` |
| `address` | Terraform resource address |
| `evidence` | Minimal JSON pointer into plan |
| `owner` | Responsible team/individual |
| `expiry` | Exception expiration date |
