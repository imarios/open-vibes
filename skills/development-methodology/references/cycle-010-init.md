# Cycle 010: Init Cycle

**Start HERE for new projects**

## Purpose

If planning has not been done, or PLAN.md does not agree with the design goals, produce a comprehensive execution plan for the project.

## Actions

### For New Projects

0. **Ask: Single or Multi-Project?**
   Before any planning, ask the team. Multi-project if either holds: the work will grow beyond 10-15 phases, or it has distinct feature sets that warrant separate plans. Otherwise single-project. If multi-project, agree a **naming theme** now (Greek Islands, Constellations, US Cities, and so on) — it shapes the entire directory structure and must be settled upfront.

1. **Decide on project structure**:
   - **Single-project**: Create `docs/planning/PLAN.md`
   - **Multi-project**: Create `docs/PROJECTS.md`, then set up the first sub-project (see below)

2. **If using sub-projects**:
   - Create first sub-project entry in `docs/PROJECTS.md` with codename, date, and description (start from `assets/PROJECTS.md`)
   - Create sub-project directory and its PLAN.md: `docs/planning/{subproject}/PLAN.md`
   - See `references/sub-project-structure.md` for details

3. **PLAN.md content** (whether single-project or sub-project) — start from `assets/PLAN.md`:
   - Split implementation into 5-10 phases
   - Each phase should have 5-10 coding tasks
   - Use `[x]` (done) or `[ ]` (not done) markers to track completion status

4. If no README.md file exists, initialize one here — a stub is enough. Cycle 080 fills it in every phase; do not also list "write the README" as a Phase task
5. Create `docs/DECISIONS.md` from `assets/DECISIONS.md` and record the decisions this cycle just made — project structure, project type, language and tooling. Cycle 090 appends to it from then on
6. Create `docs/planning/BACKLOG.md` from `assets/BACKLOG.md`, empty. It exists from the start so that every later cycle has somewhere to put deferred work and cycle 090's sweep always has a target

### For Existing Projects Adding a Sub-Project

1. Update `docs/PROJECTS.md` with new sub-project entry
2. Create sub-project directory: `docs/planning/{subproject}/`
3. Create `PLAN.md` in the sub-project directory (start from `assets/PLAN.md`)
4. Phase numbering starts at 1 (independent of other sub-projects)

## Notes

This cycle is more important for fresh projects or when starting a new sub-project within an existing project.

## Completion

Mark this cycle as complete in your task list and move on to Phase Selection and Planning Refinement Cycle (020).
