# Cycle 040: Test Creation Cycle

## Purpose

This methodology uses Test Driven Development (TDD): every test written in this Cycle fails now, because the behavior it checks does not exist yet. The next Cycle implements the code and turns the reds green, one at a time.

## Actions

1. **First — research existing tests** (skip only if this is the very first test in the project):
   - Search the codebase for existing test files and study their patterns (fixtures, helpers, naming conventions, directory structure)
   - Find tests for similar functionality and use them as a starting point — do not reinvent the wheel
   - Note any shared test utilities, factories, or base classes that should be reused
2. Write the tests from the `## Tests` section of `DETAILED_PLAN.md`, following the patterns discovered above. The `### Manual verification` list, if there is one, has no tests to write — cycle 090 performs it
3. The work list (task list if the harness has one, otherwise the open stubs — cycle 030 step 3) holds every unit of work — stubs, empty data, behavior changes. Each one needs at least one test
4. **Unit tests must never access real infrastructure.** Unit tests must not connect to a database, call a live REST API endpoint, or contact a live MCP server. Use mocks, fakes, or stubs instead. Tests that require live services are *integration tests* and must be marked accordingly (see step 7)
5. Run all newly created tests. **Every one must fail**, and for each you must be able to name the missing behavior that makes it fail. A test that passes against a stub is a bug in the test — it checks nothing, or the stub accidentally satisfies it. Fix the test before moving on
6. Two things that look like tests and are not:
   - **A Task with no red state** — pure wiring, such as an argument parser accepting a subcommand — is not a Task with behavior of its own. Fold it into the Task that gives it behavior and test it there. Do not fake a failure to satisfy step 5
   - **A test that a placeholder is a placeholder** — asserting that a stub raises not-implemented — is green by construction, tests scaffolding, and will be deleted the moment the real behavior lands. Never write one
7. Mark integration tests (anything requiring a live service) and async tests using the conventions of your test framework. Follow the applicable language-specific skill (e.g., python-coding, frontend-coding) for marker and annotation details

## Completion Criteria

This cycle is done when *ALL* tests are created.

## Completion

Mark this cycle as complete in your task list and move on to Implementation Cycle (050).
