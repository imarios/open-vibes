<!-- Template. Single-project is the default form; the Sub-Project line is for multi-project repos only.
     Replace {placeholders}, delete sections that don't apply, and delete this comment. -->

# {Project Name}

Project-Type: production
Sub-Project: {Codename} (started MM/DD/YYYY)   <!-- multi-project repos only; delete otherwise -->

Spec: docs/specs/{spec}.md (v1.0)

{One paragraph: what this project delivers and why it matters. Two or three sentences.}

## Project shape

{Narrative: how many phases, why they are ordered this way, what each one lands. Name the
constraint that drives the ordering — e.g. "Phase 1 lands the type layer so the rest of the
codebase compiles against it."}

```
Phase 1: {Name}                    ({what it lands})
   │     {key source files}
   │     {key test files}
   ↓
Phase 2: {Name}
   │     ...
   ↓
Phase 3: {Name}
```

## Confirmed design decisions

1. **{Decision}**: {what was chosen, and the reason}.
2. **{Decision}**: {what was chosen, and the reason}.

## Phase 1: {Name}
<!-- Spec: {spec}.md R1, R3 -->

{One paragraph: what "done" looks like for this phase, in observable terms.}

### Tasks
- [ ] {Task — file or module it touches} ({spec requirement refs})
- [ ] {Task}
- [ ] Tests: {test file} ({what it covers})

### Per-phase DoD additions
<!-- From cycle 020 Step 5. Only the checks beyond the standard Phase DoD. -->
- [ ] {e.g. Rebuild affected containers and inspect logs}
- [ ] {e.g. Run migrations against a test database}

## Phase 2: {Name}
<!-- Spec: {spec}.md R4-R6 -->

{Paragraph.}

### Tasks
- [ ] {Task}

### Per-phase DoD additions
- [ ] {Check}
