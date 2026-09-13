# Spec Template

This reference defines the structure for project specification documents. Specs describe **what** is being built and **why** — not how to implement it. Implementation details belong in PLAN.md and phase-specific planning files.

## Spec Location

All specs live under `docs/specs/` as flat files:

```
docs/specs/auth_design.md
docs/specs/data_model.md
docs/specs/pipeline_ingestion.md
```

Each spec file always contains the **latest** version of that spec. There are no version folders — version history is tracked per-file using frontmatter (see Template below) and git history.

## Sections by Project Type

Not every spec needs every section. Use the project type (defined at the top of PLAN.md) to decide:

| Section | script | research | production |
|---------|--------|----------|------------|
| Problem Statement | Required | Required | Required |
| Goals & Non-Goals | Skip | Optional | Required |
| Requirements | Required | Required | Required |
| Data Model | Optional | Optional | Required (if applicable) |
| Constraints | Skip | Optional | Required |
| Error Handling | Skip | Optional | Required |
| Testing Checklist | Skip | Required | Required |
| Open Questions | Optional | Optional | Required |
| Future Work | Skip | Optional | Optional |

## Template

```markdown
# [Feature/Component Name]

+++
version = "1.0"
date = "YYYY-MM-DD"
status = "draft"  # draft | active | deprecated

[[changelog]]
version = "1.0"
date = "YYYY-MM-DD"
summary = "Initial spec"
+++

## Problem Statement

What problem are we solving and why does it matter?
Keep this to 2-5 sentences. Focus on the user or system need, not the solution.

## Goals & Non-Goals

### Goals
- What this spec WILL accomplish
- Be specific and measurable where possible

### Non-Goals
- What this spec explicitly WILL NOT address
- Prevents scope creep — if someone asks "should we also do X?", point here

## Requirements

Functional requirements — what must be true when this is done.

- **R1**: The system must...
- **R2**: Users can...
- **R3**: When X happens, Y must...

Number requirements (R1, R2, ...) so phases and tasks can reference them.

## Data Model

Key entities and their relationships. Use tables, ERDs, or code blocks:

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | UUID | Primary key | Immutable |
| name | string | Display name | Max 255 chars |

Include validation rules and constraints. Show example records if helpful.

## Constraints

Technology choices, performance targets, compatibility needs:

- Must use [technology X] because...
- Response time under N ms for...
- Must be compatible with...
- Must not depend on...

## Error Handling

How the system behaves when things go wrong:

| Scenario | Behavior | User Impact |
|----------|----------|-------------|
| Invalid input | Return 400 with field-level errors | User sees specific fix instructions |
| Service unavailable | Retry 3x with backoff, then fail | User sees "try again later" |

## Testing Checklist

How to verify this works. Concrete and executable:

- [ ] Happy path: create X, verify Y
- [ ] Edge case: empty input returns appropriate error
- [ ] Edge case: duplicate entry is rejected
- [ ] Integration: end-to-end flow from A to Z

## Open Questions

Decisions not yet made. Resolve these before or during cycle 020 (Phase Selection and Planning Refinement):

- **Q1**: Should we support X or Y approach? (leaning toward X because...)
- **Q2**: What is the expected scale? (affects data model choice)

## Future Work

Explicitly deferred items. Things we know we'll want but are out of scope for now:

- Support for bulk operations (defer to a later phase)
- Admin UI for managing X (separate spec needed)
```

## Spec-to-Phase Traceability

Phases in PLAN.md should reference the spec they implement using an HTML comment:

```markdown
## Phase 3: User Authentication
<!-- Spec: auth_design.md -->

### Tasks
- [ ] Implement login endpoint (R1, R2)
- [ ] Add rate limiting (R5)
```

Key conventions:
- The `<!-- Spec: -->` comment uses a path relative to `docs/specs/`
- Tasks can reference specific requirements by number (R1, R2, etc.)
- A phase can reference multiple specs if needed: `<!-- Spec: auth.md, sessions.md -->`
- The spec comment goes directly under the phase header
- A phase that implements no requirement (scaffolding, tooling) still carries the comment: `<!-- Spec: none — scaffolding -->`

This makes it easy to find which spec drives which phase:

```bash
grep "Spec:" docs/planning/PLAN.md
```

## Good Spec Practices

Drawn from real project specs:

1. **Examples over prose** — Show a JSON payload, a SQL schema, a curl command. Worth more than paragraphs of explanation
2. **Bad vs. good comparisons** — Use ❌/✅ to show what NOT to do alongside the right approach
3. **Tables for structured data** — Attributes, error codes, field definitions, enum values
4. **Keep it scannable** — one heading per question a reader would ask, so any answer is reachable from the section list without reading prose. Bullets and code blocks over paragraphs
5. **State rationale for decisions** — "We chose X because Y" prevents the same debate from recurring
6. **State requirements as observable outcomes, not implementation stages** — "unsupported syntax is rejected with a compile error naming the line", not "rejected by the parser". A stage can turn out to be the wrong one; an outcome cannot
