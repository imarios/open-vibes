# Development Methodology Overview

This document defines how a coding project is planned and implemented in a systematic way, as a collaboration between the agent and the team.

## Working Relationship

- The agent and the team are coworkers. Think of the humans you work with as "the team", not as "the user"
- The team's success is the agent's success, and the other way around
- The team is smart but not infallible
- The agent is a faster and more thorough reader than any human. If the team appears to have misread something, say so
- Neither side should be afraid to admit when they don't know something or are in over their head
- When either side believes they are right, it is **good** to push back — but cite evidence
- If the team documents a preferred form of address or communication style in `CLAUDE.md`, follow it

## Key Definitions

A project starts with a set of specification (spec) documents that explain **what** is being built. The specs are then used to break the project down into an implementation plan.

Towards this end, a larger project is split into multiple *Phases*. Typically 5-10 depending on the complexity. Very small projects can be done in a single phase whereas larger projects may take 30+ phases.

Example Phases for a toy project (used for demonstration purposes):

- Phase 1: Build project skeleton and git repository. Setup basic automations for linting, versioning, and testing.
- Phase 2: Build and test basic feature X.
- Phase 3: Build and test basic feature Y.
- Phase 4: Build and test basic feature Z that depends on feature X and Y.
- Phase 5: End-to-end testing for X, Y, Z automation.

Every Phase is made up of multiple smaller *Tasks*. For example, building feature X requires creating and testing N functions, each of which can be its own *Task*.

A Task names the file or module it touches, the behavior it adds or changes, and how that behavior is verified. If you can't write its test from the bullet alone, the Task is under-specified; if writing it needs more than one sitting, it's a Phase that hasn't been split yet.

```
Good:   `src/core/manifest.ts`: add `parsePacksSection`; reject nested `pack:` members at parse time. (R1, R11)
Vague:  Add queue monitoring and health checks            ← two features, no file, no way to know when it's done
Too big: Migrate `api/orders.py` (18 endpoints)            ← eighteen Tasks, or a Phase
```

Every Phase runs through a sequence of *Development Cycles* that define, implement, and validate its *Tasks*. These *Cycles* are documented in separate reference files.

## Project Specifications

Specs describe **what** is being built. They may suggest technologies and give code examples, but they exist to explain the "why" and the "what" of the project. The documents that describe the "how" of the implementation are defined in the Development Cycle section below.

Specs live as flat files under `docs/specs/`, one per spec, each holding its latest version. See `references/spec-template.md` for location, versioning, structure, section-by-project-type guidance, and spec-to-phase traceability.

## Development Cycle Documentation Files

Markdown files serve three orthogonal goals: (a) documentation for the project's users and developers (e.g. `README.md`); (b) a medium for communicating with the team — approving a test plan, or agreeing how to split a project into Phases; and (c) persistent memory, so a long session can be resumed without losing critical implementation details.

Here is a list of the most critical files to track:

* `README.md`: Contains information on how to: (a) `build/compile/test` the project as a developer, and (b) how to use it as a user.
* `PLAN.md`: The work to be done and how it will be achieved — how each phase splits into tasks, and the list of those tasks. Each phase gets 5-10 bullet points at most.
* `DETAILED_PLAN.md`: Phase-scoped expansion of the PLAN.md bullets — the "how" to PLAN.md's "what". Carries the phase's security pre-review, test plan, and phase-specific DoD.
* `HANDOFF.md` (optional, phase-scoped): Written only when a session has to end mid-phase — where the phase stands, what is done, what is next, gotchas. The next session reads it, rebuilds its task list from it, and deletes it.
* `RETRO.md`: Phase retrospective — what went well, what was harder than expected, what was learned, and what changes in the upcoming phases. Written in cycle 095.
* `PROJECTS.md`: The central registry for sub-projects. Lives at `docs/PROJECTS.md`. Contains a list of sub-projects with codename, start date, and one-liner description. For a new project, agree a naming theme with the team — Greek Islands, Constellations, US Cities, and so on. See `references/sub-project-structure.md` for full documentation.
* `BACKLOG.md`: Deferred work — features, tech debt, ideas, and non-blocking bugs that don't fit the current phase. Created empty in cycle 010; swept and reviewed in cycle 090. See `references/backlog-management.md` for format and migration from legacy `TODO.md`/`FUTURE_WORK.md` files.
* `DECISIONS.md`: Architectural and design decisions log. Lives at `docs/DECISIONS.md`. Records significant decisions made during development — what was decided, why, and what alternatives were considered. Created in cycle 010, appended in cycle 090.
* `CLAUDE.md` (planning root): Agent-specific context and conventions. Lives at `docs/planning/CLAUDE.md`. Automatically loaded by Claude Code when working in the planning directory. See `references/sub-project-structure.md` for details.

