# Project Completion

## Purpose

When all phases of a project (or sub-project) are marked `✅ COMPLETE`, two things must happen before the project is truly done:

1. **Spec Verification & Deferred Items Review** — confirm everything was built and account for what wasn't
2. **Project Retrospective** — reflect on the process to drive methodology improvements

This is not optional. Every completed project goes through both steps.

## When to Trigger

### Single-Project or Sub-Project Completion

Trigger when all phases in a PLAN.md are `✅ COMPLETE`:

- **Single-project repos**: All phases in `docs/planning/PLAN.md` are done → run both steps below once
- **Multi-project repos**: All phases in a sub-project's `docs/planning/{subproject}/PLAN.md` are done → run both steps below for that sub-project. Outputs go in `docs/planning/{subproject}/COMPLETION.md` and `docs/planning/{subproject}/PROJECT_RETRO.md`

### Repo-Level Completion (Multi-Project Only)

When *all* sub-projects in `docs/PROJECTS.md` are marked complete, run a final repo-level retrospective in addition to the per-sub-project retros. This retro looks across all sub-projects for cross-cutting patterns: recurring late discoveries, scope estimation trends, methodology friction that appeared in multiple sub-projects.

Output: `docs/planning/PROJECT_RETRO.md` (repo-level, alongside the per-sub-project retros).

The team may also explicitly declare the project complete at any time.

## Step 1: Spec Verification & Deferred Items Review

Go back to the beginning and verify the project delivered what was promised.

### 1a: Walk the Specs

1. Read every spec file in `docs/specs/` that this project was built from
2. For each requirement in the spec, verify one of:
   - **Implemented** — the requirement is satisfied by code in the repo. Note the phase that delivered it
   - **Deferred** — the requirement was intentionally deferred. It MUST appear in BACKLOG.md with a clear reason
   - **Changed** — the requirement was modified during implementation. The spec should already reflect this (specs are updated in place). If it doesn't, update it now
   - **Dropped** — the requirement was abandoned. Document why in DECISIONS.md

### 1b: Review BACKLOG.md

1. Read BACKLOG.md end-to-end
2. For each open item, classify it:
   - **Must-do soon** — creates risk or blocks a known upcoming need. Propose a follow-up phase or project
   - **Nice-to-have** — useful but not urgent. Leave in BACKLOG.md
   - **Stale** — no longer relevant given what was built. Mark `[x]` with `→ dropped (no longer relevant)`
3. Present the must-do items to the team for review. The team decides whether to create a follow-up project, add phases, or accept the deferral

### 1c: Produce a Completion Summary

Create `docs/planning/COMPLETION.md` (or `docs/planning/{subproject}/COMPLETION.md` for multi-project repos) — start from `assets/COMPLETION.md`.

## Step 2: Project Retrospective

This is the big-picture reflection — not "what went well in Phase 5" (that's the phase retro), but "what did we learn about how we build software on this project."

### 2a: Gather Data

1. Read all phase retros (`docs/planning/phase_<N>/RETRO.md`) to identify recurring themes
2. Review DECISIONS.md for decisions that were revisited or reversed — these often signal process gaps
3. Review BACKLOG.md for items that were deferred multiple times — these often signal scope estimation issues
4. Check git log for patterns: emergency fixes, reverts, large refactors that suggest earlier phases missed something

### 2b: Reflect

Answer these questions (the team should discuss together):

1. **Planning accuracy**: How well did the original phases match what was actually built? Were phases added, removed, or significantly re-scoped?
2. **Late discoveries**: What important things (security issues, architectural problems, missing requirements) were discovered during implementation that should have been caught during planning?
3. **Process overhead**: Which parts of the methodology felt valuable? Which felt like overhead that didn't pay for itself?
4. **Tool & pattern effectiveness**: Did TDD catch real bugs? Did the hardening cycles find real issues? Did the phase retros lead to useful adjustments?
5. **What would we do differently?** If we started this project over with what we know now, what would change?

### 2c: Document

Create `docs/planning/PROJECT_RETRO.md` (or `docs/planning/{subproject}/PROJECT_RETRO.md`) — start from `assets/PROJECT_RETRO.md`.

### 2d: Discuss with the Team

The project retro MUST be discussed, not just written. Present the findings and proposed improvements. The team decides which improvements to adopt.

Methodology feedback from this retro may drive updates to the development methodology skill itself — this is how the methodology evolves.
