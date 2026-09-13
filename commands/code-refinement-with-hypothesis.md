---
description: Iteratively run hypothesis-driven reviews and fix issues until the code is clean
version: 1.0.1
dependencies:
  - hypothesis
---

You will run a loop of hypothesis-driven code reviews, fixing issues each round, until a clean pass is achieved.

**Process:**

1. **Start the loop**
   Use `/loop 1m /hypothesis` to run the hypothesis command on a recurring 1-minute interval. (`/loop` is a skill bundled with Claude Code; without it, just re-run `/hypothesis` manually each round.) Only one hypothesis review should be running at a time — wait for the current one to complete before the next iteration begins.

2. **After each hypothesis run completes, act on the results**
   - For each **CONFIRMED** issue: fix it immediately, unless it is a major architectural change (see below).
   - For **INCONCLUSIVE** verdicts: use your judgement — fix if the concern is legitimate and the fix is safe, otherwise note it.
   - For **DISPROVEN** verdicts: no action needed.

3. **Handle major architectural issues separately**
   - Do NOT attempt to fix issues that require major architectural changes (e.g., rethinking data models, changing module boundaries, rewriting core abstractions).
   - Instead, collect these in a running list to report at the end.

4. **Stop condition**
   - After a hypothesis run where **all 4 hypotheses are DISPROVEN** (no confirmed or inconclusive issues), stop the loop.
   - This means the recent changes have survived a full round of scrutiny with no issues found.

5. **Final report**
   When the loop stops, present a summary:

   ```
   ## Code Refinement Complete

   **Rounds:** [number of hypothesis rounds run]
   **Issues fixed:** [count]

   ### Fixes Applied
   - [round #] [file:line] [brief description of fix]

   ### Architectural Concerns (not fixed)
   - [description] — [why this needs broader discussion]

   ### Result
   All hypotheses disproven in final round. Code looks solid.
   ```

**Important:**
- Only one hypothesis review runs at a time. Wait for completion before starting the next.
- Keep fixes minimal and targeted — don't refactor surrounding code.
- If a fix introduces new changes, the next hypothesis round will naturally cover them.
- If the loop has not converged after 5 rounds, stop and report — the remaining issues likely need human judgement.
