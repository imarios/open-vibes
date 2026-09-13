# Cycle 095: Phase Retrospective

## Purpose

Pause after each phase to reflect on what worked, what didn't, and what the team learned. This mini-retro captures phase-level insights that improve the *remaining* phases of the project — while they're still actionable.

This is NOT the project retrospective (see `references/project-completion.md`). The project retro happens once, after all phases are done, and drives methodology-level changes. The phase retro happens after every phase and drives tactical adjustments for the next phases.

## Actions

### Step 1: Reflect

Answer these questions briefly (2-3 bullet points each, not essays):

1. **What went well?** — What parts of this phase were smooth? Any patterns, tools, or approaches worth repeating?
2. **What was harder than expected?** — Where did we spend more time than planned? What surprised us?
3. **What did we learn?** — Any new understanding about the codebase, domain, or tooling that changes how we should approach future work?
4. **Did the plan hold up?** — Were the tasks well-scoped? Did we add tasks mid-phase? Did we skip any as unnecessary?

### Step 2: Adjust

Based on the reflection:

1. **Refine upcoming phases**: If this phase revealed that future phases are mis-scoped (too big, too small, missing dependencies), update PLAN.md now. Don't wait until you're mid-implementation to discover the plan is wrong
2. **Update BACKLOG.md**: If anything was deferred, skipped, or discovered during this phase, make sure it's captured in BACKLOG.md (this should already be done in cycle 090, but double-check)
3. **Update CLAUDE.md**: If any tactical lesson is worth preserving for future sessions (not just future phases), add it to the relevant CLAUDE.md

### Step 3: Document

Write the retro to `docs/planning/phase_<N>/RETRO.md` (or `docs/planning/{subproject}/phase_<N>/RETRO.md` for multi-project repos). Start from `assets/RETRO.md` — it has the four standard sections. Keep it brief: a few bullets per section, not essays.

### Step 4: Discuss (if team validation happened)

If cycle 070 (Team Validation) was run for this phase, briefly discuss the retro findings with the team. The team may have additional observations from the validation process.

In FlashMode (where cycle 070 is skipped), the retro is still written but discussion is deferred to the next team interaction.

## Completion

Mark this cycle as complete in your task list and move on to Git Commit Cycle (100).