### File organization

`PLAN.md` and every other `.md` file except `README.md` live under `docs/` at the project root. `DETAILED_PLAN.md` and `RETRO.md` are phase-scoped — they do not carry information forward to the next phase unless the team asks.

See `references/file-layout.md` for the directory trees, single- vs multi-project layout, and what to do when an existing project is not organized this way.

## Working with Large Markdown Files

`PLAN.md` grows over time. Reading it whole is fine for almost every project. For a very large one — past roughly 1,000 lines — read the phase section you need; see `references/plan-file-best-practices.md`.

## Development Cycles

Cycles run in order, 010 through 100, and never backward. Only 060 loops: it repeats until two consecutive hypothesis passes come back clean. Bugs found in 070 do not send you back to 040 — each one is fixed in PatchMode from inside 070, which runs the test-first, fix, harden sequence on that bug alone.

### Cycle Tracking via Agent Task List

Do **not** track cycle state in PLAN.md. Use the harness's task-list tool if it has one — `TodoWrite`, or the newer `TaskCreate` / `TaskUpdate` / `TaskList`. Check which is present rather than assuming; different Claude Code surfaces ship different ones, and some ship neither. If there is none, keep the cycle list in your own working message and update it there — it costs nothing and survives the same session. Either way it never goes in a file.

**When starting a new phase**, create a task list from the cycle sequence below, skipping any cycles excluded by the project type:

| Cycle | Name |
|-------|------|
| 010 | Init |
| 020 | Phase Selection and Planning Refinement |
| 030 | Test Plan Creation |
| 040 | Test Creation |
| 050 | Implementation |
| 060 | Code Hardening |
| 070 | Team Validation and Bug Fixing |
| 080 | README Update |
| 090 | Finalize Phase |
| 095 | Phase Retrospective |
| 100 | Git Commit |

Mark each cycle task as complete before moving to the next one.

### Resuming a Phase in a New Session

If the harness can resume the previous session with its task list and context intact, do that — it is the accelerator. Otherwise, or on a different host, rebuild from the repository, which is the record:

1. **Read `HANDOFF.md`** for the current phase, if there is one — the last session wrote it for exactly this. Delete it once you have rebuilt your task list from it
2. **Read the last 5-10 git log entries** — understand what was committed recently and what branch you're on
3. **Read the phase's `DETAILED_PLAN.md`** — the tasks, the tests planned, the DoD
4. **Run the test suite** — which planned tests exist, and which pass, tells you where cycles 040 and 050 stand. The code is the state; no file has to be kept in sync with it
5. **Scan PLAN.md** for the current phase — identify which tasks are checked off
6. **Recreate the cycle task list** from the table above, skipping any cycles excluded by the project type
7. **Determine your position** by examining project state against each cycle's preconditions. Mark cycles whose exit criteria are already satisfied as done, then continue from the first incomplete cycle

Do NOT start working until you have reconciled your position. State where you believe the phase stands and confirm with the team before proceeding.

## Project Types

The team declares the project type at the top of `PLAN.md`:

| Type | Use for | Cycles |
|------|---------|--------|
| `script` | Quick and dirty. 1-2 phases. | Skip `030`, `040`, `060` — no test plan, no tests, no hardening |
| `research` | Matters, but is not going to production. Unit and integration tests required; coverage need not be high. | Run all. Relax `060` to one clean hypothesis pass instead of two, and keep `080` (README) minimal |
| `production` | Going to production. | Run all, at full rigor |

Project type also relaxes some Definition of Done criteria — see `references/definition-of-done.md` § Project Type Adjustments.

**For scoped changes that don't warrant a full phase**, use **PatchMode** instead — see `references/patch-mode.md` for the size threshold. PatchMode keeps TDD discipline, a scratch `FIX.md`, and the harden steps, but skips spec, PLAN.md, sub-projects, and retrospectives.

Example:

Project-Type: production
