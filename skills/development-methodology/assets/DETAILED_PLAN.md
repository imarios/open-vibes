<!-- Template. Created in cycle 020; the Tests section is filled in cycle 030. Replace {placeholders},
     delete sections that don't apply, and delete this comment. Checkboxes appear only under Manual
     verification and Phase-specific DoD — the checks no machine can observe. Everything else is verified
     from the code and the test suite. -->

# {Project} Phase {N}: {Name} — Detailed Plan

## Goal

{What this phase achieves, in one paragraph. This expands the 5-10 bullets in PLAN.md into
enough detail to implement from — the "how" to PLAN.md's "what".}

## Scope

**In scope:**
- {Thing}

**Out of scope:**
- {Thing} — {why; add to BACKLOG.md if it should come back}

## Security pre-review
<!-- Required by cycle 020 Step 4. Design-time check, not a code review. Delete rows that don't apply.
     No security surface at all (local, single-user, no network, no secrets, no untrusted input)? Replace
     the table with that one sentence. -->

| Concern | Applies? | Notes |
|---------|----------|-------|
| Auth & authorization boundaries | {yes/no} | {where checks are needed} |
| Data flow & trust boundaries | {yes/no} | {where validation/sanitization is required} |
| Secrets & credentials | {yes/no} | {how they will be managed} |
| Infrastructure exposure | {yes/no} | {what needs locking down} |

## Implementation tasks

1. **{Task}** — {file or module}
   - {Detail an implementer needs: signature, edge case, ordering constraint}
2. **{Task}** — {file or module}

## Implementation order

{Why the tasks are sequenced this way — what blocks what.}

## Dependencies

- {Upstream phase, library, service, or decision this phase needs in place}

## Tests
<!-- Filled in cycle 030. Plain bullets, not checkboxes: a test is written when it exists in the test
     directory, and the suite is the record. -->

{Short paragraph: what these tests are meant to prove. State the intent — "prove the resolver rejects
cyclic dependencies with a typed error", not "test the resolver".}

### Unit tests — `{path/to/test_file}`

- {Positive: expected input produces expected result}
- {Positive: boundary value inside the valid range}
- {Negative: invalid input produces the specific error}
- {Negative: missing/empty/malformed input is rejected}

### Integration tests — `{path/to/test_file}`

- {Positive: components interact correctly end to end}
- {Negative: failure in one component surfaces correctly}

### Manual verification
<!-- Only for a Task that no automated test can exercise — interactive I/O, hardware, a real terminal.
     Cycle 090 performs these and ticks them. Delete if empty. -->

- [ ] {Exact steps} → {expected result}

## Phase-specific DoD
<!-- Required by cycle 020 Step 5. Cycle 090 performs these and ticks them; cycle 100's check refuses to
     commit with any left unticked. Nothing beyond the standard DoD? Write "None beyond the standard
     Phase DoD." as plain text — no checkbox. -->

- [ ] {e.g. Rebuild affected containers, start them, inspect logs for errors}
- [ ] {e.g. Verify new endpoints with example requests; confirm backward compatibility}

## Open questions

- {Question that needs a team answer before or during implementation — note the answer here when it comes}
