# Cycle 070: Team Validation and Bug Fixing Cycle

## Purpose

Allow the team to manually test the work done in the current phase and fix any bugs found.

## Actions

### Validation

1. Provide instructions on how to manually test the work
2. Create verification artifacts appropriate to the project type:
   - **REST APIs**: an HTTP collection — Postman, Bruno, or a `.http` file — following whatever the project already uses, organized by functionality
   - **CLI tools**: Example commands with expected output
   - **Libraries**: Usage examples or a demo script
   - **Frontend**: Steps to exercise new UI flows
3. Reload the current phase from `PLAN.md` and check off every completed task

### Bug Fixing (if bugs were found)

4. Fix each reported bug in **PatchMode** (`references/patch-mode.md`): reproduce it with a failing test, fix until it passes, harden the diff. A bug found in validation gets the same rigor as the code that produced it — not less. Skip PatchMode's commit step; cycle 100 commits the phase
5. Follow the team's lead on fixing bugs only — no refactoring, no new features
6. Put each reported bug on the work list (task list if the harness has one, otherwise its failing test from PatchMode is the item) and mark it done as it is fixed
7. If the team agrees to skip fixing any of the reported bugs, add them as coding tasks in the main `PLAN.md` for that phase
8. **Capture aha moments:** If any bug required significant trial-and-error to diagnose (misleading symptoms, non-obvious root cause, environment-specific gotchas), create or update a `CLAUDE.md` file in the directory closest to the bug. Keep it short — what the symptom was, why it was misleading, and the actual fix

## Completion

Proceed only when the team confirms validation is complete, with or without bugs. Mark this cycle as complete in your task list and move on to README Update Cycle (080).
