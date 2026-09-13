# File Layout

Where the methodology's documents live in the repository.

`PLAN.md` and every other created `.md` file except `README.md`
live under `docs/` at the project root.

Some of these files are phase-scoped. `DETAILED_PLAN.md` and `RETRO.md` belong to the current phase
and must not carry information forward to the next one unless the team asks for it. That is why each
phase gets its own directory.

## Single-Project Structure

```
README.md                              # At the root of the project

docs/PROJECTS.md                       # Sub-project registry (optional for small projects)
docs/DECISIONS.md                      # Architectural and design decisions log
docs/planning/PLAN.md                  # Plan for the entire project
docs/planning/BACKLOG.md               # Deferred work
docs/planning/phase_1/DETAILED_PLAN.md # Plan, security pre-review, tests, DoD for phase 1
docs/planning/phase_1/RETRO.md         # Phase 1 retrospective
docs/planning/phase_1/HANDOFF.md       # Only if a session ended mid-phase; deleted on resume
```

## Multi-Project Structure (beyond 10-15 phases)

When a project grows beyond 10-15 phases, split it into sub-projects. Each sub-project has its own
PLAN.md, and its phase numbering resets to 1.

```
README.md                                 # At the root of the project

docs/PROJECTS.md                          # Sub-project registry (required)
docs/DECISIONS.md                         # Architectural and design decisions log
docs/planning/CLAUDE.md                   # Agent context & conventions (always loaded)
docs/planning/general/PLAN.md             # Unscoped / cross-project work
docs/planning/general/phase_1/DETAILED_PLAN.md
docs/planning/naxos/PLAN.md               # Naxos phases 1-N
docs/planning/naxos/BACKLOG.md            # Deferred work, scoped to Naxos
docs/planning/naxos/phase_1/DETAILED_PLAN.md
docs/planning/naxos/phase_1/RETRO.md
docs/planning/milos/PLAN.md               # Milos phases 1-N (numbering resets)
docs/planning/milos/phase_1/DETAILED_PLAN.md
```

Sub-project folders use lowercase names. See `references/sub-project-structure.md` for when and how
to split a project, and `assets/PROJECTS.md` for the registry template.

## Reorganizing an Existing Project

If the files are not organized this way, discuss it with the team before moving anything. The
layout is worth adopting, but a bulk move mid-phase costs more than it returns — the natural time
is between phases.
