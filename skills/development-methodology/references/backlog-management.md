# Backlog Management

## Purpose

Capture intentionally deferred work — ideas, improvements, and tasks that don't fit the current phase but shouldn't be forgotten. The `BACKLOG.md` file gives deferred work a structured home so it doesn't leak into `PLAN.md`, get lost in random `TODO.md` files, or disappear between sessions.

## File Location

`BACKLOG.md` is created empty in cycle 010 (from `assets/BACKLOG.md`), so every later cycle has somewhere to put deferred work. It lives alongside `PLAN.md`:

```
# Single-project
docs/planning/BACKLOG.md

# Multi-project (per sub-project)
docs/planning/naxos/BACKLOG.md
docs/planning/milos/BACKLOG.md
```

## Format

Start from `assets/BACKLOG.md` for the blank skeleton. The worked example below shows the entry
conventions:

```markdown
# Backlog

## Features
- [ ] Bulk import endpoint — out of scope for Phase 2 (from: Phase 2, Cycle 050)
- [ ] CSV export option — deprioritized, JSON-only for now (from: Phase 3, Cycle 020)

## Tech Debt
- [ ] Replace polling with WebSockets — works but won't scale (from: Phase 4, Cycle 070)
- [ ] Consolidate duplicate validation logic in handlers (from: Phase 5)

## Ideas
- [ ] Plugin system for custom formatters — mentioned during Phase 3 planning
- [ ] Dark mode support — user feedback
```

### Entry Format

Each entry must include:

- **What**: brief description of the deferred work
- **Why**: reason it was deferred (out of scope, deprioritized, needs more info, etc.)
- **Origin**: where it came from — `(from: Phase N, Cycle NNN)` or `(from: spec vN)` or `(from: user feedback)`

Use `- [ ]` for open items and `- [x]` for items that have graduated into `PLAN.md`.

### Categories

Use these standard sections. Skip empty sections:

| Section | What goes here |
|---------|---------------|
| **Features** | New functionality deferred from scope |
| **Tech Debt** | Known shortcuts, scaling concerns, code smells |
| **Ideas** | Exploratory items that need more thought before committing |
| **Bugs (Non-blocking)** | Known issues that don't block current work |

## When to Add Items

Add to `BACKLOG.md` during any cycle when you encounter work that should be deferred:

- **Cycle 020 (Phase Selection and Planning Refinement)**: Tasks deemed out of scope for the current phase
- **Cycle 050 (Implementation)**: Shortcuts taken, tech debt observed, better approaches noticed but not worth the detour
- **Cycle 070 (Team Validation and Bug Fixing)**: Nice-to-haves identified during manual testing, non-blocking bugs the team agrees to skip
- **Cycle 090 (Finalize Phase)**: Final sweep — anything deferred during the phase that wasn't yet captured

## When to Review Items

- **Cycle 090 (Finalize Phase)**: After sweeping deferred work, review existing `BACKLOG.md` items. Some may be ready to become tasks in an upcoming phase or even justify a new phase entirely.

## Graduating Items

When a backlog item moves into `PLAN.md` as a real task or phase:

1. Check it off: `- [x]` in `BACKLOG.md`
2. Add a note: `→ moved to Phase N`
3. Do NOT delete it — the history is useful

Example:
```markdown
- [x] Bulk import endpoint — out of scope for Phase 2 (from: Phase 2, Cycle 050) → moved to Phase 7
```

## Migration from Existing TODO.md / FUTURE_WORK.md Files

Projects started before this convention may have deferred work scattered across `TODO.md`, `FUTURE_WORK.md`, inline `TODO` comments, or ad-hoc files. Follow this migration strategy:

### Step 1: Find existing files

```bash
# Find TODO/FUTURE_WORK files in planning directories
find docs/planning -name "TODO.md" -o -name "FUTURE_WORK.md" | sort

# Find any stray ones at project root or elsewhere
find . -maxdepth 2 \( -name "TODO.md" -o -name "FUTURE_WORK.md" \) -not -path "*/node_modules/*" -not -path "*/.git/*" | sort
```

### Step 2: Triage each item

For every item found in the old files:

| If the item is... | Then... |
|---|---|
| Still relevant and deferred | Move to the appropriate `BACKLOG.md` section with origin `(from: migrated from TODO.md)` |
| Already done | Drop it |
| Actually a bug | Move to `BACKLOG.md` under **Bugs (Non-blocking)**, or file it directly into `PLAN.md` if blocking |
| Vague or unclear | Move to **Ideas** section with a note that it needs clarification |

### Step 3: Remove the old files

Once all items are migrated:

1. Delete the old `TODO.md` / `FUTURE_WORK.md` files
2. Commit the migration with a clear message: `Migrate deferred work from TODO.md to BACKLOG.md`

### Step 4: Check for inline TODOs (optional)

```bash
# Find inline TODO comments that might represent deferred work
grep -rn "TODO\|FIXME\|HACK\|XXX" src/ --include="*.py" --include="*.ts" --include="*.js" | head -30
```

Inline `TODO` comments in code are fine for small tactical notes. But if a `TODO` represents a significant feature or design decision, it should also appear in `BACKLOG.md` so it's visible during phase selection.
