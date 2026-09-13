# Cycle 100: Git Commit Cycle

## Purpose

Summarize the work, commit to git, and propose the next phase.

## Actions

1. Run `scripts/check_phase_done.py <N>` from the skill directory (`--sub-project <name>` in multi-project repos; `--test-cmd` if the suite is not auto-detected). It must pass. It checks what a machine can see: the ✅ COMPLETE header, no open task in the phase, the spec comment, no unticked manual check in `DETAILED_PLAN.md`, `RETRO.md` present, `DECISIONS.md` and `BACKLOG.md` present, the suite green. A failure means a cycle was skipped or shortened — go back to it
2. **Never commit code with broken tests**
3. Verify any pre-commit hooks pass
4. Create a comprehensive commit summarizing the phase work. Name the spec requirements the phase delivered and any it deferred — the commit is where cycle 090's spec walk leaves its record

## Phase Transition

After committing, proactively propose the next step:

1. Check PLAN.md for the next incomplete phase
2. Summarize what was just completed (1-2 sentences)
3. Propose the next phase with a brief description: *"Phase N complete. Next up: Phase N+1 — [description]. Shall I proceed?"*
4. If all phases are marked `✅ COMPLETE`, trigger the project completion process — see `references/project-completion.md`

Do not wait for the team to ask "what's next?" — always close a phase with a clear handoff.

## Completion

Mark this cycle as complete in your task list. To continue, create a fresh cycle task list for the next phase starting from Phase Selection and Planning Refinement (cycle 020).
