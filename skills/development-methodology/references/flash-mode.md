# Flash Mode: Autonomous Phase Implementation

## Purpose

FlashMode is an autonomous workflow that implements an entire phase without stopping for team validation. Use this mode when you have a clear phase description in PLAN.md and want to execute it fully autonomously from planning through implementation, hardening, and commit.

## When to Use FlashMode

- Phase description in PLAN.md is clear and well-defined
- No ambiguity about what needs to be built
- Working on a well-understood feature or component
- Want rapid iteration without manual validation checkpoints

## When NOT to Use FlashMode

- Phase requirements are unclear or ambiguous
- Working on critical production features that need manual review
- Making architectural changes that require team discussion
- First time implementing a new pattern or technology

## CRITICAL: Go Fast, Never Cut Corners

**FlashMode and LightningMode are about speed — not about cutting corners.** The speed comes from removing wait-time between cycles (no stopping for team validation), NOT from skipping steps or doing them halfway.

Every phase MUST go through every cycle in the workflow table below, in order. No shortcuts. No merging steps together. No skipping cycles "because the phase is small" or "because we're in autonomous mode."

The whole point of the methodology is that the structure produces quality. Autonomous execution is faster because it removes human handoff delays — but the rigor stays exactly the same.

## FlashMode Workflow

Run the standard cycles in order, without stopping for team input. **Each cycle file is the authority
on what to do** — load it when you reach it and follow it in full. The table below states only what
FlashMode changes; where the delta is "none", the cycle runs exactly as written.

| # | Cycle | FlashMode delta |
|---|-------|-----------------|
| 1 | `cycle-020-phase-selection-and-planning.md` | Do not stop to agree the phase with the team — take the next incomplete phase in PLAN.md and proceed |
| 2 | `cycle-030-test-plan-creation.md` | No team approval of the test plan — proceed straight to 040 |
| 3 | `cycle-040-test-creation.md` | none |
| 4 | `cycle-050-implementation.md` | none |
| 5 | `cycle-060-code-hardening.md` | none |
| — | `cycle-070-team-validation.md` | **Skipped.** The only cycle FlashMode omits — it is the one that requires a human in the loop |
| 6 | `cycle-080-readme-update.md` | none |
| 7 | `cycle-090-finalize-phase.md` | none |
| 8 | `cycle-095-phase-retrospective.md` | Write `RETRO.md` as usual; Step 4 (discuss with the team) is deferred to the next team interaction |
| 9 | `cycle-100-git-commit.md` | One commit for the whole phase. Propose the next phase, but do not wait for an answer |

**Use the templates.** Every file these cycles create has a blank skeleton in `assets/` — see the
Templates table in `SKILL.md`. Autonomous runs have no team member to catch an invented structure, so
this matters more here, not less.

## FlashMode Checklist

The phase is complete when the **Phase DoD** in `references/definition-of-done.md` is fully satisfied
— that checklist is the authority, and it already covers tests, the task list, the test plan,
PLAN.md, README, retrospective, and the commit.

FlashMode adds only these:

- [ ] Every cycle above was actually run — none merged, shortened, or skipped except 070
- [ ] The phase landed as a single commit
- [ ] The next incomplete phase has been proposed

## Output Expectations

At the end of a FlashMode run, the Phase DoD is satisfied and the phase exists as one commit, with a
proposal for the next phase. Nothing about the deliverables differs from a phase run interactively —
only the absence of team checkpoints along the way.

## Recovery from FlashMode

Issues found after a FlashMode run are the team validation that FlashMode skipped, arriving late. Size decides the route, the same way it does everywhere else in the methodology:
- PatchMode-sized (see `references/patch-mode.md` for the threshold) → fix it in PatchMode, exactly as cycle 070 would have
- Bigger → add a phase or tasks to PLAN.md and run it as a phase, with FlashMode or without

## Invoking FlashMode

When working with a subagent, you can invoke FlashMode by instructing:

"Use FlashMode from the development-methodology skill to autonomously implement Phase X."

The subagent should:
1. Read the phase description from PLAN.md
2. Follow the FlashMode workflow autonomously
3. Complete all steps without stopping for validation
4. Commit everything at the end

---

# Lightning Mode: Autonomous Project Implementation

## Purpose

LightningMode implements an **entire project** end-to-end by running FlashMode on every phase, one at a time, until all phases are complete. Use this when the project plan is solid and you want fully autonomous execution across all phases.

## When to Use LightningMode

- All phases in PLAN.md are clearly defined
- Project type is well-understood (not exploratory)
- You trust the plan enough to let it run without checkpoints between phases

## When NOT to Use LightningMode

- Phases are loosely defined or likely to change
- The project requires mid-course architectural decisions
- You want to review work between phases
- First time working on this type of project

## LightningMode Workflow

**Reminder: Never skip the full phase structure for any phase — see "CRITICAL: Go Fast, Never Cut Corners" above.**

1. Read PLAN.md and identify all incomplete phases (sequential, lowest to highest)
2. For each incomplete phase, run **FlashMode** (see workflow above)
3. After each phase completes, move to the next incomplete phase
4. Repeat until all phases are marked `✅ COMPLETE`

The agent should not stop between phases unless:
- A phase fails (tests don't pass, blocking issue)
- The agent encounters ambiguity that cannot be resolved from the specs

## Invoking LightningMode

"Use LightningMode from the development-methodology skill to autonomously implement the entire project."

Or for a sub-project:

"Use LightningMode to implement all remaining phases of the Naxos sub-project."

## Output Expectations

Every phase satisfies the Phase DoD, one commit per phase, and the **Project DoD** in
`references/definition-of-done.md` is satisfied for the project as a whole.

## Project Completion

When LightningMode finishes all phases, it MUST trigger the project completion process:

1. **Spec verification** — walk every spec and verify all requirements are accounted for
2. **Deferred items review** — classify BACKLOG.md items and present must-do items to the team
3. **Project retrospective** — reflect on the entire process, document findings

See `references/project-completion.md` for the full protocol. This step is not optional — it is what closes the project.
