<!-- Template. Write this ONLY when a session has to end mid-phase. It exists so the next session — on
     any host, with no memory of this one — can rebuild its task list and continue. Delete it once the
     next session has resumed. Replace {placeholders} and delete this comment. -->

# {Project} Phase {N} — Handoff

Written {MM/DD/YYYY} at the end of a session, mid-phase.

## Where the phase stands

- Cycle in progress: {NNN — name}
- Cycles done: {list}

## Task list to rebuild

- [x] {work item that landed}
- [ ] {work item still open — stub, data declaration, or behavior change}

## Next step

{The single concrete thing to do first on resume.}

## Gotchas

- {Anything the next session would otherwise have to rediscover — a misleading error, a non-obvious
  ordering constraint, a decision made mid-cycle that DECISIONS.md does not yet record}
