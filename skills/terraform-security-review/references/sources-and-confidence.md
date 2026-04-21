# Sources and Confidence Notes

This file records supporting sources for major claims and highlights areas that require environment-specific validation.

## Primary Sources

- tfsec migration guidance to Trivy: https://aquasecurity.github.io/tfsec/latest/guides/migrating-to-trivy/
- Trivy Terraform misconfiguration tutorial: https://trivy.dev/latest/tutorials/misconfiguration/terraform/
- Checkov Terraform scan examples: https://www.checkov.io/7.Scan%20Examples/Terraform.html
- Checkov GitHub Actions integration docs: https://www.checkov.io/4.Integrations/GitHub%20Actions.html
- Terrascan archived (Nov 2025): https://github.com/tenable/terrascan
- KICS command/output docs: https://docs.kics.io/1.5.9/commands/
- TFLint docs site: https://terraform-linters.github.io/tflint/
- Infracost CI/CD integration docs: https://www.infracost.io/docs/integrations/cicd/
- Infracost release stream (for OpenTofu support checks): https://github.com/infracost/infracost/releases
- driftctl repository README (project status and usage): https://github.com/snyk/driftctl
- Gitleaks repository README (command/report support): https://github.com/gitleaks/gitleaks
- TruffleHog repository README (verified results mode and CLI): https://github.com/trufflesecurity/trufflehog
- OPA policy language docs: https://www.openpolicyagent.org/docs/policy-language/
- Conftest docs: https://www.conftest.dev/
- HashiCorp Sentinel docs: https://developer.hashicorp.com/sentinel/docs
- Terraform provider requirements/version constraints: https://developer.hashicorp.com/terraform/language/providers/requirements
- Terraform dependency lock file docs: https://developer.hashicorp.com/terraform/language/files/dependency-lock
- Terraform sensitive data in state guidance: https://developer.hashicorp.com/terraform/language/state/sensitive-data
- Terraform plan command (`-refresh-only`, `--detailed-exitcode`): https://developer.hashicorp.com/terraform/cli/commands/plan
- Terraform test command: https://developer.hashicorp.com/terraform/cli/commands/test
- Terraform import blocks: https://developer.hashicorp.com/terraform/language/import
- Terraform moved/refactoring guidance: https://developer.hashicorp.com/terraform/language/modules/develop/refactoring
- Terraform Cloud workspace permissions: https://developer.hashicorp.com/terraform/cloud-docs/users-teams-organizations/permissions/workspace
- Terraform Cloud variable management: https://developer.hashicorp.com/terraform/cloud-docs/workspaces/settings/variables
- Terraform Cloud run triggers: https://developer.hashicorp.com/terraform/cloud-docs/workspaces/settings/run-triggers
- AzureRM provider v4 announcement: https://www.hashicorp.com/en/blog/terraform-azurerm-provider-4-0-adds-provider-defined-functions
- AzureRM 4.0 upgrade guide: https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/guides/4.0-upgrade-guide
- GitHub OIDC hardening docs: https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect
- GitLab OIDC ID token auth docs: https://docs.gitlab.com/ci/secrets/id_token_authentication/
- Azure DevOps workload identity federation docs: https://learn.microsoft.com/en-us/azure/devops/pipelines/release/configure-workload-identity
- GitHub SARIF upload docs: https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/uploading-a-sarif-file-to-github
- GitLab SAST report docs: https://docs.gitlab.com/ee/user/application_security/sast/
- Azure DevOps pipeline schema/docs: https://learn.microsoft.com/en-us/azure/devops/pipelines/yaml-schema/

### Added Sources (Enhancement Round)

