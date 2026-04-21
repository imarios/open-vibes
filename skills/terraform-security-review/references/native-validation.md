# Native Terraform Validation Features

Terraform and OpenTofu include built-in validation mechanisms that enforce security constraints without external tools. These run at plan or apply time and require no additional installation.

## Table of Contents
- [Variable Validation](#variable-validation)
- [Preconditions and Postconditions](#preconditions-and-postconditions)
- [Check Blocks](#check-blocks)
- [Feature Comparison](#feature-comparison)

---

## Variable Validation

Validate input variables at plan time before any resources are created. Stable since Terraform v0.13. Cross-variable references added in Terraform v1.9 (June 2024).

### Security-Focused Examples

```hcl
variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the VPC"

  validation {
    condition     = can(cidrnetmask(var.vpc_cidr))
    error_message = "Must be a valid IPv4 CIDR block (e.g., 10.0.0.0/16)."
  }

  validation {
    condition     = tonumber(split("/", var.vpc_cidr)[1]) >= 16
    error_message = "CIDR prefix must be /16 or smaller to limit blast radius."
  }
}

variable "instance_type" {
  type        = string
  description = "EC2 instance type — restricted to approved families"

  validation {
    condition     = contains(["t3.micro", "t3.small", "t3.medium", "m5.large"], var.instance_type)
    error_message = "Only approved instance types are allowed."
  }
}

variable "environment" {
  type        = string
  description = "Deployment environment"

  validation {
    condition     = can(regex("^(prod|staging|dev)-[a-z0-9]+$", var.environment))
    error_message = "Environment must match naming convention: prod-*, staging-*, or dev-*."
  }
}

variable "db_password" {
  type      = string
  sensitive = true

  validation {
    condition     = length(var.db_password) >= 16
    error_message = "Database password must be at least 16 characters."
  }
}
```

### Cross-Variable Validation (Terraform 1.9+)

```hcl
variable "enable_public_access" {
  type = bool

  validation {
    condition     = !(var.enable_public_access && var.environment == "prod")
    error_message = "Public access is not allowed in production environments."
  }
}
```

### Gotchas

- Pre-1.9: validation blocks can **only** reference the variable itself (`var.<self>`). Cross-variable references cause an error.
- A single variable can have **multiple** validation blocks — Terraform evaluates them in order and reports the first failure.
- OpenTofu supports variable validation but cross-variable validation (the TF 1.9 feature) has known compatibility issues — see [opentofu/opentofu#2191](https://github.com/opentofu/opentofu/issues/2191).

---

## Preconditions and Postconditions

Contract-based assertions on resources and data sources. Introduced in Terraform v1.2 (June 2022). Fully supported in OpenTofu.

- **Preconditions** run **before** resource creation — validate inputs and assumptions. Cannot use `self`.
- **Postconditions** run **after** resource creation — verify guarantees. Can use `self`.
- Both cause **hard errors** that halt the operation.

### Security Examples

```hcl
resource "aws_s3_bucket" "data" {
  bucket = "my-secure-bucket"

  lifecycle {
    precondition {
      condition     = var.enable_encryption == true
      error_message = "Encryption must be enabled for S3 buckets."
    }

    postcondition {
      condition     = self.server_side_encryption_configuration != null
      error_message = "S3 bucket was created without server-side encryption."
    }
  }
}

resource "aws_instance" "app" {
  ami           = var.ami_id
  instance_type = var.instance_type

  metadata_options {
    http_tokens = "required"
  }

  lifecycle {
    postcondition {
      condition     = self.root_block_device[0].encrypted == true
      error_message = "Root EBS volume must be encrypted."
    }
  }
}

data "aws_iam_policy" "boundary" {
  name = var.permissions_boundary_name

  lifecycle {
    postcondition {
      condition     = self.policy != ""
      error_message = "Permissions boundary policy must exist and not be empty."
    }
  }
}
```

### Gotchas

- Preconditions and postconditions live inside `lifecycle {}`, not at the resource top level.
- They work on resources and data sources. **Output blocks** support preconditions only (not postconditions) — and preconditions go directly inside the output block without a `lifecycle` wrapper.
- They do **not** currently work directly on module calls.
- Multiple precondition/postcondition blocks are allowed in a single lifecycle block.

---

## Check Blocks

Standalone assertions that produce **warnings only** (never block operations). Introduced in Terraform v1.5 (June 2023). Fully supported in OpenTofu.

Check blocks can define their own scoped `data` sources for runtime validation.

### Security Examples

```hcl
check "lb_security" {
  assert {
    condition     = length(aws_lb.main.security_groups) > 0
    error_message = "Load balancer must have at least one security group."
  }

  assert {
    condition     = aws_lb.main.enable_deletion_protection == true
    error_message = "Load balancer deletion protection must be enabled."
  }
}

check "api_health" {
  data "http" "api" {
    url = "https://api.example.com/health"
  }

  assert {
    condition     = data.http.api.status_code == 200
    error_message = "API health check failed — returned ${data.http.api.status_code}."
  }
}

check "bucket_encryption" {
  assert {
    condition     = aws_s3_bucket.data.server_side_encryption_configuration != null
    error_message = "S3 bucket encryption is not configured — investigate."
  }
}
```

### Continuous Validation (HCP Terraform)

In HCP Terraform (formerly Terraform Cloud), enabling health checks on a workspace causes check blocks to run **daily** (health assessments). This enables ongoing security monitoring — e.g., verifying SSL certificates haven't expired or security configurations haven't drifted. This feature is **not available** in open-source Terraform CLI or OpenTofu.

### Gotchas

- Check blocks **never block** operations. For enforcement, use preconditions/postconditions or variable validation.
- The scoped `data` block inside a check is only available within that check block.
- Check blocks can contain multiple assert blocks — all are evaluated.

---

## Feature Comparison

| Feature | Stable Version | OpenTofu | On Failure | Best For |
|---------|---------------|----------|------------|----------|
| Variable validation | v0.13 (cross-var: v1.9) | Yes (cross-var has caveats) | Hard error at plan | Input constraints (CIDR, instance types, naming) |
| Precondition | v1.2 | Yes | Hard error before create | Assumption checks (encryption enabled, policy exists). Works on resources, data sources, and outputs. |
| Postcondition | v1.2 | Yes | Hard error after create | Guarantee checks (EBS encrypted, SG attached). Works on resources and data sources only (not outputs). |
| Check block | v1.5 | Yes | Warning only | Ongoing health/security validation |

### When to Use Each

- **Variable validation**: First line of defense. Catches bad inputs before anything happens.
- **Preconditions**: Guard against incorrect assumptions about the environment (data source results, feature flags).
- **Postconditions**: Verify that created resources meet security invariants (encryption, network isolation).
- **Check blocks**: Non-blocking monitoring for conditions that should be investigated but shouldn't halt deploys.

### Layering with External Tools

Native validation is complementary to external scanners — not a replacement:
- Variable validation catches bad inputs; scanners catch bad configurations.
- Preconditions/postconditions enforce per-resource contracts; OPA/Rego enforces org-wide policies.
- Check blocks monitor runtime health; drift detection catches out-of-band changes.
