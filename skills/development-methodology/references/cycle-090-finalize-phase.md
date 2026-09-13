# Cycle 090: Finalize Phase Cycle

## Purpose

Verify the phase meets the Definition of Done and prepare for the next phase.

## Actions

1. Review the **Phase DoD** checklist in `references/definition-of-done.md` and verify every item is satisfied
2. In particular, confirm:
   - All tasks checked off in PLAN.md for this phase
   - All tests pass (unit and integration)
   - The work list from cycle 030 is empty — no open task, no remaining not-implemented stub; every data declaration and behavior change landed
   - Every test planned in `DETAILED_PLAN.md` § Tests exists; any Manual verification steps performed and ticked there
   - README.md updated (cycle 080)
3. **Run all unit tests.** This is mandatory unless the phase explicitly declares it is leaving code in an intentionally half-baked state (e.g., a planning-only or documentation-only phase with no code changes). If the phase touched code, tests must run and pass — no exceptions
4. **Verify phase-specific DoD**: Check the context-specific DoD criteria defined during planning (cycle 020, Step 5). If the phase modified containers, run them. If it modified DB schema, verify migrations. If it changed APIs, verify endpoints. See `references/definition-of-done.md` § Phase-Specific DoD for the full table. **Important**: Re-evaluate what actually changed during implementation — scope often shifts from what was planned. If the phase ended up touching containers, DB schema, or APIs that weren't anticipated in planning, apply the corresponding DoD checks now regardless of what was written in DETAILED_PLAN.md. Tick each item in DETAILED_PLAN.md as it is verified — these are the checks no machine can observe, and the ticks are their only record
5. Review phase documentation for completeness
6. Adjust checks based on project type (script, research, production) — see DoD reference for details
7. **Sweep deferred work into `BACKLOG.md`**: Review any items deferred during this phase (shortcuts, out-of-scope ideas, non-blocking bugs) and ensure they are captured in `BACKLOG.md`. See `references/backlog-management.md`
8. **Review backlog for graduation**: Check if any existing `BACKLOG.md` items should be added as tasks to an upcoming phase, or if they justify creating a new phase. If items graduate into `PLAN.md`, mark them `[x]` in `BACKLOG.md` with a `→ moved to Phase N` note
9. **Update `docs/DECISIONS.md`**: Record any significant architectural or design decisions made during this phase — what was decided, why, and what alternatives were considered. The file was created in cycle 010; append to it. Record a decision when it constrains future work or would be expensive to reverse — routine implementation choices stay in the commit message

10. **Walk this phase's spec requirements**: for each requirement in the phase's `<!-- Spec: -->` comment, confirm it is implemented by a checked-off task or sits in `BACKLOG.md` with a reason. A clause that is neither blocks completion
Cycle 100 runs `scripts/check_phase_done.py <N>` before committing. It re-checks, mechanically, everything above that a machine can see. Anything skipped here blocks the commit there.

## Completion

Mark phase as complete (add ✅ COMPLETE to phase header). Mark this cycle as complete in your task list and move on to Phase Retrospective Cycle (095).
