# Cycle 030: Test Plan Creation Cycle

## Purpose

Stub every function the Phase's Tasks call for, and plan the tests that will drive their implementation.

## Actions

1. For every Task in the Phase, create the thing a test can fail against. Which thing depends on what the Task adds:
   - **A new function or method** → a **stub**: the real signature, a one-line docstring saying what it will do, and a body that raises the language's not-implemented error (`raise NotImplementedError`, `throw new Error("not implemented")`, `todo!()`). No placeholder return values — a stub that returns `None` or `[]` can make a test pass by accident
   - **New data — a table, constant, schema, config key** → declare it empty or leave it absent, so a test that reads it fails on a lookup or import error rather than on a wrong value
   - **A change to behavior that already exists** → nothing to stub. The failing test written in 040 is the placeholder
   - **A plain data type** — a dataclass, record, or struct whose definition *is* its implementation → no stub and no test of its own; it is covered by the tests of the first function that consumes it
2. Stub enough that the codebase compiles and the tests in Cycle 040 can import and call what they test — otherwise they cannot run
3. Put every item from step 1 — stubs, empty data, behavior changes — on the task list, if the harness has one (`TodoWrite`, or `TaskCreate` / `TaskUpdate` / `TaskList`; see `references/overview.md` § Cycle Tracking). If it has none, **the stubs are the list**: `grep -rn NotImplementedError src/` (or the language's equivalent) is the open-items query, empty output is done, and a behavior change with nothing to stub is tracked by its failing test. Either way the list is the contract for the next two cycles — 040 writes a test for each entry, 050 implements each and marks it done — and it never lives in a file. If the session must end mid-phase, write `HANDOFF.md` (start from `assets/HANDOFF.md`) so the next session can rebuild it
4. Write the test plan as the `## Tests` section of `DETAILED_PLAN.md` — the section is already in `assets/DETAILED_PLAN.md`. A short paragraph on what the tests are meant to prove, then the tests to be built, grouped by kind, naming the test file each group lives in
5. Include both *positive and negative* test cases
6. A Task whose verification can only be manual — interactive I/O, hardware, a real terminal — gets a `### Manual verification` list in that section with the exact steps and the expected result, in place of an automated test. This is an exception for that Task, not a category for the Phase: everything else still gets a test. Cycle 090 performs those steps and ticks them — the only ticks this methodology keeps are for checks no machine can observe
7. Do not track "test written" with checkboxes. A test is written when it exists in the test directory; the suite is the record

## Completion

Mark this cycle as complete in your task list and move on to Test Creation Cycle (040).
