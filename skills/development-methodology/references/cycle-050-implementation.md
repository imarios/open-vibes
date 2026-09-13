# Cycle 050: Implementation Cycle

## Purpose

Implement the stubbed methods and modify any existing methods as needed to make all tests pass.

## Actions

1. Implement the stubbed methods and modify any existing methods as needed
2. Work through the work list (task list if the harness has one, otherwise the open stubs — cycle 030 step 3), marking each item done as it lands
3. **IMPORTANT**: Always search the existing codebase for similar implementations and follow the same design patterns, conventions, and coding styles. Only invent new patterns if nothing similar exists
4. Run tests to verify that code functionality matches expectations set on tests
5. Modify code to match the tests. Do not change a test unless it is clearly incorrect. Deleting a test that asserted a placeholder's contract is not changing a test — it should not have been written (cycle 040, step 6), and it goes the moment the real behavior lands
6. If a test does change here, keep the `## Tests` section of `DETAILED_PLAN.md` up to date
7. Confirm the work list is empty — no open task, no remaining not-implemented stub — and check again for anything missed
8. Before moving on, revisit `PLAN.md` and check off all completed tasks
9. **Capture aha moments:** If any problem required significant trial-and-error to solve (wrong turns, misleading errors, non-obvious configuration), create or update a `CLAUDE.md` file in the directory closest to where the problem occurred. Keep it short — what went wrong, why, and what to do instead. This eliminates future toil for anyone (human or AI) working in that area
10. **Completed phases are never reopened.** If this phase needs a change in code an earlier, completed phase wrote — a token the lexer lacks, a field a model needs — that change is work in *this* phase: a task if it was planned, a `docs/DECISIONS.md` entry if it was discovered. Do not edit the earlier phase's PLAN.md section

## Completion Criteria

The Cycle is complete only when all tests pass.

## Completion

Mark this cycle as complete in your task list and move on to Code Hardening Cycle (060).
