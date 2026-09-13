---
name: development-methodology
description: Plan and implement software projects using phases, development cycles (010–100), and TDD. Use when starting a project, managing PLAN.md, implementing a phase, applying a scoped fix with PatchMode, or running autonomously with FlashMode or LightningMode.
version: 4.4.0
dependencies:
  - code-refinement-with-hypothesis
---

# Development Methodology

Systematic approach to planning and implementing software projects using phases, tasks, and development cycles.

## When to Use This Skill

Use this skill when:
- Starting a new software development project
- Planning project phases and breaking down work into tasks
- Following TDD (Test-Driven Development) workflows
- Working through implementation cycles (planning, testing, implementation, validation)
- Managing collaboration between team members on structured projects
- Tracking progress through development cycles
- Applying a PatchMode-sized change that doesn't warrant a full phase (TDD + harden, no project ceremony — see `references/patch-mode.md` for the size threshold)
- Running autonomous implementation (FlashMode for a single phase, LightningMode for an entire project)
- Completing a project (spec verification, deferred items review, project retrospective)

## Team Interaction

Refer to the humans you work with as "the team", not "the user". See `references/overview.md` §
Working Relationship for the full model — coworker framing, pushback norms, and `CLAUDE.md`
preferences.

## Reference Routing Table

**Read `references/overview.md` before any cycle or phase work.** It is short and defines the vocabulary every other reference assumes — Phases, Tasks, Cycles, project types, and the 010–100 sequence. Then load only the references the task at hand calls for.

| Reference | Read when you need to… |
|-----------|------------------------|
| `overview.md` | **First, every time** — core concepts, cycle sequence 010–100, team model, session resume protocol |
| `plan-file-best-practices.md` | Read or edit a very large PLAN.md |
| `sub-project-structure.md` | Projects grow beyond 10-15 phases — PROJECTS.md registry, `planning/{subproject}/PLAN.md` layout, naming themes |
| `spec-template.md` | Write project specs — section-by-project-type table, spec-to-phase traceability convention |
| `cycle-NNN-*.md` | Execute a specific cycle — load the matching cycle file, follow sequentially 010→100 |
| `patch-mode.md` | Apply a **PatchMode-sized scoped change** (see the file for the size threshold) with TDD + a scratch `FIX.md` + a harden pass, but no project ceremony. Invoke: *"Use PatchMode to [description]"* |
| `flash-mode.md` § FlashMode | Implement **one phase** autonomously — runs the standard cycles 020–100 without stopping, skipping only 070 (Team Validation). Invoke: *"Use FlashMode to implement Phase X"* |
| `flash-mode.md` § LightningMode | Implement an **entire project** autonomously — runs FlashMode on every incomplete phase, sequentially, until all phases are `✅ COMPLETE`. Invoke: *"Use LightningMode to implement the project"* |
| `definition-of-done.md` | Determine if work is complete — criteria per level (task, phase, sub-project, project), phase-specific DoD, project-type adjustments |
| `project-completion.md` | Close out a completed project — spec verification, deferred items review, project retrospective. Triggered when all phases are `✅ COMPLETE` |
| `file-layout.md` | Set up or reorganize the `docs/` tree — single- vs multi-project layout, which files are phase-scoped |

Upgrading an existing project from an older methodology version? See `CHANGELOG.md` at the skill root.

## Templates

`assets/` holds a blank skeleton for every file the methodology asks you to create. Read the
matching template before writing the file for the first time — do not invent a structure. Replace
the `{placeholders}`, delete sections that don't apply, and delete the leading HTML comment.

| Create this | From | Cycle |
|-------------|------|-------|
| `docs/planning/PLAN.md` | `assets/PLAN.md` | 010 |
| `docs/PROJECTS.md` | `assets/PROJECTS.md` | 010 |
| `phase_<N>/DETAILED_PLAN.md` | `assets/DETAILED_PLAN.md` | 020 (plan), 030 (its Tests section) |
| `phase_<N>/HANDOFF.md` | `assets/HANDOFF.md` | only when a session must end mid-phase |
| `docs/planning/BACKLOG.md` | `assets/BACKLOG.md` | 010 (created empty), swept in 090 |
| `docs/DECISIONS.md` | `assets/DECISIONS.md` | 010 (created), appended in 090 |
| `phase_<N>/RETRO.md` | `assets/RETRO.md` | 095 |
| `docs/planning/COMPLETION.md` | `assets/COMPLETION.md` | project completion |
| `docs/planning/PROJECT_RETRO.md` | `assets/PROJECT_RETRO.md` | project completion |

Specs are the exception — they have their own reference, `references/spec-template.md`.

## Tracking State vs. Records

Two kinds of state, two homes. **Records** — the spec, PLAN.md, DETAILED_PLAN.md, DECISIONS.md, BACKLOG.md, RETRO.md — are files in git: durable, readable by the next human or the next agent on any host. **Tracking state** — which stub is done, which test is written, which cycle you are in — never lives in a checklist file. Prefer the harness's task list when it has one; where a task list can't carry the state, each kind has its own fallback — see `references/overview.md` § Cycle Tracking for cycle position, and `references/cycle-030-test-plan-creation.md` step 3 for stubs (an open stub is an open item; a test is written when it exists, a stub is done when the suite says so). The only checkboxes that survive are for checks no machine can observe (manual verification, phase-specific DoD), and a script verifies everything else.

## Scripts

| Script | Usage | Purpose |
|--------|-------|---------|
| `scripts/check_phase_done.py` | `scripts/check_phase_done.py <N> [--sub-project NAME] [--test-cmd CMD]` | Mechanical phase-done check, run by cycle 100 before the commit: ✅ header, no open task, spec comment, no unticked manual check, RETRO present, DECISIONS/BACKLOG present, suite green |
