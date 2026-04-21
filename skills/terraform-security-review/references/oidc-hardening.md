# OIDC Subject Claim Hardening

Federated identity (OIDC/WIF) eliminates long-lived cloud secrets in CI/CD, but overly permissive trust policies are a critical vulnerability. This reference covers subject claim restrictions for GitHub Actions, GitLab CI, and Azure DevOps across AWS, Azure, and GCP.

## Table of Contents
- [Why This Matters](#why-this-matters)
- [GitHub Actions OIDC](#github-actions-oidc)
- [GitLab CI OIDC](#gitlab-ci-oidc)
- [Azure DevOps WIF](#azure-devops-wif)
- [Cloud Trust Policy Examples](#cloud-trust-policy-examples)
- [Best Practices](#best-practices)

---

## Why This Matters

Without a `sub` condition in the trust policy, **any** GitHub/GitLab user on the platform can assume your IAM role. Wiz and Datadog Security Labs documented this vulnerability widely in production environments. AWS has since **mandated** that trust policies for GitHub's OIDC provider include a `sub` condition.

Common mistakes:
- Checking only `aud` (audience) without `sub` — allows any repo to authenticate
- Using overly broad wildcards like `repo:my-org/*:*` — any repo in the org on any branch gains access
- Using `StringLike` where `StringEquals` suffices — widens the blast radius unnecessarily

---

## GitHub Actions OIDC

### Subject Claim Format

The `sub` claim varies by trigger context:

| Trigger | Subject format |
|---------|---------------|
| Branch push | `repo:OWNER/REPO:ref:refs/heads/BRANCH` |
| Tag | `repo:OWNER/REPO:ref:refs/tags/TAG` |
| Environment | `repo:OWNER/REPO:environment:ENV_NAME` |
| Pull request | `repo:OWNER/REPO:pull_request` |

### Available OIDC Token Claims

`sub`, `repository`, `repository_id`, `repository_owner`, `repository_owner_id`, `ref`, `ref_type`, `environment`, `workflow`, `job_workflow_ref`, `workflow_ref`, `workflow_sha`, `actor`, `actor_id`, `run_id`, `run_number`, `run_attempt`, `event_name`, `repository_visibility`.

### AWS Trust Policy (Restrictive)

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::111111111111:oidc-provider/token.actions.githubusercontent.com"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
        "token.actions.githubusercontent.com:sub": "repo:my-org/my-repo:ref:refs/heads/main"
      }
    }
  }]
}
```

### Azure Federated Identity Credential

- **Issuer:** `https://token.actions.githubusercontent.com`
- **Subject identifier:** `repo:my-org/my-repo:ref:refs/heads/main`
- **Audience:** `api://AzureADTokenExchange`

Azure now supports Flexible Federated Identity Credentials (preview) with pattern matching:
`claims['sub'] matches 'repo:my-org/my-repo:ref:refs/heads/*'`

### GCP Workload Identity Pool

Attribute condition using CEL:

```
assertion.repository_owner == "my-org" &&
assertion.repository == "my-org/my-repo" &&
assertion.ref == "refs/heads/main" &&
assertion.ref_type == "branch"
```

Minimum attribute mappings:
- `google.subject` = `assertion.sub`
- `attribute.repository` = `assertion.repository`
- `attribute.repository_owner` = `assertion.repository_owner`

IAM binding principal:
`principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/attribute.repository/my-org/my-repo`

---

## GitLab CI OIDC

### Subject Claim Format

`project_path:{group}/{project}:ref_type:{type}:ref:{branch_or_tag}`

Example: `project_path:mygroup/myproject:ref_type:branch:ref:main`

### Available Claims

`sub`, `namespace_path`, `project_path`, `ref_type`, `ref`, `pipeline_id`, `job_id`, `iss`, `aud`.

### AWS Trust Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/gitlab.example.com"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "gitlab.example.com:sub": "project_path:mygroup/myproject:ref_type:branch:ref:main"
      }
    }
  }]
}
```

For group-level access, use `StringLike` with `project_path:mygroup/*` — but understand this grants access to all projects in the group.

---

## Azure DevOps WIF

### How It Works

Azure DevOps uses workload identity federation scoped via **service connections**. The subject identifier inherently restricts to a specific org, project, and connection.

- **Subject identifier:** `sc://<organisation-name>/<project-name>/<service-connection-name>`
- **Issuer:** `https://vstoken.dev.azure.com/<organisation-guid>`
- **Audience:** `api://AzureADTokenExchange`

Only pipelines using that specific service connection in that specific project can authenticate. This is more restrictive by design than GitHub/GitLab OIDC.

---

## Cloud Trust Policy Examples

### AWS — Restrict to Repo + Branch

```json
"Condition": {
  "StringEquals": {
    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
    "token.actions.githubusercontent.com:sub": "repo:my-org/infra:ref:refs/heads/main"
  }
}
```

### AWS — Restrict to Environment (Recommended for Production)

```json
"Condition": {
  "StringEquals": {
    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
    "token.actions.githubusercontent.com:sub": "repo:my-org/infra:environment:production"
  }
}
```

### GCP — Attribute Condition

```
assertion.repository == "my-org/infra" &&
assertion.ref == "refs/heads/main"
```

For GCP, **always** set an `attribute_condition` on the workload identity pool provider — never leave it empty.

---

## Best Practices

### Minimum Viable Restriction

At a bare minimum, restrict to `organization + repository + branch` (or `project_path + ref_type + ref` for GitLab). Never deploy a trust policy that only checks `aud` without also checking `sub`.

### Recommendations

- **Prefer `StringEquals`** over `StringLike` for production roles — eliminates wildcard risks
- **Pin to specific branches** (`main`, `release/*`) for roles with write access to production resources
- **Use environments** in GitHub Actions — the `sub` claim includes the environment name, enabling environment-level restrictions and requiring approvals
- **Layer conditions** using additional claims (`repository_id`, `job_workflow_ref`) for defense in depth
- **Separate read and write roles** — `terraform plan` needs read-only access; only `terraform apply` needs write. Use different OIDC-scoped roles for each
- **Audit regularly** — use Checkov or Wiz to detect overly permissive OIDC trust policies in your AWS/Azure/GCP accounts

### Review Checklist for OIDC Trust Policies

- [ ] `sub` claim is restricted (not just `aud`)
- [ ] `StringEquals` used instead of `StringLike` for production roles
- [ ] Branch restriction present for write-access roles
- [ ] No `repo:org/*:*` broad wildcards
- [ ] Separate roles for plan (read-only) vs apply (write)
- [ ] GCP attribute_condition is non-empty
