# Cycle 020: Phase Selection and Planning Refinement Cycle

## Purpose

Select the next phase to work on and define the coding *Tasks* needed to implement it. Do NOT start writing code yet.

## Actions

### Step 1: Select Sub-Project (if applicable)

For multi-project repositories:

1. Review `docs/PROJECTS.md`
2. Identify which sub-project to work on
3. Navigate to the sub-project's PLAN.md: `docs/planning/{subproject}/PLAN.md`

Skip this step for single-project repositories.

### Step 2: Select Next Phase

1. Check PLAN.md's size before opening it, and read it whole or grep it selectively according to `references/plan-file-best-practices.md` — it owns the threshold and the extraction commands
2. Identify the next incomplete phase (sequential, lowest to highest)
3. Agree with the team on what phase to work on next

### Step 3: Refine Tasks

1. Create/update coding tasks in PLAN.md file
2. Close completed tasks
3. Close any invalid tasks
4. Create detailed plans in a new `DETAILED_PLAN.md` file under a dedicated `docs/planning/phase_<CURRENT_PHASE>/` folder — start from `assets/DETAILED_PLAN.md`, which already carries the Security pre-review, Tests, and Phase-specific DoD sections — Steps 4 and 5 below fill the first and last; cycle 030 fills Tests
5. Create the folder as needed
6. For each requirement named in this phase's `<!-- Spec: -->` comment, confirm at least one task covers every clause of it. A clause with no task is either added as a task now or deferred to `BACKLOG.md` with a reason — never silently narrowed. Project completion will walk the spec again; the point of doing it here is to catch the gap while the phase is still open. A phase that implements no requirement — scaffolding, tooling — says so in the comment: `<!-- Spec: none — scaffolding -->`. The absence must be a statement, not an omission

### Step 4: Security Pre-Review

Before any code is written, review the plan for security implications. This is a lightweight design-time check — not a code review.

1. **Authentication & authorization boundaries**: Does this phase add or modify endpoints, APIs, or services? If so, identify where auth checks are needed and note them in the task list
2. **Data flow & trust boundaries**: Does data cross trust boundaries (user input → DB, service → service, internal → external)? Note where validation and sanitization are required
3. **Secrets & credentials**: Will this phase introduce, move, or modify secrets, API keys, or connection strings? Plan how they'll be managed (env vars, vault, etc.)
4. **Infrastructure exposure**: Does this phase modify deployment configs, networking, or access controls? Note what needs to be locked down

Document any security-relevant notes directly in the phase tasks or DETAILED_PLAN.md. The goal is to think about security *before* writing code, not to produce a formal security document. If the project has no security surface at all — local, single-user, no network, no secrets, no untrusted input — say so in one line in place of the table, once, and refer back to it in later phases. Cycle 060's always-check list still applies: a local CLI that reads a file path can still have path traversal.

### Step 5: Define Phase-Specific DoD

The generic Phase DoD always applies, but each phase may need additional context-specific verification.

Identify what this phase changes — code only, containers, DB schema, APIs, infrastructure, or configuration — and copy the matching criteria from `references/definition-of-done.md` § Phase-Specific DoD into the `## Phase-specific DoD` section of DETAILED_PLAN.md.

That table is the single source of truth for these criteria; cycle 090 (Finalize Phase) verifies whatever you record here, in addition to the standard checklist. If nothing beyond the standard DoD applies, write `None beyond the standard Phase DoD.` as plain text — not as a checkbox. Cycle 100's check looks for unticked boxes; a box that says "nothing to check" is noise.

## Important

- Focus only on planning, security review, and task definition — no code
- For large PLAN.md files, make targeted edits without loading the whole file — see `references/plan-file-best-practices.md`

## Completion

Mark this cycle as complete in your task list and move on to Test Plan Creation Cycle (030).
