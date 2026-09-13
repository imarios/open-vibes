# PatchMode: TDD-First Scoped Changes

## Purpose

PatchMode is the lightest-weight workflow in the methodology — for small-to-medium scoped changes (~20–150 lines, 2–6 files) that don't warrant a full phase. It keeps TDD discipline, a brief written plan, and harden steps, but skips spec, PLAN.md, sub-projects, team validation, and retrospectives.

**Below the floor**: trivial non-bug changes (a typo, one config value) don't need PatchMode — just make the change. A bug fix is never below the floor: however small, it gets a failing test that reproduces it before the fix (Step 2). What a one-line bug fix may skip is the scratch file and the harden pass, not the test. PatchMode proper kicks in when the work has enough surface area that you can't hold it all in your head.

## When to Use PatchMode

- Bug fix that needs to be applied in 3–5 places after root-cause analysis
- Small feature touching one module deeply (handler + service + test fixtures)
- Refactor with a clear shape but multiple touchpoints (rename + adjust callers + update tests)
- Dependency upgrade with API surface changes across a few files
- Config or schema change with a targeted test

## When NOT to Use PatchMode (escalate to a full phase)

- New architectural pattern or abstraction
- Touches multiple service boundaries or cross-cutting concerns
- Needs design discussion before implementation
- Database migration with data backfill
- Multiple people need to coordinate on the change
- Scope is genuinely uncertain — "I think it's medium but I'm not sure"

If you start in PatchMode and discover the change is bigger than expected, stop and escalate to a full phase. There is no shame in upgrading — catching scope creep early is exactly what the methodology is for.

## PatchMode Workflow

### Step 1: Scope

Write a single scratch `FIX.md` capturing:
- **Intent** — one paragraph: what changes, why
- **Test list** — bullet list of failing tests to write
- **Affected files** — bullet list

If the test list or the affected-files list won't fit in a handful of bullets, the change is too big — escalate.

Put it somewhere git already ignores — `docs/planning/scratch/FIX.md` with `scratch/` gitignored, or the agent's own scratch directory. It is a thinking aid for this one change, not a project artifact, and it must not end up in a commit.

### Step 2: Test First (TDD Red)

1. Write the failing tests from the test list
2. Run them and confirm they fail for the right reason
3. For bugs: tests should reproduce the exact failure the user reported

### Step 3: Fix (TDD Green)

1. Make the minimal change to turn each test green
2. Run the full test suite after each meaningful change
3. If the change touches containers, DB schema, APIs, infrastructure, or configuration, apply the matching verification from `references/definition-of-done.md` § Phase-Specific DoD — it owns those criteria

### Step 4: Harden

1. Simplify the diff — fix reuse opportunities, dead code, and inefficiencies (`/simplify` automates this)
2. Hypothesis-driven review to 1 clean cycle — fix any issues found (`/code-refinement-with-hypothesis` automates this)
3. P0 security scan on the changed code: injection, auth bypass, secrets

The slash commands are accelerators. Without them, do the same two reviews by hand — see `references/cycle-060-code-hardening.md` for what each one covers.

### Step 5: Commit and Clean

1. Run all unit tests — they must pass
2. Commit with a clear message describing the change
3. Delete `FIX.md` (it was scratch — its job is done)

## Invoking PatchMode

"Use PatchMode to [fix/implement description]."

Or simply describe a scoped change — the agent should recognize when PatchMode is appropriate and suggest it.

## What PatchMode Skips

| Full Methodology | PatchMode |
|------------------|-----------|
| Spec | Skip |
| PLAN.md updates | Skip |
| DETAILED_PLAN.md (plan and tests) | Skip — replaced by intent and test list in `FIX.md` |
| Phase selection (020) | Skip |
| Team validation (070) | Skip |
| README update (080) | Skip — unless user-facing behavior changed |
| Phase retrospective (095) | Skip |
| BACKLOG.md sweep | Skip |
