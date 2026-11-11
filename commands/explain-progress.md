---
description: Show where this session stands: the goal, the steps toward it, what's done, and what's next, drawn so it can be read at a glance
version: 1.0.0
---

## Your task

The user is switching between several sessions and has lost track of this one. Give them a quick, visual re-orientation: where this work is heading, how far along it is, and what happens next. They should be able to pick the thread back up in under a minute, without scrolling back through the conversation.

If the user named a focus, report progress on only that part: $ARGUMENTS

This is a one-shot command. After this reply, go back to your normal style.

### Step 1: Rebuild the picture from real sources

Work out the goal and the steps from what actually exists. Don't reconstruct them from memory alone. Check, in this order:

1. **A written plan**, if there is one: a plan or spec file (`PLAN.md`, a SPEC section, a design doc), a task or todo list in this session, or a numbered plan you or the user wrote earlier in the conversation. If you find one, use its steps and say where they come from ("the spec, section 3", "PLAN.md phase 2").
2. **The conversation**: what the user asked for, what you agreed to do, and what got done.
3. **The repo**: recent commits, uncommitted changes, and test results, to confirm what is really finished.
4. **Work in flight**: background jobs, running commands, or other sessions that this work is waiting on.

If there is no written plan, infer the steps from the conversation and say so in one line ("No written plan; these steps are reconstructed from our conversation"). Don't present an inferred plan as if it were a formal one.

### Step 2: Classify each step honestly

Give each step exactly one status:

| Mark | Status      | Use when                                                        |
|------|-------------|-----------------------------------------------------------------|
| ✅   | done        | Finished **and** checked (test passes, output seen, committed). |
| 🟡   | done, unchecked | Finished but not verified yet. Say what's missing.          |
| ▶    | in progress | Being worked on now, or running in the background.              |
| ⛔   | blocked     | Can't continue. Say what it's waiting on.                       |
| ○    | to do       | Not started. Mark the very next one as **next**.                |

For each done step, add one short line of **evidence**: a number, a test result, a file, a commit ("p95 latency went from 900ms to 210ms"). For anything not ✅, don't round up. A step that's mostly done is ▶, not ✅.

### Step 3: Draw it

Use this layout, top to bottom:

1. **Right now** (one line, only if something is in flight): what's running and roughly when it will finish.
2. **Goal** (one or two sentences, in plain words): what this work is for, not just what it changes. Say why it matters.
3. **Progress bar** with a count and the plan's source:
   ```
   ███████████░░░░░░░░░░░░░░  3 of 7 steps  (plan: PLAN.md phase 2)
   ```
4. **Step table**: number, step name, status mark, and the evidence or the blocker. Use the plan's own step names and the code's own terms.
5. **What we've learned so far** (2–4 bullets): results that change how we see the problem, both what worked and what didn't. Use real numbers when you have them.
6. **Next** (one or two lines): the very next action, and any decision the user needs to make before it can happen.

How to render it:

- **If you have a tool that renders visuals inline** (an SVG/HTML visualization tool, an artifact viewer), you may use it for the progress bar and the step list, as a vertical track of steps with done ones filled in, the current one highlighted, and future ones faded.
- **Otherwise**, use a markdown table for the steps and a fenced code block for the progress bar. Keep anything in a code block within 80 columns.

### Rules

- **Keep it short.** The whole reply should fit on one screen. This is a status board, not a report. Leave out history the user doesn't need to move forward.
- **Separate facts from guesses.** If you can't tell whether a step was finished (for example, a background job's result never came back), say so instead of guessing.
- **Point out drift.** If the work has moved away from the original goal or plan (steps added, skipped, or reordered), say so in one line, so the user can decide whether that's fine.
- **Don't start new work.** This command only reports. Don't run the next step. Let the user decide.

### Example

```
Right now: the full load test against staging is running (~5 min).

Goal: make the nightly import finish in under an hour, so reports are
ready before the morning shift starts.

███████████░░░░░░░░░░░░░░  3 of 7 steps  (plan: PLAN.md phase 2)
```

| # | Step | Status | Evidence / blocker |
|---|------|--------|--------------------|
| 1 | Add timing to each import stage | ✅ | Per-stage timings in the job log |
| 2 | Batch database writes | ✅ | Committed, tests pass |
| 3 | Parse files in parallel | ✅ | Parse stage: 48 min → 11 min |
| 4 | Cache lookups of reference data | ○ **next** | |
| 5 | Move validation after the load | ○ | |
| 6 | Drop the unused staging tables | ○ | |
| 7 | Full run on production-sized data, compare | ○ | |

**What we've learned so far**
- Parsing in parallel worked: that stage is 4× faster.
- The total is still 2h 10m. Reference-data lookups now take most of the time, which is what step 4 targets.

**Next:** start step 4 once the load test finishes and confirms the parse speedup.
