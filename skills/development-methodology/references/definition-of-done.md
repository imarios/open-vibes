# Definition of Done

This reference defines when work is considered complete at each level of the methodology. Use these checklists as the authoritative criteria — individual cycle files describe *how* to get there, this file defines *what "done" means*.

## Task DoD

A single task (e.g., "Implement function X") is done when:

- [ ] Code is implemented
- [ ] Tests for this task pass
- [ ] Task is checked off `[x]` in PLAN.md
- [ ] Its item on the work list is done (task list if the harness has one, otherwise its stub no longer raises not-implemented)

## Phase DoD

A phase is done when all of the following are true:

- [ ] All tasks checked off in PLAN.md for this phase
- [ ] Every requirement in the phase's `<!-- Spec: -->` comment is implemented or deferred to BACKLOG.md with a reason (cycle 090)
- [ ] All unit tests pass (mandatory unless the phase explicitly declares no code changes)
- [ ] All integration tests pass (if applicable)
- [ ] Every work item from cycle 030 is implemented — the work list is empty, and no not-implemented stub remains
- [ ] Every test planned in DETAILED_PLAN.md § Tests exists in the test directory; any Manual verification steps performed and ticked there
- [ ] Unit tests do not access databases, live REST endpoints, or live MCP servers
- [ ] Every bug found in team validation has a reproducing test (cycle 070)
- [ ] Phase-specific DoD criteria satisfied (see below)
- [ ] Code hardened — simplify pass, hypothesis review to 2 consecutive clean cycles, security review appropriate to what changed (cycle 060)
- [ ] README.md updated with new functionality (cycle 080)
- [ ] Deferred work swept into BACKLOG.md; `docs/DECISIONS.md` updated with any significant decisions (cycle 090)
- [ ] Phase retrospective written (cycle 095)
- [ ] `scripts/check_phase_done.py <N>` passes — the mechanical half of this checklist, run by cycle 100 before the commit
- [ ] Phase header in PLAN.md marked with `✅ COMPLETE` (cycle 090)
- [ ] Code committed (cycle 100)

### Phase-Specific DoD

During planning (cycle 020, Step 5), identify which of these additional checks apply based on what the phase changes:

| Change Type | Additional Verification |
|-------------|------------------------|
| **Code only** | Unit tests pass. Standard DoD is sufficient. |
| **Container/service changes** | Rebuild affected containers. Start them, inspect logs for errors. Run smoke tests or health checks. Verify dependent services still communicate. |
| **DB schema changes** | Run migrations against a test/dev database. Verify schema state. For large changes, run broader integration test with full stack. |
| **API changes** | Verify endpoints with example requests. Confirm backward compatibility or document breaking changes. |
| **Infrastructure/deployment** | Apply to dev/test environment. Verify services come up healthy. Check security groups, IAM, network policies. |
| **Configuration/env changes** | Restart affected services. Verify behavior. Confirm no secrets hardcoded or logged. |

Defined during planning (cycle 020, Step 5); verified by cycle 090 alongside the standard checklist.

## Sub-Project DoD

A sub-project (e.g., "Naxos") is done when:

- [ ] All phases marked `✅ COMPLETE` in the sub-project's PLAN.md
- [ ] No open tasks `[ ]` remain in any phase
- [ ] Entry moved from "Active Projects" to "Completed Projects" in PROJECTS.md
- [ ] End date added to the PROJECTS.md entry

## Project DoD

The overall project is done when:

- [ ] All sub-projects complete (multi-project) or all phases complete (single-project)
- [ ] README.md reflects the final state of the project
- [ ] No open tasks in any PLAN.md
- [ ] All tests pass across the entire codebase
- [ ] Spec verification complete — all requirements accounted for (implemented, deferred, changed, or dropped). See `references/project-completion.md`
- [ ] Deferred items reviewed with team — must-do items have proposed follow-ups
- [ ] Project retrospective written and discussed with team
- [ ] COMPLETION.md and PROJECT_RETRO.md created in docs/planning/

## Project Type Adjustments

The DoD applies differently based on project type (defined at the top of PLAN.md):

| Criteria | script | research | production |
|----------|--------|----------|------------|
| Tests pass | Skip | Required | Required |
| Test plan (DETAILED_PLAN.md § Tests) | Skip | Required | Required |
| README.md updated | Minimal | Required | Required |
