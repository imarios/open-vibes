---
name: terraform-security-review
version: 0.1.0
description: >-
  End-to-end Terraform and OpenTofu security review with static analysis,
  policy-as-code, secrets scanning, drift detection, and CI/CD gates. Use when
  hardening IaC, writing OPA/Rego or Sentinel policies, or setting up
  Trivy/Checkov PR pipelines.
---

# Terraform Security Review

Guides security reviews of Terraform and OpenTofu infrastructure-as-code across the full lifecycle: authoring, commit, CI/CD, plan-time, and runtime drift detection.

## Reference Loading Guide

| Reference | Read when | Consult for |
|-----------|-----------|-------------|
| `references/static-analysis-tools.md` | Choosing or configuring scanners | Trivy, Checkov, KICS, TFLint, Infracost setup; comparison matrix; finding normalization |
| `references/workflow-and-gates.md` | Designing gate strategy or pre-commit setup | Pre-commit hooks, PR gate logic, plan-time flow, secret incident response, exception management |
| `references/ci-cd-integration.md` | Building platform-specific pipelines | GitHub Actions, GitLab CI, Azure DevOps workflows; OIDC/WIF auth; SARIF upload patterns |
| `references/oidc-hardening.md` | Securing CI/CD cloud credentials | GitHub/GitLab/Azure DevOps OIDC subject claim restrictions; AWS/Azure/GCP trust policies; common misconfigurations |
| `references/policy-as-code.md` | Writing or reviewing custom governance rules | OPA/Rego policies, Conftest, Sentinel, plan-time evaluation, unknown-value handling, policy testing |
| `references/native-validation.md` | Using Terraform's built-in security features | Variable validation, preconditions/postconditions, check blocks; no external tools needed |
| `references/secrets-and-drift.md` | Detecting secrets or infrastructure drift | Gitleaks, TruffleHog, Terraform-specific secret patterns, drift detection, OpenTofu compatibility |
| `references/supply-chain-and-state.md` | Hardening modules, providers, state, or cloud posture | Provider pinning, module verification, lock files, state encryption, cloud-specific controls, dependency automation |
| `references/atlantis-and-terragrunt.md` | Using Atlantis or Terragrunt securely | Atlantis PR automation with security gates; Terragrunt security risks (run_cmd, generate); OpenTofu support |
| `references/sources-and-confidence.md` | Verifying claims or uncertain areas | Source links, evidence notes, and explicitly flagged low-confidence items |

## Decision Path

1. **Classify scope**: `code-only` (HCL source) → static analysis. `plan-aware` (plan JSON) → plan-time scanning with Checkov or OPA/Conftest. `runtime` → drift detection.
2. **Where in workflow?** Developer machine → pre-commit hooks. PR/MR → CI pipeline gates. Post-deploy → scheduled drift checks.
3. **Custom policies needed?** Org-specific rules → OPA/Rego with Conftest or Sentinel. Standard compliance → built-in rulesets from Trivy/Checkov.
4. **Build layered controls**: linter (TFLint) → misconfiguration scanners → secrets scanning → policy-as-code enforcement.
5. **Emit machine-readable outputs** (`sarif`, `json`, `junit`) so findings can be gated, trended, and audited.

## Guardrails

- tfsec is deprecated — use `trivy config .` instead (all tfsec check IDs work in Trivy)
- **Terrascan is archived** (Nov 2025, by Tenable) — migrate to Checkov, KICS, or Trivy
- driftctl is in maintenance mode — consider Driftive for new projects; disclose lifecycle constraints before adoption
- Always scan both HCL source *and* plan JSON — some misconfigurations only surface after variable interpolation
- Never store secrets in Terraform state or variable defaults — use vault references or data sources
- Use short-lived federated CI credentials (OIDC/WIF), not long-lived cloud secrets — always restrict OIDC subject claims to specific repo + branch
- Run at least one parser-diverse scanner pair to reduce single-parser blind spots
- Pin provider and module versions; commit and enforce `.terraform.lock.hcl` in CI
- Use Terraform's native validation (`variable validation`, `precondition`, `postcondition`) as a first layer — free, no tools required
- Automate provider/module updates with Renovate or Dependabot to reduce exposure window
