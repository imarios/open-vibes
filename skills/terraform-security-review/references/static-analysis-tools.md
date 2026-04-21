# Static Analysis Tools for Terraform Security

## Table of Contents
- [Capability Map](#capability-map)
- [Selection Strategy](#selection-strategy)
- [Trivy (successor to tfsec)](#trivy)
- [Checkov](#checkov)
- [Terrascan](#terrascan)
- [KICS](#kics)
- [TFLint](#tflint)
- [Infracost](#infracost)
- [Tool Comparison Matrix](#tool-comparison-matrix)
- [tfsec-to-Trivy Migration](#tfsec-to-trivy-migration)
- [Finding Normalization](#finding-normalization)
- [SARIF Strategy](#sarif-strategy)
- [Operational Controls](#operational-controls)

---

## Capability Map

| Tool | Primary role | Best input | Key output formats | Notable strengths | Common blind spots |
|------|-------------|------------|-------------------|-------------------|-------------------|
| Trivy config | IaC misconfiguration + optional secret/license scanning | HCL, plan JSON | `sarif`, `json`, `table` | Fast multi-IaC engine, broad policy corpus, easy SARIF upload | Plan-time computed values not fully visible unless separately evaluated |
| Checkov | IaC misconfig + graph/context checks + plan scanning | HCL, `terraform show -json` output | `sarif`, `json`, `junitxml`, `cyclonedx` | Strong graph checks, supports `terraform_plan` framework, 1,000+ built-in policies | Can produce noisy overlaps with Trivy/KICS without de-duplication |
| ~~Terrascan~~ | **ARCHIVED Nov 2025** by Tenable | — | — | Migrate existing Rego policies to Conftest or Trivy | No further updates or security patches |
| KICS | Query-based IaC/SAST misconfiguration scanner | HCL and many IaC formats | `sarif`, `json`, `html`, `junit` | Large query library (2,400+), good cross-stack support | Query overlap with Checkov/Trivy can inflate duplicate findings |
| TFLint | Terraform-specific lint/provider best-practice checks | HCL | `default`, `json`, `sarif` | Catches provider/resource usage issues scanners miss | Not a full policy engine; low coverage for org-specific governance |
| Infracost | Cost policy and spend-risk guardrail | HCL, plan JSON | `json`, `table`, diff outputs | Detects suspicious cost jumps and unapproved expensive resources | Not a direct security scanner; complementary gate only |
| Gitleaks | Secret detection in git history/working tree | Git repo / commits | `sarif`, `json`, `junit`, `csv` | High-signal git-focused scanning, 160+ secret types, baselines | Not cloud-validation aware (secret may be inactive) |
| TruffleHog | Secret detection + verification against services | Git, filesystem, images, registries | `json` | Verifies many credential types to reduce false positives | SARIF requires conversion layer; runtime can be heavier |

---

## Selection Strategy

| Review mode | Minimum stack | Why this stack |
|-------------|--------------|---------------|
| Fast PR gate (minutes) | `tflint` + `trivy config` + `gitleaks` | High signal with low runtime for developer feedback |
| Security hard gate (merge/apply) | `tflint` + `trivy` + `checkov` + `gitleaks` + policy engine | Parser/rule diversity plus policy enforceability |
| Release gate with computed values | Above stack + plan JSON checks (`checkov --framework terraform_plan`, OPA/Sentinel) | Evaluates unknown/computed values and module expansions |
| Runtime posture audit | Above stack + drift path (`terraform plan -refresh-only` + driftctl where permitted) | Captures out-of-band cloud changes and unmanaged assets |

---

## Trivy

Trivy is Aqua Security's unified scanner that absorbed tfsec in 2023-2024. It scans Terraform HCL, plan JSON, CloudFormation, Kubernetes manifests, Dockerfiles, and more.

### Installation

```bash
# macOS
brew install trivy

# Linux (apt)
sudo apt-get install -y trivy

# Docker
docker pull aquasec/trivy
```

### Basic Usage

```bash
# Scan a Terraform directory (replaces `tfsec .`)
trivy config .

# Scan with specific severity threshold
trivy config --severity HIGH,CRITICAL .

# Scan a Terraform plan JSON
terraform plan -out=tfplan.binary
terraform show -json tfplan.binary > tfplan.json
trivy config tfplan.json

# Output as SARIF for GitHub Security tab
trivy config --format sarif --output results.sarif .

# Output as JSON
trivy config --format json --output results.json .

# Ignore specific checks
trivy config --skip-dirs modules/legacy --ignorefile .trivyignore .
```

### .trivyignore File

```
# Ignore by Aqua Vulnerability Database ID
AVD-AWS-0086
AVD-AWS-0107

# Ignore by file path (inline)
# In HCL files, use: #trivy:ignore:AVD-AWS-0086
```

### Inline Ignores in HCL

```hcl
resource "aws_s3_bucket" "example" {
  #trivy:ignore:AVD-AWS-0086 This bucket intentionally has no logging
  bucket = "my-public-assets"
}
```

### Custom Rules with Rego

Trivy supports custom Rego policies:

```bash
# Create a policy directory
mkdir -p policies/

# Run with custom policies
trivy config --config-policy policies/ --policy-namespaces users .
```

Example custom Rego rule (`policies/required_tags.rego`):

```rego
# METADATA
# title: All resources must have required tags
# description: Ensure Owner and Environment tags are present
# custom:
#   severity: HIGH
#   input:
#     selector:
#       - type: cloud
#         subtypes:
#           - provider: aws

package users.terraform.required_tags

import rego.v1

deny contains msg if {
    resource := input.resource[type][name]
    required := {"Owner", "Environment"}
    provided := {tag | resource.tags[tag]}
    missing := required - provided
    count(missing) > 0
    msg := sprintf("%s.%s is missing required tags: %v", [type, name, missing])
}
```

### OpenTofu Compatibility

Trivy scans OpenTofu configurations identically to Terraform — same HCL parser, same check IDs. No configuration changes needed.

---

## Checkov

Checkov by Bridgecrew (Prisma Cloud) is a policy-rich open-source IaC scanner with 1,000+ built-in checks. It uses graph-based analysis to understand resource relationships (e.g., a security group attached to an EC2 instance).

### Installation

```bash
pip install checkov
# or
brew install checkov
```

### Basic Usage

```bash
# Scan current directory
checkov -d .

# Scan specific file
checkov -f main.tf

# Scan Terraform plan JSON (catches post-interpolation issues)
terraform plan -out=tfplan.binary
terraform show -json tfplan.binary > tfplan.json
checkov -f tfplan.json --framework terraform_plan

# Output as SARIF
checkov -d . -o sarif --output-file-path results/

# Output as JUnit XML (for CI test reporters)
checkov -d . -o junitxml --output-file-path results/

# Multiple output formats simultaneously
checkov -d . -o cli -o sarif -o json --output-file-path console,results/,results/

# Skip specific checks
checkov -d . --skip-check CKV_AWS_18,CKV_AWS_21

# Run only specific checks
checkov -d . --check CKV_AWS_18,CKV_AWS_21

# Filter by severity
checkov -d . --check-severity HIGH,CRITICAL
```

### Custom Policies in YAML

```yaml
# policies/require_encryption.yaml
metadata:
  id: "CUSTOM_AWS_001"
  name: "Ensure RDS instances are encrypted"
  severity: HIGH
  category: "ENCRYPTION"
definition:
  cond_type: "attribute"
  resource_types:
    - "aws_db_instance"
  attribute: "storage_encrypted"
  operator: "equals"
  value: "true"
```

### Custom Policies in Python

```python
# policies/check_s3_versioning.py
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories

class S3Versioning(BaseResourceCheck):
    def __init__(self):
        name = "Ensure S3 bucket has versioning enabled"
        id = "CUSTOM_AWS_002"
        supported_resources = ["aws_s3_bucket"]
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id,
                         categories=categories,
                         supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        versioning = conf.get("versioning", [{}])
        if isinstance(versioning, list):
            versioning = versioning[0]
        if versioning.get("enabled", [False]) == [True]:
            return CheckResult.PASSED
        return CheckResult.FAILED

check = S3Versioning()
```

Load custom policies with `--external-checks-dir policies/`.

### .checkov.yaml Config File

```yaml
# .checkov.yaml in repo root
directory:
  - "."
skip-check:
  - CKV_AWS_18   # S3 logging — handled by org-level config
  - CKV_AWS_144  # Cross-region replication — not needed for dev
framework:
  - terraform
  - terraform_plan
output:
  - cli
  - sarif
soft-fail-on:
  - CKV_AWS_79   # Metadata IMDSv2 — warn but don't block
```

### Plan-Time vs Source-Time Scanning

Source-time scanning (`checkov -d .`) catches most issues but cannot resolve:
- Variable interpolations (`var.enable_encryption`)
- Conditional resources (`count` or `for_each` based on variables)
- Module outputs used as inputs

Plan-time scanning (`checkov -f tfplan.json --framework terraform_plan`) resolves all variables and shows the actual resources that will be created. Use both for defense-in-depth.

---

## Terrascan (ARCHIVED)

> **Terrascan was archived by Tenable in November 2025.** The GitHub repository is read-only — no new features, bug fixes, or security patches. Migrate to Checkov, KICS, or Trivy. Existing Terrascan Rego policies can often be adapted for Conftest or Trivy's custom Rego policy support.

---

## KICS

KICS (Keeping Infrastructure as Code Secure) by Checkmarx is an open-source scanner with 2,400+ built-in queries covering Terraform, CloudFormation, Ansible, Kubernetes, Pulumi, and more.

### Installation

```bash
# Docker (recommended)
docker pull checkmarx/kics

# Binary release
curl -sfL https://raw.githubusercontent.com/Checkmarx/kics/master/install.sh | bash
```

### Basic Usage

```bash
# Scan directory
kics scan -p /path/to/terraform/

# Scan with severity filter
kics scan -p . --fail-on high,critical

# Output as SARIF
kics scan -p . -o results/ --report-formats "sarif"

# Output multiple formats
kics scan -p . -o results/ --report-formats "json,sarif,html"

# Exclude specific queries
kics scan -p . --exclude-queries "Query-ID-1,Query-ID-2"

# Scan with custom queries directory
kics scan -p . -q /path/to/custom-queries/
```

### Strengths

- Broad IaC format support (Terraform, CloudFormation, Ansible, K8s, Docker, Pulumi)
- CWE mapping on every finding — useful for security dashboards
- Built-in remediation suggestions in output
- Supports `.kics.config` for persistent configuration

---

## TFLint

TFLint is a pluggable linter focused on Terraform-specific correctness rather than pure security. It catches invalid instance types, deprecated syntax, naming convention violations, and provider-specific issues that security scanners miss.

### Installation

```bash
brew install tflint
# or
curl -s https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh | bash
```

### Configuration (.tflint.hcl)

```hcl
# .tflint.hcl
plugin "aws" {
  enabled = true
  version = "0.32.0"
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
}

plugin "azurerm" {
  enabled = true
  version = "0.26.0"
  source  = "github.com/terraform-linters/tflint-ruleset-azurerm"
}

plugin "google" {
  enabled = true
  version = "0.29.0"
  source  = "github.com/terraform-linters/tflint-ruleset-google"
}

rule "terraform_naming_convention" {
  enabled = true
  format  = "snake_case"
}

rule "terraform_documented_variables" {
  enabled = true
}

rule "terraform_documented_outputs" {
  enabled = true
}

rule "terraform_unused_declarations" {
  enabled = true
}

rule "terraform_required_version" {
  enabled = true
}

rule "terraform_required_providers" {
  enabled = true
}
```

### Usage

```bash
# Initialize plugins
tflint --init

# Lint current directory
tflint

# Lint with specific config
tflint --config .tflint.hcl

# Output as SARIF
tflint --format sarif

# Output as JSON
tflint --format json

# Recursive scan of all modules
tflint --recursive
```

### OpenTofu Compatibility

TFLint has limited OpenTofu support. It parses standard HCL but may not recognize OpenTofu-specific features like `encryption` blocks. For OpenTofu projects, combine TFLint for linting with `tofu validate` for syntax validation.

---

## Infracost

Infracost is not a security tool per se, but it prevents cost-based security issues (e.g., someone deploying 100 `p4d.24xlarge` instances) and helps detect risky infrastructure deltas such as sudden spend spikes from unexpected internet-facing or oversized resources.

### Installation

```bash
brew install infracost
infracost auth login  # free API key required
```

### Usage in Security Context

```bash
# Generate cost breakdown
infracost breakdown --path .

# Compare costs against baseline (PR comments)
infracost diff --path . --compare-to infracost-base.json

# Generate JSON for CI gating
infracost breakdown --path . --format json --out-file results/infracost.json
infracost diff --path . --compare-to base.json --format json --out-file results/infracost-diff.json
```

### Gate Pattern

- Fail on percentage and absolute increase thresholds for sensitive environments.
- Require security review label when cost delta implies broader attack surface growth.
- Use as a complementary gate alongside security scanners — not a replacement.

---

## Tool Comparison Matrix

| Feature | Trivy | Checkov | KICS | TFLint |
|---------|-------|---------|------|--------|
| Built-in rules | 1,000+ | 1,000+ | 2,400+ | Provider-specific |
| Plan JSON scanning | Yes | Yes | No | No |
| Custom policies | Rego | Python/YAML | Rego | Go plugins |
| SARIF output | Yes | Yes | Yes | Yes |
| Graph-based analysis | No | Yes | No | No |
| CIS benchmarks | Yes | Yes | Yes | No |
| Speed (large repos) | Fast | Moderate | Moderate | Very fast |
| OpenTofu support | Full | Full | Full | Partial |
| Container scanning | Yes | Yes | No | No |
| Secrets detection | Yes | Yes | No | No |
| IaC SBOM (CycloneDX) | Yes | Yes | No | No |

### Recommended Combinations

**Minimal setup**: Trivy (covers security) + TFLint (covers correctness)

**Comprehensive setup**: Checkov (deepest policy coverage + graph analysis) + TFLint (linting) + Trivy (secondary scanner for defense-in-depth)

**Compliance-heavy**: Checkov (pre-mapped to CIS/SOC2/PCI + custom org policies) + KICS (broad query library with CWE mapping) + TFLint

---

## tfsec-to-Trivy Migration

If a repository already uses `tfsec`, keep it temporarily to avoid abrupt rule drift, then migrate gates to Trivy in a controlled rollout:

```bash
# Run both for one release window, compare findings
tfsec --format sarif --out results/tfsec.sarif .
trivy config --format sarif --output results/trivy.sarif .
```

Compare normalized control IDs between outputs, then retire `tfsec` once parity is acceptable. All tfsec check IDs work unchanged in Trivy.

---

## Finding Normalization

When running multiple scanners, use one canonical finding key to collapse duplicates before gating:

`<cloud-account>/<workspace>/<resource-address>/<normalized-rule>/<severity>`

Normalization tips:
- **resource-address**: prefer Terraform address from plan (`module.x.aws_s3_bucket.y`) over raw file line.
- **normalized-rule**: map vendor IDs (`CKV_AWS_20`, `AVD-AWS-0089`, `KICS-uuid`) to one control ID catalog.
- **severity harmonization**: convert to `critical/high/medium/low/info` only once in aggregator logic.
- If two tools disagree on severity, keep the higher severity and preserve both evidences.

---

## SARIF Strategy

- Treat SARIF as transport, not truth; keep raw JSON outputs for reprocessing.
- Emit one SARIF file per tool, then optionally merge for upload.
- Preserve scanner-specific metadata in SARIF `properties` so triage can trace provenance.
- For tools without strong SARIF emitters (e.g., TruffleHog, Terrascan), publish native JSON alongside SARIF so nothing is lost.
- Use distinct `category` per tool when uploading to GitHub Code Scanning to avoid overwriting results.

---

## Operational Controls

- Run at least one parser-diverse pair (`checkov` + `trivy` or `checkov` + `kics`) to reduce single-parser blind spots.
- Keep scanner versions pinned in CI images; rule drift can silently flip pass/fail outcomes.
- Build suppressions as expiring exceptions (`expires_on`, owner, ticket) rather than permanent ignores.
- Tie suppressions to normalized control IDs, not vendor-specific rule IDs, so tool swaps do not reset governance history.
