# Sub-Project Structure

**When to use sub-projects:** When a single project grows beyond 10-15 phases, or when distinct feature sets warrant logical separation, split into sub-projects.

## Overview

Large projects are organized into **Sub-Projects** - self-contained units of work with their own PLAN.md and phase numbering. Sub-projects are tracked in `docs/PROJECTS.md`.

## PROJECTS.md

The `PROJECTS.md` file is the central registry for all sub-projects. It lives at `docs/PROJECTS.md`.

### Format

Start from `assets/PROJECTS.md` for the blank skeleton. The worked example below shows the entry
conventions:

```markdown
# Projects

Project Naming Theme: Greek Islands

## Active Projects

- **Naxos** (09/25/2025): Pluggable connector framework for third-party integrations
- **Milos** (10/01/2025): Cloud deployment and environment provisioning
- **Rodos** (10/14/2025): Type-checked workflows built from reusable node templates

## Completed Projects

- **Paros** (10/03/2025 - 10/12/2025): MCP server exposing task-authoring tools ✅
```

### Required Fields

Each sub-project entry must include:
- **Codename** (bold): The sub-project identifier (e.g., Naxos, Milos)
- **Start date**: When work began
- **One-liner description**: What this sub-project accomplishes

### Naming Themes

When starting a new project, choose a naming theme for sub-projects. Examples:
- Greek Islands (Naxos, Milos, Rodos, Paros, Kea)
- Constellations (Orion, Cassiopeia, Perseus)
- US Cities (Austin, Denver, Portland)
- Elements (Helium, Neon, Argon)

The theme should be documented at the top of PROJECTS.md.

## Directory Structure

See `references/file-layout.md` § Multi-Project Structure for the tree — it owns the layout.

### Key Points

1. **Phase numbering resets**: Each sub-project starts at Phase 1
2. **Lowercase directories**: Sub-project folder names use lowercase (naxos, not Naxos)
3. **Self-contained**: Each sub-project has complete planning documentation
4. **`general/` is always present**: Captures unscoped and cross-project work so every piece of work maps to a sub-project
5. **`CLAUDE.md` at planning root**: Agent-specific context and conventions — see the section below

## Sub-Project PLAN.md Structure

Each sub-project's PLAN.md follows the standard format but includes a sub-project header:

```markdown
# Naxos - Pluggable Connector Framework

Project-Type: production
Sub-Project: Naxos (started 09/25/2025)

## Phase 1: Core Connector Interface ✅ COMPLETE

### Tasks
- [x] Define base connector abstract class
- [x] Implement configuration schema
...

## Phase 2: First Connector Implementation ✅ COMPLETE
...

## Phase 3: Connector Registry and Discovery

### Tasks
- [x] Build connector registry service
- [ ] Implement auto-discovery mechanism
...
```

## When to Create a New Sub-Project

Create a new sub-project on the same two criteria cycle 010 uses to choose multi-project in the first place: the work will grow beyond 10-15 phases, or it is a distinct feature set that warrants its own plan. Two signals that one of those has quietly become true: people need to work in parallel on unrelated features, or the main PLAN.md has grown past roughly 1,000 lines.

## Migrating from Single PLAN.md

If you have an existing large PLAN.md with multiple logical projects:

1. Identify logical groupings (look for project names in phase titles)
2. Create sub-project directories under `docs/planning/`
3. Move related phases to each sub-project's PLAN.md
4. Reset phase numbering within each sub-project
5. Update PROJECTS.md with all sub-projects
6. Archive or delete the old monolithic PLAN.md

**Note**: Discuss with the team before migrating - this is a significant reorganization.

## The `general` Sub-Project

Every multi-project repository includes a `general/` sub-project. It captures:
- Work that doesn't belong to any named sub-project
- Cross-project maintenance tasks (dependency upgrades, CI changes)
- Exploratory or ad-hoc work that hasn't been scoped into a named project yet

`general` follows the same structure as any other sub-project (PLAN.md, phase folders, etc.) and is listed in PROJECTS.md like any other entry. It uses a fixed name regardless of the naming theme.

## CLAUDE.md — Cross-Project Context

`docs/planning/CLAUDE.md` is automatically loaded by Claude Code when working in the planning directory. It provides agent-specific context at the start of every session. `AGENTS.md` is the cross-host equivalent; use whichever your agent honors, with the same content.

Use it for:
- Cross-project conventions and constraints relevant to the agent
- Notes that any future AI session should be aware of

**Note:** Architectural decisions belong in `docs/DECISIONS.md`, not here. `CLAUDE.md` is for agent context; `DECISIONS.md` is the human-readable decisions log.

This file is **not** phase-specific or sub-project-specific — it applies globally across all planning work.

## Cross-Project Coordination

### Dependencies Between Sub-Projects

If sub-project B depends on work from sub-project A:
1. Document the dependency in sub-project B's PLAN.md
2. Reference the specific phase/task in sub-project A
3. Example: "Depends on: Naxos Phase 2 (connector interface)"

### Working on Multiple Sub-Projects

You can work on multiple sub-projects in parallel:
- Each sub-project has its own cycle task list
- Switch between sub-projects as needed
- Clearly indicate which sub-project you're working on in conversation

## Selecting a Sub-Project

Cycle 020, Step 1 — see `references/cycle-020-phase-selection-and-planning.md`. Resuming mid-phase is covered by the session resume protocol in `references/overview.md`.
