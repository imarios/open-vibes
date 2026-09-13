---
description: Generate 4 hypotheses about the last change and verify each one by tracing through the code
version: 1.0.1
---

## Context

- Unstaged changes: !`git diff --stat`
- Staged changes: !`git diff --staged --stat`
- Last commit message: !`git log -1 --pretty=format:"%s%n%n%b"`
- Last commit diff (stat): !`git diff HEAD~1 HEAD --stat`
- Files changed in last commit: !`git diff HEAD~1 HEAD --name-only`

## Your task

You are a manual QA tester performing a hypothesis-driven review of the most recent code change.

**Which change to review:** If there are unstaged or staged changes, review those (use `git diff` / `git diff --staged`). Otherwise, review the last commit (use `git diff HEAD~1 HEAD`). For large diffs (>500 lines), focus on the most critical files rather than reading the entire diff.

### Step 1: Formulate 4 hypotheses

Based on the diff and commit message above, formulate **4 hypotheses** about things that could go wrong or need verification. These should be concrete, testable concerns such as:

- Edge cases the change might not handle
- Callers or dependents of modified code that might break
- State or data flow assumptions that might be violated
- Off-by-one errors, missing null checks, or incorrect type handling
- Integration points where the change interacts with other parts of the system

Present all 4 hypotheses to the user in a numbered list before proceeding.

### Step 2: Verify each hypothesis in parallel

Launch **4 subagents in parallel** (one per hypothesis). A fast mid-tier model is a good fit — each subagent does focused tracing, not synthesis. If subagents are unavailable, verify the four hypotheses sequentially yourself. Each subagent should:

1. Read the relevant source files involved in its hypothesis
2. Trace the code path step by step, following function calls, imports, and data flow
3. Check whether the hypothesis holds (the concern is real) or is disproven (the code handles it correctly)
4. Return a clear verdict: **CONFIRMED** (real issue found), **DISPROVEN** (code handles it), or **INCONCLUSIVE** (unable to fully verify)
5. Include the specific file paths and line numbers examined as evidence

### Step 3: Report results

After all subagents complete, present a summary table:

| # | Hypothesis | Verdict | Key evidence |
|---|-----------|---------|-------------|
| 1 | ... | ... | ... |
| 2 | ... | ... | ... |
| 3 | ... | ... | ... |
| 4 | ... | ... | ... |

If any hypothesis is **CONFIRMED**, highlight it and suggest a fix. If all are disproven, state that the change looks solid.
