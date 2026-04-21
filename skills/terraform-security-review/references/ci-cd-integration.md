# CI/CD Integration Patterns

## Table of Contents
- [Shared Conventions](#shared-conventions)
- [OIDC/WIF Authentication](#oidcwif-authentication)
- [GitHub Actions](#github-actions)
- [GitLab CI](#gitlab-ci)
- [Azure DevOps Pipelines](#azure-devops-pipelines)
- [SARIF Upload Patterns](#sarif-upload-patterns)
- [Dashboard Architecture](#dashboard-architecture)

---

## Shared Conventions

- Write scanner outputs to `results/`.
- Keep one file per tool (`trivy.sarif`, `checkov.sarif`, `kics.sarif`, `gitleaks.sarif`, `trufflehog.json`, `infracost.json`).
- Upload raw artifacts even when jobs fail (`if: always()` / `when: always`) for forensic triage.
- Gate on policy and severity after collection so all findings are visible in one run.
- For gate execution order and severity thresholds, see `workflow-and-gates.md` § PR Gate Strategy.

---

## OIDC/WIF Authentication

Use short-lived federated identity for any stage that runs `terraform plan`, drift checks, or cloud API reads. Avoid long-lived cloud secrets in CI variables.

### AWS

```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789012:role/gha-terraform-plan-readonly
    aws-region: us-east-1
```

### Azure

```yaml
- uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

### GCP

```yaml
- uses: google-github-actions/auth@v3
  with:
    workload_identity_provider: projects/123456/locations/global/workloadIdentityPools/pool/providers/provider
    service_account: terraform-plan@project-id.iam.gserviceaccount.com
```

### Platform Notes

- **GitHub Actions**: set `permissions: id-token: write`, then exchange OIDC token for cloud credentials.
- **GitLab CI**: configure `id_tokens` and use web identity federation in cloud STS/IAM.
- **Azure DevOps**: use workload identity federation service connections; avoid static client secrets in variable groups.

**Critical:** Always restrict OIDC subject claims to specific repos and branches in your cloud trust policies. Overly permissive trust policies allow any repo to assume your IAM roles. See `oidc-hardening.md` for trust policy examples, subject claim formats, and a review checklist.

---

## GitHub Actions

### Comprehensive Security Scanning Workflow

```yaml
# .github/workflows/terraform-security.yml
name: Terraform Security Review
on:
  pull_request:
    paths:
      - '**.tf'
      - '**.tfvars'
      - '.terraform.lock.hcl'

permissions:
  contents: read
  pull-requests: write
  security-events: write  # Required for SARIF upload
  id-token: write         # Required for OIDC

jobs:
  # Job 1: Linting (fast, catches syntax and correctness issues)
  tflint:
    name: TFLint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: terraform-linters/setup-tflint@v6
        with:
          tflint_version: latest

      - run: tflint --init
      - run: tflint --recursive --format sarif > tflint-results.sarif
        continue-on-error: true

      - uses: github/codeql-action/upload-sarif@v4
        with:
          sarif_file: tflint-results.sarif
          category: tflint

  # Job 2: Trivy security scan
  trivy:
    name: Trivy Config Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy scanner
        uses: aquasecurity/trivy-action@0.35.0
        with:
          scan-type: 'config'
          scan-ref: '.'
          severity: 'HIGH,CRITICAL'
          format: 'sarif'
          output: 'trivy-results.sarif'
          exit-code: '1'

      - uses: github/codeql-action/upload-sarif@v4
        if: always()
        with:
          sarif_file: trivy-results.sarif
          category: trivy

  # Job 3: Checkov deep analysis
  checkov:
    name: Checkov
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Checkov
        uses: bridgecrewio/checkov-action@v12
        with:
          directory: .
          framework: terraform
          output_format: cli,sarif
          output_file_path: console,checkov-results.sarif
          soft_fail: false
          skip_check: CKV_AWS_18,CKV_AWS_144

      - uses: github/codeql-action/upload-sarif@v4
        if: always()
        with:
          sarif_file: checkov-results.sarif
          category: checkov

  # Job 4: Secrets detection
  secrets:
    name: Secrets Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for secret scanning

      - name: Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  # Job 5: Plan-time scanning
  plan-scan:
    name: Plan-Time Security Scan
    runs-on: ubuntu-latest
    needs: [tflint]
    env:
      TF_VAR_environment: "ci"
    steps:
      - uses: actions/checkout@v4

      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.9.x"
          terraform_wrapper: false  # Required for JSON output

      - name: Terraform Init & Plan
        run: |
          terraform init -backend=false
          terraform plan -out=tfplan.binary
          terraform show -json tfplan.binary > tfplan.json

      - name: Checkov Plan Scan
        run: |
          pip install checkov
          checkov -f tfplan.json \
            --framework terraform_plan \
            -o cli -o sarif \
            --output-file-path console,plan-results.sarif

      - name: OPA Policy Check
        run: |
          conftest test tfplan.json \
            --policy policy/ \
            --all-namespaces

      - uses: github/codeql-action/upload-sarif@v4
        if: always()
        with:
          sarif_file: plan-results.sarif
          category: checkov-plan

  # Job 6: Cost estimation guardrail
  infracost:
    name: Cost Estimate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: infracost/actions/setup@v3
        with:
          api-key: ${{ secrets.INFRACOST_API_KEY }}

      - name: Generate cost diff
        run: |
          infracost breakdown --path=. --format=json --out-file=/tmp/infracost.json

      - name: Post PR comment
        run: |
          infracost comment github \
            --path=/tmp/infracost.json \
            --repo=${{ github.repository }} \
            --pull-request=${{ github.event.pull_request.number }} \
            --github-token=${{ secrets.GITHUB_TOKEN }} \
            --behavior=update
```

### Minimal GitHub Actions Setup

For smaller projects, a single-job workflow:

```yaml
name: TF Security
on:
  pull_request:
    paths: ['**.tf']

jobs:
  scan:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - uses: aquasecurity/trivy-action@0.35.0
        with:
          scan-type: config
          severity: HIGH,CRITICAL
          format: sarif
          output: results.sarif
          exit-code: '1'
      - uses: github/codeql-action/upload-sarif@v4
        if: always()
        with:
          sarif_file: results.sarif
```

### Severity and Secrets Gate Step

Add this after all scanners have run to enforce a unified gate:

```yaml
- name: Gate on severity and verified secrets
  run: |
    set -euo pipefail
    verified_count="$(jq -s '[.[] | select((.Verified // .verified // false) == true)] | length' results/trufflehog.json)"
    error_level_count="$(jq -s '[.[] | .runs[]?.results[]? | select((.level // "") == "error")] | length' \
      results/trivy.sarif results/checkov.sarif results/gitleaks.sarif)"
    if [ "$verified_count" -gt 0 ] || [ "$error_level_count" -gt 0 ]; then
      echo "Gate failed: verified secrets or error-level SARIF findings detected"
      exit 1
    fi
```

---

## GitLab CI

### .gitlab-ci.yml

```yaml
stages:
  - validate
  - security
  - plan

variables:
  TF_ROOT: ${CI_PROJECT_DIR}
  TF_IN_AUTOMATION: "true"

default:
  id_tokens:
    GITLAB_OIDC_TOKEN:
      aud: https://gitlab.com

# Shared setup
.terraform-base:
  image: hashicorp/terraform:1.9
  before_script:
    - cd ${TF_ROOT}
    - terraform init -lockfile=readonly

# Stage 1: Validation and linting
validate:
  stage: validate
  image: ghcr.io/terraform-linters/tflint:latest
  script:
    - tflint --init
    - tflint --recursive --format json > gl-tflint-report.json
  artifacts:
    reports:
      codequality: gl-tflint-report.json

# Stage 2a: Trivy scan
trivy-scan:
  stage: security
  image:
    name: aquasec/trivy:latest
    entrypoint: [""]
  script:
    - trivy config --severity HIGH,CRITICAL
        --format json --output gl-trivy-report.json
        ${TF_ROOT}
    - trivy config --severity HIGH,CRITICAL
        --exit-code 1
        ${TF_ROOT}
  artifacts:
    reports:
      codequality: gl-trivy-report.json
    when: always

# Stage 2b: Checkov scan
checkov-scan:
  stage: security
  image:
    name: bridgecrew/checkov:latest
    entrypoint: [""]
  script:
    - checkov -d ${TF_ROOT}
        --framework terraform
        -o cli -o gitlab_sast
        --output-file-path console,gl-checkov-report.json
  artifacts:
    reports:
      sast: gl-checkov-report.json

# Stage 2c: Secrets scan
secrets-scan:
  stage: security
  image:
    name: zricethezav/gitleaks:latest
    entrypoint: [""]
  script:
    - gitleaks detect --source=${CI_PROJECT_DIR}
        --report-format json
        --report-path gl-gitleaks-report.json
  artifacts:
    reports:
      secret_detection: gl-gitleaks-report.json
  allow_failure: false

# Stage 2d: KICS scan (optional, parser-diverse backup)
kics-scan:
  stage: security
  image:
    name: checkmarx/kics:latest
    entrypoint: [""]
  script:
    - kics scan -p ${TF_ROOT}
        --report-formats "glsast"
        -o ${CI_PROJECT_DIR}/
  artifacts:
    reports:
      sast: gl-sast-results.json

# Stage 3: Plan-time scan
plan-scan:
  stage: plan
  extends: .terraform-base
  script:
    - terraform plan -out=tfplan.binary
    - terraform show -json tfplan.binary > tfplan.json
    - pip install checkov
    - checkov -f tfplan.json
        --framework terraform_plan
        -o cli -o gitlab_sast
        --output-file-path console,gl-plan-report.json
    - conftest test tfplan.json -p policy/opa --all-namespaces
  artifacts:
    reports:
      sast: gl-plan-report.json
  rules:
    - if: $CI_MERGE_REQUEST_IID
```

### GitLab-Specific Features

- **SAST report format**: Checkov and KICS output GitLab SAST format natively (`-o gitlab_sast` / `--report-formats glsast`)
- **Code Quality**: TFLint and Trivy results can map to GitLab Code Quality widgets
- **Secret Detection**: Gitleaks output maps to GitLab's secret detection report format
- **Merge request widgets**: All report artifacts appear as widgets on the MR page
- **GitLab auth**: Exchange `$GITLAB_OIDC_TOKEN` for cloud credentials using your provider's STS/WIF flow before plan or drift stages

---

## Azure DevOps Pipelines

### azure-pipelines.yml

```yaml
trigger:
  branches:
    include:
      - main
  paths:
    include:
      - '**.tf'

pr:
  branches:
    include:
      - main
  paths:
    include:
      - '**.tf'

pool:
  vmImage: 'ubuntu-latest'

stages:
  - stage: SecurityScan
    displayName: 'Terraform Security Scan'
    jobs:
      - job: StaticAnalysis
        displayName: 'Static Analysis'
        steps:
          # Install tools
          - script: |
              curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
              pip install checkov
            displayName: 'Install Security Tools'

          # Trivy scan
          - script: |
              trivy config --severity HIGH,CRITICAL \
                --format sarif --output $(Build.ArtifactStagingDirectory)/trivy.sarif \
                $(Build.SourcesDirectory)
            displayName: 'Trivy Scan'
            continueOnError: true

          # Checkov scan
          - script: |
              checkov -d $(Build.SourcesDirectory) \
                --framework terraform \
                -o cli -o sarif -o junitxml \
                --output-file-path console,$(Build.ArtifactStagingDirectory)/checkov.sarif,$(Build.ArtifactStagingDirectory)/checkov-junit.xml
            displayName: 'Checkov Scan'
            continueOnError: true

          # Publish test results (shows in Tests tab)
          - task: PublishTestResults@2
            inputs:
              testResultsFormat: 'JUnit'
              testResultsFiles: '**/checkov-junit.xml'
              searchFolder: $(Build.ArtifactStagingDirectory)
            displayName: 'Publish Checkov Results'
            condition: always()

          # Publish SARIF artifacts
          - task: PublishBuildArtifacts@1
            inputs:
              PathtoPublish: $(Build.ArtifactStagingDirectory)
              ArtifactName: 'SecurityResults'
            condition: always()

          # Optional: Advanced Security SARIF ingestion (if enabled in org)
          - task: AdvancedSecurity-Publish@1
            condition: always()
            inputs:
              SarifsInputDirectory: $(Build.ArtifactStagingDirectory)

      - job: PlanScan
        displayName: 'Plan-Time Scan'
        dependsOn: StaticAnalysis
        steps:
          - task: TerraformInstaller@1
            inputs:
              terraformVersion: 'latest'

          - script: |
              terraform init -lockfile=readonly
              terraform plan -out=tfplan.binary
              terraform show -json tfplan.binary > tfplan.json
            displayName: 'Generate Plan'

          - script: |
              pip install checkov
              checkov -f tfplan.json \
                --framework terraform_plan \
                -o junitxml \
                --output-file-path $(Build.ArtifactStagingDirectory)/plan-results.xml
            displayName: 'Scan Plan'

          - script: |
              conftest test tfplan.json -p policy/opa
            displayName: 'OPA Policy Check'

          - task: PublishTestResults@2
            inputs:
              testResultsFormat: 'JUnit'
              testResultsFiles: '**/plan-results.xml'
              searchFolder: $(Build.ArtifactStagingDirectory)
            condition: always()
```

### Azure DevOps Tips

- **SARIF**: Azure DevOps doesn't have native SARIF support like GitHub. Use the "SARIF SAST Scans Tab" extension from the marketplace, or publish as JUnit for the Tests tab. `AdvancedSecurity-Publish@1` availability depends on Azure DevOps feature enablement/licensing.
- **Branch policies**: Configure branch policies to require the SecurityScan stage to pass before merging.
- **Variable groups**: Store skip-check lists and severity thresholds in variable groups for consistency across pipelines.
- **Auth**: Use workload identity federation service connections for `terraform plan` access; avoid storing cloud keys in pipeline variables.

---

## SARIF Upload Patterns

### GitHub Code Scanning

All major tools output SARIF. Upload with `github/codeql-action/upload-sarif@v3`:

```yaml
- uses: github/codeql-action/upload-sarif@v4
  with:
    sarif_file: results.sarif
    category: tool-name  # Groups findings by tool in Security tab
```

Findings appear in **Security → Code scanning alerts** with severity levels, file/line references, and a dismissal workflow for false positives. Use a distinct `category` per tool to avoid overwriting results.

### GitLab Dashboard

Feed the dashboard via `gl-sast-report.json` (using `-o gitlab_sast`); keep SARIF as artifact for external SIEM ingestion.

### Azure DevOps

Always publish artifacts; ingest SARIF to Advanced Security only where the task is available. JUnit output provides the most reliable dashboard integration via the Tests tab.

---

## Dashboard Architecture

| Platform | Primary finding path | Secondary/archive path |
|----------|---------------------|----------------------|
| GitHub | SARIF → Security tab (Code Scanning) | Artifact download for SIEM |
| GitLab | `gitlab_sast` report → MR security widget | SARIF artifacts for external tools |
| Azure DevOps | JUnit → Tests tab | SARIF artifacts; Advanced Security where available |
