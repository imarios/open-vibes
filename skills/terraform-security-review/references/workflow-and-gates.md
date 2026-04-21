# Workflow Gates and Pre-Commit Setup

## Table of Contents
- [Repository Bootstrap](#repository-bootstrap)
- [Pre-Commit Hooks](#pre-commit-hooks)
- [PR Gate Strategy](#pr-gate-strategy)
- [Secret Incident Response](#secret-incident-response)
- [Plan-Time Gate](#plan-time-gate)
- [De-duplication and Exception Hygiene](#de-duplication-and-exception-hygiene)
- [Release and Runtime Controls](#release-and-runtime-controls)
- [Legacy Repo Baseline Strategy](#legacy-repo-baseline-strategy)

---

## Repository Bootstrap

One-time setup per repository:

1. Pin IaC and scanner versions in toolchain docs (or container image tags).
2. Commit `.terraform.lock.hcl` and enforce read-only lockfile behavior in CI (`terraform init -lockfile=readonly`).
3. Create `security/exceptions.yaml` with mandatory fields: `control_id`, `resource`, `justification`, `owner`, `expires_on`, `ticket`.
4. Add `results/` and `.sarif/` output folders to `.gitignore`.
5. Define a dedicated read-only cloud role for `plan` and drift jobs (write permissions are not required for review gates).

---

## Pre-Commit Hooks

The `pre-commit-terraform` framework by Anton Babenko is the standard for local Terraform security checks.

### .pre-commit-config.yaml

```yaml
repos:
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.96.2  # Pin to a specific version
    hooks:
      # Formatting
      - id: terraform_fmt

      # Validation
      - id: terraform_validate

      # Linting
      - id: terraform_tflint
        args:
          - --args=--config=__GIT_WORKING_DIR__/.tflint.hcl

      # Security scanning with Trivy (successor to tfsec)
      - id: terraform_trivy
        args:
          - --args=--severity=HIGH,CRITICAL
          - --args=--ignorefile=__GIT_WORKING_DIR__/.trivyignore

      # Documentation generation
      - id: terraform_docs
        args:
          - --hook-config=--path-to-file=README.md
          - --hook-config=--add-to-existing-file=true
          - --hook-config=--create-file-if-not-exist=true

      # Lock file integrity
      - id: terraform_providers_lock
        args:
          - --args=-platform=linux_amd64
          - --args=-platform=darwin_amd64
          - --args=-platform=darwin_arm64

  # Checkov as a separate pre-commit hook
  - repo: https://github.com/bridgecrewio/checkov
    rev: 3.2.300
    hooks:
      - id: checkov
        args:
          - --quiet
          - --compact
          - --skip-check=CKV_AWS_18,CKV_AWS_144

  # Secrets detection
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.21.2
    hooks:
      - id: gitleaks

  - repo: https://github.com/trufflesecurity/trufflehog
    rev: v3.82.13
    hooks:
      - id: trufflehog
        entry: trufflehog filesystem --no-update --fail
        args:
          - --only-verified
```

### Installation

```bash
# Install pre-commit
pip install pre-commit

# Install hooks defined in .pre-commit-config.yaml
pre-commit install

# Run all hooks against all files (useful for first-time setup)
pre-commit run --all-files

# Run a specific hook
pre-commit run terraform_trivy --all-files
```

### Alternative: Local Hooks

Teams that prefer not to pull external repos can use local hooks with system entry points:

```yaml
repos:
  - repo: local
    hooks:
      - id: terraform-fmt
        name: terraform fmt check
        entry: terraform fmt -check -recursive
        language: system
        pass_filenames: false
      - id: tflint
        name: tflint
        entry: tflint --recursive
        language: system
        pass_filenames: false
      - id: trivy-config
        name: trivy config quick scan
        entry: trivy config --severity HIGH,CRITICAL --exit-code 1 .
        language: system
        pass_filenames: false
      - id: gitleaks-staged
        name: gitleaks staged
        entry: gitleaks git --pre-commit --staged --redact --exit-code 1
        language: system
        pass_filenames: false
```

Version note for Gitleaks: v8.19+ uses `gitleaks git --pre-commit --staged` (the `--pre-commit` flag is required to get the old `protect` behavior). Pre-v8.19 uses `gitleaks protect --staged`.

### Optional Pre-Push (Heavier)

```bash
trufflehog git file://. --since-commit HEAD~50 --results=verified,unknown --json
```

---

## PR Gate Strategy

### Execution Order

Run in this order to fail quickly and reduce spend:

1. `fmt` / `validate` / `init -lockfile=readonly`
2. `tflint --recursive`
3. Static IaC scanners (`trivy`, `checkov`, optionally `kics` or `terrascan`)
4. Secrets scanners (`gitleaks`, `trufflehog`)
5. Findings normalizer + severity gate

### Gate Levels

**Hard gates** (block merge):
- CRITICAL and HIGH severity findings from Trivy or Checkov (not covered by active exception)
- Any verified secret detected by Gitleaks/TruffleHog
- Any secret finding in production paths (e.g., `live/prod/**`) regardless of verification
- TFLint errors (invalid resource types, missing required providers)

**Soft gates** (warn but allow merge):
- MEDIUM severity findings
- Infracost threshold warnings
- Checkov checks marked in `soft-fail-on`

**Informational** (no blocking):
- LOW severity findings
- Cost breakdown comments
- Documentation generation diffs

### Implementation Pattern

Use `exit-code` and severity flags to control blocking behavior:

```bash
# Hard gate: exit 1 on HIGH/CRITICAL
trivy config --severity HIGH,CRITICAL --exit-code 1 .

# Soft gate: always exit 0, but report findings
checkov -d . --soft-fail-on CKV_AWS_79 || true

# Conditional: fail only on new findings (not existing)
checkov -d . --baseline .checkov.baseline
```

---

## Secret Incident Response

Triggered by any confirmed secret finding:

1. **Revoke or disable** the exposed credential immediately.
2. **Rotate** the secret in the source system and all dependent workloads.
3. **Audit** provider/service logs for suspicious usage between exposure and revocation.
4. **Remove** the secret from repository history and regenerate derived artifacts if needed.
5. **Record** incident ticket with root cause, blast radius, and prevention action (policy, hook, or IAM hardening).

---

## Plan-Time Gate

Static scans miss computed values and dynamic blocks. Run plan-time scanning for high assurance before merge-to-main or pre-apply:

```bash
terraform init -lockfile=readonly
terraform plan -out tfplan.binary
terraform show -json tfplan.binary > tfplan.json

# Checkov plan scan
checkov -f tfplan.json --framework terraform_plan \
  -o sarif --output-file-path console,results/checkov-plan.sarif

# OPA/Conftest policy evaluation
conftest test tfplan.json -p policy/opa --all-namespaces -o json > results/opa-plan.json

# Module-level security invariants
terraform test -json > results/terraform-test.json
```

Use `terraform test` for module-level security invariants that should not depend on external policy engines (e.g., required tags, forbidden CIDRs, mandatory encryption flags).

**Sentinel path** (if Terraform Cloud/Enterprise): evaluate `tfplan/v2` policies in policy sets and block run on `hard-mandatory` failures.

---

## De-duplication and Exception Hygiene

- De-duplicate using the normalized key from `static-analysis-tools.md` § Finding Normalization.
- Merge equivalent findings into a single ticket with multiple evidence links.
- Auto-close exceptions that are expired or no longer matched.
- Reject exception entries without owner or expiration date.

---

## Release and Runtime Controls

**Before apply**:
- All policy checks pass
- No active critical findings
- Infracost diff is within approved budget/risk envelope

```bash
infracost breakdown --path . --format json --out-file results/infracost-base.json
infracost diff --path . --compare-to results/infracost-base.json \
  --format json --out-file results/infracost-diff.json
```

**After apply** (scheduled):
- `terraform plan -refresh-only -detailed-exitcode` (see `secrets-and-drift.md` § Drift Detection)
- Drift ticketing for exit code `2` and unmanaged resources

---

## Legacy Repo Baseline Strategy

If baseline security debt is high, gate on *new or worsened* risk:

1. Create signed baseline snapshots per tool:
   ```bash
   # Checkov baseline
   checkov -d . --create-baseline
   # Creates .checkov.baseline — commit this file

   # Subsequent runs compare against baseline
   checkov -d . --baseline .checkov.baseline
   ```
2. PR must not increase critical count.
3. PR must not introduce new control IDs in high/critical bands.
4. Force full cleanup milestones with dated targets; do not let delta-only mode become permanent.
