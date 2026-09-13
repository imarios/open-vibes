# Cycle 060: Code Hardening Cycle

## Purpose

Harden the implementation before team validation. This cycle focuses on code quality, iterative refinement, and security — ensuring the code is clean and safe before anyone reviews it.

## Actions

Steps 1 and 2 name slash commands that automate them. The commands are accelerators, not prerequisites — if your agent host doesn't provide them, perform the same review by hand. The requirement is the review, not the tooling.

### Step 1: Simplify

Review the changed code — on a project's first phase that is every file, since there is no earlier commit to diff against — for reuse opportunities, quality issues, and inefficiencies, and fix what you find: duplicated logic that should call an existing helper, dead code, needless indirection, and obvious inefficiencies.

*Automated by*: `/simplify`, a skill bundled with Claude Code.

### Step 2: Hypothesis-Driven Refinement

Perform iterative hypothesis-driven review: form concrete, testable hypotheses about what could be wrong with the change (unhandled edge cases, broken callers, violated state assumptions, integration seams), verify each one by tracing the actual code, fix what is confirmed, and repeat.

*Automated by*: the `/code-refinement-with-hypothesis` slash command, which loops the `/hypothesis` review until a clean pass.

**Requirement**: Run at least **2 consecutive clean cycles** (no issues found) before moving on. If issues are found, fix them and restart the count. There is no cap on total passes and no minimum beyond that — the stop rule is the only rule, and it is the same whether the review runs through a slash command or by hand.

### Step 3: Security Review

Conduct a post-implementation security review. The depth depends on what this phase changed.

#### Always Check (All Phases)

- Injection vulnerabilities (SQL, command, XSS)
- Authentication/authorization bypasses
- Secrets or credentials in code or config
- Unsafe deserialization
- Path traversal

#### If the Phase Modified Infrastructure or Deployment

- **Network exposure**: Are new ports, endpoints, or services exposed? Are they behind auth?
- **IAM/RBAC**: Do new roles or permissions follow least-privilege? Are there overly broad wildcards?
- **Secrets management**: Are secrets injected via environment/vault, not hardcoded in configs, Helm values, or Terraform?
- **TLS/encryption**: Is data in transit encrypted? Are there new HTTP-only endpoints that should be HTTPS?
- **Resource limits**: Do new containers/services have memory/CPU limits? Can a single request exhaust resources?

#### If the Phase Modified Database Schema

- **Migration safety**: Can the migration be rolled back? Does it lock tables for too long on large datasets?
- **Data exposure**: Are new columns/tables properly scoped by tenant? No cross-tenant data leaks?
- **Sensitive data**: Are new fields that store PII, tokens, or secrets encrypted at rest?

#### If the Phase Modified APIs or Service Boundaries

- **Input validation**: Are all new endpoints validating and sanitizing input at the boundary?
- **Rate limiting**: Do new public endpoints have rate limits?
- **Error messages**: Do error responses avoid leaking internal state, stack traces, or schema details?
- **Actor identity propagation**: When service A calls service B on behalf of a user, does B enforce the original user's permissions (not the service account's)?

Focus on exploitable issues that would block a release. Do not flag theoretical or low-severity concerns — note those in BACKLOG.md if they deserve future attention.

## Completion

Mark this cycle as complete in your task list and move on to Team Validation and Bug Fixing Cycle (070).