- Terraform variable validation (v0.13+): https://developer.hashicorp.com/terraform/language/block/variable
- Terraform 1.9 cross-variable validation: https://www.hashicorp.com/en/blog/terraform-1-9-enhances-input-variable-validations
- Terraform preconditions/postconditions (v1.2+): https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle
- Terraform check blocks (v1.5+): https://developer.hashicorp.com/terraform/language/block/check
- OpenTofu custom conditions: https://opentofu.org/docs/language/expressions/custom-conditions/
- OpenTofu checks: https://opentofu.org/docs/language/checks/
- OpenTofu cross-variable validation issue: https://github.com/opentofu/opentofu/issues/2191
- Atlantis GitHub repo: https://github.com/runatlantis/atlantis
- Atlantis custom workflows: https://www.runatlantis.io/docs/custom-workflows
- Atlantis server-side repo config: https://www.runatlantis.io/docs/server-side-repo-config.html
- Atlantis OpenTofu support: https://www.runatlantis.io/blog/2024/integrating-atlantis-with-opentofu
- Terragrunt HCL blocks reference: https://terragrunt.gruntwork.io/docs/reference/hcl/blocks/
- Terragrunt run_cmd function: https://terragrunt.gruntwork.io/docs/reference/built-in-functions/
- Terragrunt OpenTofu support: https://www.gruntwork.io/blog/terragrunt-opentofu-better-together
- Terragrunt version compatibility: https://terragrunt.gruntwork.io/docs/reference/supported-versions/
- Renovate Terraform manager: https://docs.renovatebot.com/modules/manager/terraform/
- Dependabot Terraform ecosystem: https://docs.github.com/en/code-security/dependabot/ecosystems-supported-by-dependabot/supported-ecosystems-and-repositories
- Dependabot OpenTofu support (Dec 2025): https://github.blog/changelog/2025-12-16-dependabot-version-updates-now-support-opentofu/
- GitHub OIDC subject claims: https://docs.github.com/actions/reference/openid-connect-reference
- AWS OIDC trust policy guidance: https://aws.amazon.com/blogs/security/use-iam-roles-to-connect-github-actions-to-actions-in-aws/
- Wiz OIDC misconfiguration research: https://www.wiz.io/blog/avoiding-mistakes-with-aws-oidc-integration-conditions
- GitLab OIDC cloud services: https://docs.gitlab.com/ci/cloud_services/
- Azure DevOps WIF: https://devblogs.microsoft.com/devops/introduction-to-azure-devops-workload-identity-federation-oidc-with-terraform/
- Azure Flexible Federated Identity Credentials: https://learn.microsoft.com/en-us/entra/workload-id/workload-identities-flexible-federated-identity-credentials
- GCP Workload Identity Federation: https://docs.cloud.google.com/iam/docs/workload-identity-federation
- Checkov SBOM CycloneDX: https://docs.bridgecrew.io/docs/sbom-generation
- terraform-docs: https://terraform-docs.io/

## Confidence Notes

**High confidence:**
- Scanner role mapping, Terraform plan-based policy patterns, provider pinning/lockfile guidance, `terraform test` integration, and state-sensitivity controls.
- Terrascan archived status (confirmed from GitHub repo).
- Variable validation (v0.13+), preconditions/postconditions (v1.2+), check blocks (v1.5+) — versions and syntax confirmed from HashiCorp docs.
- OIDC subject claim formats for GitHub/GitLab/Azure DevOps and cloud trust policy patterns — confirmed from official docs and security research (Wiz, Datadog).
- Atlantis v0.40.0 status, OpenTofu support (v0.33.0+), custom workflow `run` step mechanics — confirmed from runatlantis.io docs and GitHub releases.
- Terragrunt `run_cmd` and `generate` security risks — confirmed from Gruntwork docs.
- Dependabot OpenTofu support (Dec 2025) — confirmed from GitHub changelog.

**Medium confidence:**
- Exact output-format flags for rapidly evolving scanner versions; pin tool versions and run CI smoke tests after upgrades.
- GitLab and Azure DevOps security dashboard ingestion specifics can vary by edition/licensing and enabled features.
- Gitleaks staged-scan subcommand syntax differs across versions; pin and validate CLI behavior in your toolchain image.
- Azure DevOps `AdvancedSecurity-Publish@1` availability is tenant/feature dependent — validate in each organization before making it a required pipeline step.
- driftctl long-term maintenance and provider coverage may change; confirm project health before treating it as mandatory rather than supplemental.
- OpenTofu behavior in third-party cost/scanner tools can change between releases; validate exact support in CI before enforcing hard gates.
- OpenTofu cross-variable validation (TF 1.9 feature) has known compatibility issues — test before relying on it.
- Renovate `.terraform.lock.hcl` constraint normalization has had recurring bugs — verify lock files pass `terraform init` in CI.
- Terragrunt v1.0.0 stable release timing — RC3 as of March 2026, stable expected Q1 2026.
- Azure Flexible Federated Identity Credentials are in preview — behavior may change.
- IaC SBOM standards are still emerging — Checkov CycloneDX is the most practical option today but there is no unified standard.

## Synthesis-Based Claims

These are operational heuristics inferred from combining tool docs and practice — not sourced from a single authority:

- Parser-diverse scanner pairing reduces blind spots compared with single-engine scanning.
- De-duplication via normalized control IDs improves triage quality and trend reporting.
- Delta-based gating is a practical interim strategy for legacy repositories with high security debt.

Treat these as operational heuristics; validate against your incident history and risk model.
