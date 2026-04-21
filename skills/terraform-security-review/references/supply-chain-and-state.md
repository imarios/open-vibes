# Cloud Controls, Module Security, State Security, and Supply Chain

## Table of Contents
- [Cloud Provider Security Priorities](#cloud-provider-security-priorities)
- [Provider Constraint Pinning and Lockfile Controls](#provider-constraint-pinning-and-lockfile-controls)
- [Terraform Cloud/Enterprise Workspace Security](#terraform-cloudenterprise-workspace-security)
- [Module Supply-Chain Controls](#module-supply-chain-controls)
- [Import and Moved Block Security Review](#import-and-moved-block-security-review)
- [State File Security](#state-file-security)

---

## Cloud Provider Security Priorities

### AWS Review Focus

- **IAM**: reject wildcard actions/resources for human or CI roles unless constrained by conditions.
- **Compute**: enforce IMDSv2 on EC2 launch templates/instances (see `policy-as-code.md` § AWS: Enforce IMDSv2 for Rego example).
- **Storage**: require block-public-access posture for S3 and encryption at rest with KMS where required.
- **Networking**: deny `0.0.0.0/0` on administrative ports; review egress-all defaults.
- **Logging**: require CloudTrail + CloudWatch/centralized logs in each account boundary.

### Azure Review Focus

- **Identity**: prefer Managed Identity over client secrets/service principal passwords.
- **Storage**: disable unnecessary public network access and require private endpoint patterns for sensitive data planes.
- **Key management**: enforce Key Vault purge protection + soft delete.
- **Network isolation**: require private endpoints for data plane services when feasible.
- **Policy alignment**: verify resources map to Azure Policy baseline, not only Terraform policy.

### GCP Review Focus

- **IAM**: avoid primitive roles (`roles/editor`, `roles/owner`) for workloads.
- **Service accounts**: deny unmanaged key creation; prefer workload identity federation.
- **Storage**: enforce uniform bucket-level access and public access prevention (see `policy-as-code.md` § GCP: Enforce Uniform Bucket-Level Access).
- **Network**: restrict broad ingress and enforce firewall logging on sensitive segments.
- **Auditability**: ensure audit log sinks are immutable and centrally retained.

---

## Provider Constraint Pinning and Lockfile Controls

Use explicit provider constraints and enforce lockfile immutability in CI:

```hcl
terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}
```

### Hardening Checks

- `.terraform.lock.hcl` is committed and code-reviewed.
- CI runs `terraform init -lockfile=readonly`.
- Provider upgrades happen through explicit dependency-update PRs only.
- Use `~>` constraints for providers; never leave versions unconstrained.

---

## Terraform Cloud/Enterprise Workspace Security

Apply these checks when using remote runs and Sentinel policy sets:

- **Team RBAC**: separates `read`, `plan`, `apply`, and workspace-admin capabilities.
- **Variable sets**: follow least privilege and are scoped only to required workspaces.
- **Sensitive variables**: marked sensitive and never echoed in run logs.
- **Run triggers**: explicit and documented; avoid broad fan-out triggers across unrelated workspaces.
- **Policy sets and run tasks**: mandatory for production workspaces, with break-glass flow tracked and time-bound.

---

## Module Supply-Chain Controls

### High-Confidence Module Hygiene

- Pin module versions (`version = "x.y.z"`) or immutable commit SHAs for `git::` sources.
- Disallow mutable refs (`main`, floating tags) in production workspaces.
- Maintain allowlist of trusted registries/org namespaces.
- Require provenance metadata in module READMEs: maintainer, security contact, changelog policy.
- Run scanner suite against module code before publishing to private registry.

### Risk Signals That Should Block Promotion

- Module consumes broad credentials by default.
- Module creates internet-exposed endpoints without explicit opt-in variable.
- Module lacks outputs for security controls (e.g., missing encryption key IDs).
- Module upgrades contain breaking permission expansion without migration notes.

---

## Import and Moved Block Security Review

`import` and `moved` blocks are valid modernization tools but can hide risky ownership transitions if unreviewed.

```hcl
import {
  to = aws_s3_bucket.logs
  id = "prod-logs-bucket"
}

moved {
  from = aws_security_group.legacy
  to   = module.network.aws_security_group.main
}
```

### Review Controls

- For each `import`, require proof of current cloud ownership, tagging, and baseline policy compliance.
- After import, run full static and plan-time security scans before allowing apply.
- For each `moved`, confirm the destination address preserves attached IAM/policy dependencies and monitoring.
- Reject moves that orphan encryption keys, logging sinks, or network policies.

---

## State File Security

Treat state as sensitive because it can include infrastructure topology and secret-adjacent values.

### Backend Controls by Cloud

| Cloud | Backend | Key Controls |
|-------|---------|-------------|
| AWS | S3 | Bucket encryption, versioning, least-privilege IAM, access logging. State locking: use `use_lockfile = true` (native S3 locking, TF 1.10+) instead of the deprecated `dynamodb_table` approach. |
| Azure | Blob Storage | Private container, RBAC-only access, optional CMK, immutable retention where required |
| GCP | GCS | Uniform bucket-level access, CMEK where mandated, object versioning, tight IAM scopes |

### Operational Controls

- Block local state in shared CI agents.
- Do not export state/plan files into public artifact stores.
- Rotate backend access credentials with short-lived federation where possible.
- Alert on direct backend object access outside CI/Terraform principals.
- Never store secrets in state via variable defaults — use vault data sources instead.
