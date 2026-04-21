# Secrets Detection and Drift Detection

## Table of Contents
- [Gitleaks](#gitleaks)
- [TruffleHog](#trufflehog)
- [Gitleaks vs TruffleHog](#gitleaks-vs-trufflehog)
- [Terraform-Specific Secret Patterns](#terraform-specific-secret-patterns)
- [Drift Detection](#drift-detection)
- [OpenTofu Compatibility](#opentofu-compatibility)

---

## Gitleaks

Gitleaks is a fast, lightweight secret scanner that uses regex patterns to detect hardcoded credentials in Git repositories. It scans commit history, staged changes, and the working directory.

### Installation

```bash
brew install gitleaks
# or
docker pull zricethezav/gitleaks
```

### Usage

```bash
# Scan repo (all commits)
gitleaks detect --source . -v

# Scan only staged changes (ideal for pre-commit)
gitleaks protect --staged -v

# Scan specific directory (not git-aware)
gitleaks detect --source . --no-git -v

# Output as JSON for CI processing
gitleaks detect --source . --report-format json --report-path gitleaks-report.json

# Output as SARIF
gitleaks detect --source . --report-format sarif --report-path gitleaks.sarif
```

Version note: Gitleaks v8.19+ uses `gitleaks git --pre-commit --staged` instead of `gitleaks protect --staged`. The `--pre-commit` flag is required to get the staged-changes-only behavior. Check your installed version and use the appropriate subcommand.

### Configuration (.gitleaks.toml)

Customize rules for Terraform-specific patterns:

```toml
# .gitleaks.toml
title = "Terraform Security Gitleaks Config"

[extend]
useDefault = true

# Custom rule: Terraform variable defaults containing secrets
[[rules]]
id = "terraform-variable-secret-default"
description = "Terraform variable with secret in default value"
regex = '''variable\s+"[^"]*(?:password|secret|token|key|api_key)[^"]*"\s*\{[^}]*default\s*=\s*"[^"]{8,}"'''
tags = ["terraform", "secret"]

# Custom rule: AWS provider hardcoded credentials
[[rules]]
id = "terraform-aws-hardcoded-creds"
description = "Hardcoded AWS credentials in Terraform provider"
regex = '''(?:access_key|secret_key)\s*=\s*"(?:AKIA|aws_)[A-Za-z0-9/+=]{16,}"'''
tags = ["terraform", "aws"]

# Allowlist paths and patterns
[allowlist]
paths = [
    '''\.terraform/''',
    '''\.terraform\.lock\.hcl''',
    '''terraform\.tfstate.*''',
]

regexes = [
    '''EXAMPLE_KEY''',
    '''REPLACE_ME''',
]
```

---

## TruffleHog

TruffleHog goes beyond regex matching — it classifies 800+ secret types and **verifies** whether detected secrets are live by testing them against their APIs. This dramatically reduces false positives.

### Installation

```bash
brew install trufflehog
# or
docker pull trufflesecurity/trufflehog
```

### Usage

```bash
# Scan Git repo (full history)
trufflehog git file://. --only-verified

# Scan filesystem (no git history)
trufflehog filesystem . --only-verified

# Scan since a specific commit (fast for CI — only scan new commits)
trufflehog git file://. --since-commit HEAD~5 --only-verified

# Output as JSON
trufflehog git file://. --only-verified --json > trufflehog-results.json

# Scan with all findings (not just verified)
trufflehog git file://. --results verified,unverified
```

### Key Flags

| Flag | Purpose |
|------|---------|
| `--only-verified` | Only report secrets confirmed to be live/active |
| `--results verified,unverified` | Report both verified and unverified |
| `--no-update` | Skip auto-update check (faster in CI) |
| `--fail` | Exit with non-zero code on findings |
| `--include-detectors` | Scan only with specific detector types |
| `--exclude-detectors` | Skip specific detector types |

---

## Gitleaks vs TruffleHog

| Feature | Gitleaks | TruffleHog |
|---------|----------|------------|
| Detection method | Regex patterns | Regex + entropy + verification |
| Verification | No (pattern match only) | Yes (tests if secret is live) |
| Speed | Very fast | Moderate (verification adds time) |
| False positives | Higher | Very low (with `--only-verified`) |
| Secret types | 160+ | 800+ |
| SARIF output | Native | Requires conversion layer |
| Best for | Pre-commit hooks, fast CI gates | Thorough scans, audit trails |

**Recommended approach**: Use Gitleaks in pre-commit hooks (fast, catches most issues) and TruffleHog in CI (thorough, verified results). For pre-commit hook and CI pipeline setup, see `workflow-and-gates.md` and `ci-cd-integration.md`.

---

## Terraform-Specific Secret Patterns

### Common Anti-Patterns

```hcl
# WRONG: Hardcoded provider credentials
provider "aws" {
  access_key = "AKIAIOSFODNN7EXAMPLE"
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}

# WRONG: Default values containing real secrets
variable "db_password" {
  default = "SuperSecret123!"  # Will appear in state file
}

# WRONG: Secrets in terraform.tfvars committed to repo
# terraform.tfvars
database_password = "production-password-123"

# WRONG: Secrets in local_exec provisioners
provisioner "local-exec" {
  command = "curl -H 'Authorization: Bearer sk-live-abc123' https://api.example.com"
}
```

### Correct Patterns

```hcl
# RIGHT: Use environment variables
provider "aws" {
  # Reads AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY from env
}

# RIGHT: Use a secrets manager data source
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "prod/database/password"
}

resource "aws_db_instance" "main" {
  password = data.aws_secretsmanager_secret_version.db_password.secret_string
}

# RIGHT: Use sensitive variables without defaults
variable "db_password" {
  type      = string
  sensitive = true
  # No default — must be provided via env var, CLI, or tfvars
}

# RIGHT: Use Azure Key Vault
data "azurerm_key_vault_secret" "db_password" {
  name         = "database-password"
  key_vault_id = data.azurerm_key_vault.main.id
}

# RIGHT: Use GCP Secret Manager
data "google_secret_manager_secret_version" "db_password" {
  secret = "database-password"
}
```

### .gitignore for Terraform

```gitignore
# Terraform
*.tfstate
*.tfstate.backup
*.tfstate.*.backup
.terraform/
*.tfvars       # Contains variable values, often secrets
!example.tfvars # Keep example files
crash.log
override.tf
override.tf.json
*_override.tf
*_override.tf.json
```

### Secret Incident Response

For the full incident response procedure when a secret is detected, see `workflow-and-gates.md` § Secret Incident Response.

---

## Drift Detection

Drift occurs when the actual cloud infrastructure diverges from the Terraform state — caused by manual console changes, out-of-band automation, or emergency fixes.

### Drift Detection Model

Use two complementary paths:
- **Native drift path**: `plan -refresh-only` on a schedule for authoritative drift against current state.
- **Unmanaged-resource path**: driftctl (where adopted) to identify resources not represented in state.

### Native Drift Path (Recommended Baseline)

```bash
terraform init -lockfile=readonly
terraform plan -refresh-only -detailed-exitcode -out refresh.plan
# Exit code 0 = no changes, 1 = error, 2 = changes detected (drift)
```

**Known bug:** There are confirmed issues (hashicorp/terraform#35117, #37406) where `-refresh-only -detailed-exitcode` returns exit code 2 (changes detected) even when the console output says "no changes detected." Pin your Terraform version and test this behavior in your environment before relying on it as an automated gate. Consider parsing the plan output as a secondary signal.

Scheduled CI job example:

```yaml
# GitHub Actions drift check
name: Drift Detection
on:
  schedule:
    - cron: '0 6 * * 1'  # Every Monday at 6 AM

jobs:
  drift:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3

      - run: terraform init
      - run: terraform plan -detailed-exitcode -refresh-only
        id: drift
        continue-on-error: true

      - name: Alert on drift
        if: steps.drift.outcome == 'failure'
        run: |
          echo "::warning::Infrastructure drift detected!"
          # Send Slack/email notification here
```

Operational guidance:
- Run with read-only cloud credentials where provider permits refresh.
- Include workspace/account labels in ticket metadata.
- Suppress known ephemeral resources through policy, not ad hoc script filters.

### driftctl (Maintenance Mode)

driftctl by Snyk compares Terraform state against the live cloud environment using read-only API access. It has been in maintenance mode since June 2023 — it still works but receives no new features.

```bash
# Install
brew install driftctl

# Scan AWS (reads state from local backend)
driftctl scan

# Scan with S3 remote backend
driftctl scan --from tfstate+s3://my-bucket/terraform.tfstate

# Scan with multiple state files
driftctl scan \
  --from tfstate+s3://bucket/env/prod/terraform.tfstate \
  --from tfstate+s3://bucket/env/staging/terraform.tfstate

# Output as JSON
driftctl scan --output json://drift-report.json

# Filter specific resource types
driftctl scan --filter "Type=='aws_iam_role'"

# Generate HTML report
driftctl scan --output html://drift-report.html
```

Interpretation:
- `unmanaged`: cloud objects exist but are absent from state.
- `missing`: state references objects no longer present in cloud.
- `changed`: object attributes diverge from state expectations.

### Driftive (Active Alternative)

Driftive is a newer open-source alternative with explicit OpenTofu and Terragrunt support:

```bash
# Install
pip install driftive

# Scan for drift
driftive --repo-path /path/to/terraform

# With Slack notifications
driftive --repo-path . --slack-url $SLACK_WEBHOOK
```

### Drift Detection Strategy Comparison

| Method | Pros | Cons |
|--------|------|------|
| `terraform plan -refresh-only` | No extra tools, authoritative | Requires full TF credentials, slow for large state |
| driftctl | Read-only access, finds unmanaged resources | Maintenance mode, AWS-focused |
| Driftive | Active development, OpenTofu support | Newer, smaller community |
| Scheduled CI runs | Automated, repeatable | Delayed detection (not real-time) |

**Recommended approach**: Run `terraform plan -detailed-exitcode -refresh-only` on a weekly cron schedule in CI. For environments that need to detect unmanaged resources (shadow IT), supplement with driftctl or Driftive.

### Drift Response Policy

- **Critical perimeter drift** (public ingress, IAM broadening, encryption disabled): immediate block/fix.
- **Non-critical drift**: time-bound remediation ticket with owner.
- **Repeat drift on same control**: escalate to platform engineering root-cause review.
- Every drift exception must include compensating control and expiration.

---

## OpenTofu Compatibility

### Compatibility Map

| Area | Terraform | OpenTofu | Review implication |
|------|-----------|----------|-------------------|
| HCL static scanners (Trivy/Checkov/Terrascan/KICS/TFLint) | Supported | Generally supported (same HCL input) | Keep same static scanner pipeline |
| Plan JSON policy input (OPA/Rego) | `terraform show -json` | `tofu show -json` equivalent structure | Reuse policy logic; validate with fixtures |
| Sentinel policy runtime | Terraform Cloud/Enterprise native | No equivalent native runtime | Prefer OPA/Rego for TF/OpenTofu parity |
| Secret scanners (Gitleaks/TruffleHog) | VCS/data-source based | Same | No change required |
| Infracost plan integration | Mature support | Supported with version-dependent behavior | Validate in CI smoke tests; pin known-good version |

### OpenTofu + Infracost Validation Checklist

- Run the release-gate Infracost flow against a representative OpenTofu repo.
- Confirm parsed resource count and cost deltas match expected parity for unchanged infrastructure.
- Pin Infracost version only after successful OpenTofu smoke tests; track upgrades as explicit dependency PRs.
- Re-run smoke tests whenever OpenTofu or provider major versions change.

### Migration-Safe Control Strategy

When moving from Terraform to OpenTofu:
1. Freeze policy bundle versions first (avoid policy and engine change in one release).
2. Re-run policy tests against both Terraform and OpenTofu plan fixtures.
3. Keep dual-run mode for one release window: compare finding deltas before full cutover.
4. Promote OpenTofu-only after parity threshold is met for high/critical controls.
