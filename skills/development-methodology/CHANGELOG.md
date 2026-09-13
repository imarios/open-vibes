# Changelog

Version history for the development-methodology skill. Each entry says what changed and, where a
release moved files or renamed conventions, what an existing project has to do about it.

## 4.4.0

Tightened the frontmatter `description` to remove a common description anti-pattern (a "Covers X, Y, Z"
clause reading as a trigger-term list bolted onto the WHAT/WHEN sentences). It ran 496 characters and
named every mode and reference topic; it's now 253 characters, keeping only the terms distinctive to
this skill — PLAN.md, the 010–100 cycle range, PatchMode, FlashMode, LightningMode — woven into the
WHAT and WHEN sentences instead of appended as a list.

**Migration**: none.

## 4.3.0

The PatchMode size threshold (~20–150 lines, 2–6 files) was copied into five files. `patch-mode.md`
is now the only place the numbers live — `SKILL.md` (both mentions), `flash-mode.md`, and
`overview.md` say "PatchMode-sized" and point there instead of restating the figures.

**Migration**: none.

## 4.2.0

DRY pass on `SKILL.md` against `references/overview.md` — the two files every cycle or phase task
reads together, so anything stated twice there is the highest-visibility duplication in the skill.

- **Team Interaction** no longer restates three of `overview.md`'s Working Relationship bullets. It
  keeps the one load-bearing line ("the team", not "the user") and points at the reference for the
  rest.
- **Tracking State vs. Records** no longer names the task-list tools itself — `overview.md` § Cycle
  Tracking is now the only place `TodoWrite` / `TaskCreate` / `TaskUpdate` / `TaskList` are listed.
  This also fixes a real inconsistency: the old wording said cycle position falls back to "the code
  itself" when there's no task list, but `overview.md` correctly uses a working-message fallback for
  cycle position (stubs are the fallback for a different kind of tracking state, per cycle 030). The
  two are now cross-referenced instead of each guessing at the other's mechanics.

**Migration**: none.

## 4.1.0

Fixes from the third real run (a ledger CLI at 4.0.0 — every 4.0.0 change held) and from reading the
log of five days of real maintenance on skilltree, where PatchMode ran about fifteen times.

- **The task list is no longer assumed.** 4.0.0 said work items "live on the agent's task list".
  Three of three environments observed this week — the desktop app, a subagent spawned from it, and
  the session that wrote this — expose no such tool; only the CLI does, as `TodoWrite` or the newer
  `TaskCreate` / `TaskUpdate` / `TaskList`. The methodology now names both, says to check which is
  present, and makes the fallback explicit: the stubs are the list, `grep NotImplementedError` is the
  open-items query, empty is done. Two agents invented that fallback independently; it is now the rule.
- **`/resolve-issue` invokes the skill instead of pointing at a path.** Fourteen of fifteen runs in the
  skilltree log never loaded `patch-mode.md`, despite the pointer landing one minute before the
  session started — the agent could not locate the skill. The Skill tool resolves that.
- A phase with nothing beyond the standard DoD writes one plain sentence, not a checkbox to tick. A
  project with no security surface says so once instead of filling an N/A table every phase.
- Cycle 030 gains the fourth Task shape: a plain data type is covered by its first consumer's tests.
- Cycle 060 notes that a first phase has no diff base — the review is every file.

**Migration**: none.

## 4.0.0

Modernization. The methodology stops using markdown files as tracking state — the job modern agent
harnesses do natively — and keeps files for what only files do: durable records a human or a
different agent can read. Measured against 234 real `TEST_PLAN.md` files, only 20% ever had their
boxes ticked back and 42% had no boxes at all; 62% of `SHORT_MEMORY.md` files were nothing but a
todo list. The choreography was not being followed, and the 3.13.0 rule that tightened it was the
wrong direction.

- **`SHORT_MEMORY.md` retired.** The work items from cycle 030 live on the agent's task list. A new
  optional `HANDOFF.md` is written only when a session must end mid-phase, and deleted on resume.
- **`TEST_PLAN.md` retired.** The test plan — intent, positive and negative cases, manual steps — is
  the `## Tests` section of `DETAILED_PLAN.md`. Tests are plain bullets: a test is written when it
  exists, and the suite is the record. Per-phase files drop from four to two.
- **"Verification leaves marks" replaced by `scripts/check_phase_done.py`.** Cycle 100 runs it before
  committing. It checks what a machine can see: ✅ header, no open task, spec comment, no unticked
  manual check, RETRO present, DECISIONS and BACKLOG present, suite green. The only checkboxes that
  survive are for checks no machine can observe. Stdlib only; ships with its own tests.
- **`plan-file-best-practices.md` collapsed** from 158 lines of grep choreography to a paragraph.
  Real PLAN.md sizes: median under 200 lines, p90 about 900, max about 2,300 — all fit a modern
  context. Read the whole file; for a very large one, read the phase section.
- **Resume protocol** names harness-native resume as the accelerator and rebuilds from the
  repository otherwise — git log, DETAILED_PLAN, the test suite, HANDOFF.md if present.
- **`AGENTS.md`** named as the cross-host equivalent of `CLAUDE.md`.
- New SKILL.md section, *Tracking State vs. Records*, states the principle so it is not re-derived.

Also the six fixes from the second real run (a Sonnet agent building a MiniLang compiler at 3.13.0,
5 phases, 115 tests — every 3.13.0 fix held): a Task with no red state is folded into the Task that
gives it behavior and never faked; tests that assert a placeholder's contract are never written and
are deleted, not "changed", when the real behavior lands; completed phases are never reopened —
a change to earlier-phase code is work in the current phase; spec requirements are stated as
observable outcomes, not implementation stages; a scaffolding phase carries
`<!-- Spec: none — scaffolding -->`; README is stubbed in cycle 010 and never listed as a Phase task;
the cycle 060 stop rule is the only rule — no cap, no minimum.

**Migration**: existing `TEST_PLAN.md` and `SHORT_MEMORY.md` files stay where they are; nothing reads
them any more. New phases create neither. Add `## Tests` to `DETAILED_PLAN.md` from the template
when a phase is next planned. `check_phase_done.py` runs against any project laid out per
`file-layout.md`.

## 3.13.0

First release driven by a real run. A Sonnet agent built a Tetris game from scratch under
LightningMode at 3.12.0 (5 phases, 94 tests, 6 commits) and reported every point where the
methodology was unclear, contradictory, or impossible to follow; an independent review of the
artifacts found two more. All seven are fixed here.

- **Cycle 030's stub definition now covers all three Task shapes.** "A body that raises
  not-implemented" only described new functions. Every phase of the run hit a data table or a
  change to an existing method, where there is nothing to stub — the failing test is the
  placeholder. `SHORT_MEMORY.md` lists all three kinds.
- **Spec coverage is checked per phase.** A requirement clause (R12's "restart") was silently
  narrowed in phase 5 planning and surfaced only at project completion. Cycle 020 now maps every
  claimed requirement to a task; cycle 090 walks them before ✅ COMPLETE; the Phase DoD lists it.
- **Verification leaves marks.** Cycle 090 said "verify every item" but never said to tick anything,
  and the Phase DoD lives in a read-only reference with no per-phase instance. Result in the run:
  the phase-specific DoD was unticked in all five phases and phase 2's success criteria were
  unticked, with every phase marked complete. Cycle 090 now ticks each item where it lives, and an
  unticked `[ ]` anywhere in the phase folder blocks completion.
- **`DECISIONS.md` and `BACKLOG.md` are created in cycle 010.** Cycle 010 makes real decisions but
  DECISIONS.md's only trigger was cycle 090; nothing said when BACKLOG.md first exists. Both now
  exist from the start.
- **Manual-only verification has a home.** A Task no automated test can exercise (interactive I/O,
  hardware) gets a `## Manual verification` section in TEST_PLAN.md with exact steps; cycle 090
  performs and ticks them. An exception per Task, not an escape hatch per phase.
- **`assets/PLAN.md` defaults to single-project.** It led with a codename header and a
  `Sub-Project:` line, so the common case meant deleting template lines.

Also from the run, worth recording: cycle 060's hypothesis step caught a bug before it was written
in phase 3 and a wrong "simplification" in phase 5 — the first direct evidence that the hardening
cycle earns its cost.

**Migration**: existing projects should create `docs/DECISIONS.md` and `docs/planning/BACKLOG.md`
if absent. Nothing else changes for files already written.

## 3.12.0

Fresh-eyes pass on the remaining references. This completes the pass across the whole skill.

- `sub-project-structure.md` gave three different thresholds for creating a sub-project ("5+ phases",
  "10 phases", "10-15 phases"). It now uses the same two criteria cycle 010 uses to choose
  multi-project. Its directory tree (a copy of `file-layout.md`'s) and its "Selecting a Sub-Project"
  section (a copy of cycle 020 Step 1) are pointers now.
- `assets/COMPLETION.md` and `assets/PROJECT_RETRO.md` added — the two skeletons the 3.5.0 templates
  pass missed, previously inline in `project-completion.md`. The Templates table now really does
  cover every file the methodology creates.
- `overview.md`'s spec section no longer restates spec location and versioning; `spec-template.md`
  owns them.
- "A developer should find what they need in 30 seconds" → one heading per question a reader would
  ask. Seconds are not something the agent can check.
- `definition-of-done.md` said "verified by cycle 090" in two adjacent sentences; once now.
- `plan-file-best-practices.md`'s twelve-line "Why This Matters" is one sentence.

**Migration**: none.

## 3.11.0

Fresh-eyes pass on PatchMode and FlashMode. Two of the fixes are for things earlier entries in this
changelog claimed were already done.

- `flash-mode.md` had duplicate "Output Expectations" and "Recovery" sections. The v3.8.0 rewrite
  replaced the range ending at "Invoking FlashMode" and the old copies sat after it — including the
  DoD-restating list that release said was removed. Gone now.
- `patch-mode.md`'s "What PatchMode Keeps" list still framed the harden pass as `/simplify` +
  `/code-refinement-with-hypothesis`, the framing v3.7.0 said was fixed "at all four sites". It was
  the fifth. The list is dropped; the skips table and the Purpose paragraph already say what it said.
- **PatchMode's floor no longer exempts bug fixes from a reproducing test.** "Single-line bug fix —
  just make the change" contradicted the standing rule that every bug is reproduced with a test
  first, and cycle 070 as of v3.9.0. A tiny fix may skip the scratch file and the harden pass; never
  the test.
- "If you can't write this in under 10 minutes" → "if the test list or affected-files list won't fit
  in a handful of bullets". Minutes are not something the agent can check.
- PatchMode Step 3's container / DB / config validation was a third copy of the Phase-Specific DoD
  table; it now points at `definition-of-done.md`, which owns it.
- FlashMode's Recovery section listed three options with no rule for choosing. Size decides, as it
  does everywhere else: PatchMode-sized → PatchMode; bigger → a phase.
- FlashMode's "full structure" prose list is replaced by a pointer to the workflow table beneath it,
  which is complete (the list had forgotten the commit step).

**Migration**: none.

## 3.10.0

Fresh-eyes pass on the cycle files.

- **Cycle 040 no longer says "verify that most fail".** Every new test must fail, and for each the
  agent must be able to name the missing behavior; a test that passes against a stub is a bug in the
  test. "Most" let a test that checked nothing through unnoticed.
- **"Stub" is defined** (cycle 030): real signature, one-line docstring, body that raises the
  language's not-implemented error — no placeholder return values. Matches what 31 real
  SHORT_MEMORY.md files already do. `SHORT_MEMORY.md` is described the same way in 030 and 040: the
  stub list is the contract between 030, 040, and 050. Previously 040 called it a list of
  "sub-functions that need testing".
- **Cycle 010 asks each question once.** Single vs multi was asked in Step 0 and re-bucketed in Step 1
  with `< 10-15` / `> 10-15`, leaving 10-15 itself in neither; the naming theme was asked in Step 0 and
  again in Step 2.
- Cycle 020 and plan-file-best-practices.md no longer name Claude Code's Read and Edit tools — the
  same host-agnostic stance already taken for slash commands. Cycle 020's Important section stops
  repeating its own Purpose, and its See Also section (a copy of two routing-table rows) is gone.

**Migration**: none.

## 3.9.0

- **Bugs found in team validation (cycle 070) are now fixed in PatchMode** — failing test, fix,
  harden the diff. Previously 070 said only "fix bugs, no refactoring", so a validation bug was the
  least-rigorous code in the phase: no reproducing test, no hardening, and cycle 090's test run
  passed because nothing tested for it. Of 9 real SHORT_MEMORY.md files with a bug checklist, 3
  mentioned a test. The Phase DoD now requires a reproducing test per validation bug.
- The process rule in `overview.md` said cycles could "instruct you to go back to an earlier one".
  None ever did. It now says cycles run forward only; 060 is the one loop; 070 bugs are handled in
  place via PatchMode.
- A Task now has a checkable definition — names the file, the behavior, and how it is verified —
  with a good / vague / too-big example. The old text asked for "best practices" and "palatable"
  Tasks, which gave the agent nothing to test against.
- "the Human operator" → "the team" in the project-type section.

**Migration**: none.

## 3.8.1

- Cycle 060 described `/simplify` as "a Claude Code built-in". The docs distinguish built-in
  commands (`/help`, `/compact`) from bundled skills (`/debug`, `/code-review`, `/loop`);
  `/simplify` is the latter. Same correction applied to `/loop` in the
  code-refinement-with-hypothesis command.

**Migration**: none.

## 3.8.0

- FlashMode no longer restates cycles 020-100 in its own words. It is now a table of the standard
  cycles with a delta column saying what FlashMode changes — for most cycles, nothing. The cycle
  files are the single authority.
- This was not only a drift risk: the restatement had already silently dropped two requirements the
  cycles mandate — cycle 050's "capture aha moments" step and cycle 040's rule that unit tests never
  touch real infrastructure. Autonomous runs were following a lossy copy.
- FlashMode's checklist now defers to the Phase DoD in `definition-of-done.md`, keeping only the
  three items genuinely specific to autonomous execution.
- `definition-of-done.md`'s Phase DoD gained the two cycle obligations it had been missing: the
  cycle 060 hardening pass, and the cycle 090 BACKLOG sweep plus DECISIONS.md update. Cycles required
  both; the authoritative checklist did not list either.
- LightningMode's output expectations defer to the Project DoD for the same reason.

flash-mode.md: 215 -> 163 lines, with nothing lost.

**Migration**: none.

## 3.7.0

Consistency pass. Every finding below was two files disagreeing with each other.

- FlashMode still ordered `/simplify` and `/code-refinement-with-hypothesis` as bare commands, which
  3.4.0 had already stopped doing in cycle 060 and PatchMode. All four sites now frame them as
  accelerators for a review that is required either way.
- Cycle 100 gained the pre-commit hook check that FlashMode had been requiring of it all along.
- Cycle 080's title said "README.md Update"; the canonical cycle table said "README Update".
- `overview.md`'s list of critical files omitted `DETAILED_PLAN.md` and `RETRO.md`, both mandated by
  cycles and both shipped with templates in 3.5.0.
- FlashMode's "full structure" list named seven of the nine steps it runs, omitting the retrospective.
- The PLAN.md read threshold was specified in three places; cycle 020 now defers to
  `plan-file-best-practices.md`, which owns it.
- 27 more instructional first-person phrases rewritten to imperative across 11 files. Reflective "we"
  in retro and spec questions is deliberately kept — that is the team voice the skill asks for.

**Migration**: none.

## 3.6.0

Structural pass. No behavior changes to the cycles themselves.

- `overview.md` cut from 199 to ~127 lines. Directory trees moved to the new `references/file-layout.md`;
  the PLAN.md size strategy now points at `plan-file-best-practices.md`, which owns it.
- The "load overview.md first" mandate appeared three times in SKILL.md; it now appears once, and the
  document it points at is short enough for the instruction to be cheap.
- Phase-specific DoD table deduplicated — `definition-of-done.md` is the single owner; cycle 020
  points at it.
- Migration guides for v2.0→v2.1 and v2.1→v3.0 replaced by this CHANGELOG (243 lines → the tables
  that mattered).
- Project types are now operationalized uniformly: each states which cycles it skips or relaxes.
  Previously only `script` did.
- PatchMode's scratch `FIX.md` moves out of the repo root to a gitignored path — it was one
  `git add .` away from being committed.
- Cycle 070 no longer prescribes Postman specifically; any HTTP collection the project already uses.
- Remaining first-person voice removed from `overview.md`.

**Migration**: none.

## 3.5.0

- Added `assets/` — blank templates for all eight files the methodology creates (PLAN, DETAILED_PLAN,
  TEST_PLAN, SHORT_MEMORY, BACKLOG, RETRO, DECISIONS, PROJECTS). Each cycle now points at its template.
- RETRO template corrected to match observed practice: `## Plan adjustments`; dropped the line cap.
- FlashMode points at the templates directly, since it restates cycle steps rather than loading them.

**Migration**: none. New projects pick the templates up automatically; existing files are unaffected.

## 3.4.0

- Removed private context and first-person voice; the methodology now addresses "the team".
- Cycles 060 and PatchMode treat `/simplify` and `/code-refinement-with-hypothesis` as accelerators,
  not prerequisites — the review is required, the tooling is not.
- Fixed a stale cross-reference in FlashMode and a filename that had been wrong since 3.2.0
  (`PLAN_DETAILS.md` → `DETAILED_PLAN.md`).

**Migration**: none.

## 3.3.0

- Renamed QuickFixMode to PatchMode; added the harden steps to it.

**Migration**: none — the mode's file is `patch-mode.md`; update any local shortcut that referenced
the old name.

## 3.2.0

Driven by a scan of 54 real sessions where the process needed manual steering.

- New: QuickFixMode (now PatchMode), cycle 095 (Phase Retrospective), project completion, security
  pre-review in cycle 020, per-phase DoD, session resume protocol.
- Enhanced: cycle 060 gained the context-specific security review; cycle 090 made unit tests
  mandatory; FlashMode/LightningMode gained security, retros, and completion.

**Migration**: none required, but existing projects should start writing `RETRO.md` per phase and
`docs/DECISIONS.md` per cycle 090.

## 3.1.0

- Cycle 010 Step 0: decide single vs multi-project, and the naming theme, before any planning.
- FlashMode/LightningMode gained the "Go Fast, Never Cut Corners" rule.

**Migration**: none.

## 3.0.0

| Area | 2.1.0 | 3.0.0 |
|------|-------|-------|
| Directory | `project_docs/` | `docs/` |
| Cycle tracking | `<!-- Cycle: NNN -->` marker in PLAN.md | Agent task list, no file-based tracking |
| Cycle sequence | 13 cycles (010–130) | 10 cycles (010–100) — dropped Phase Selection, Linting/Refactoring, Pretty Code Commit; added Code Hardening |
| Spec versioning | `specs/version_1/`, `version_2/` folders | Flat files in `docs/specs/` with per-file TOML frontmatter |
| PROJECTS.md | Repository root | `docs/PROJECTS.md` |
| Decisions | `CLAUDE.md` (mixed with agent context) | `docs/DECISIONS.md` + `docs/planning/CLAUDE.md` |

**Migration**: rename `project_docs/` → `docs/`; move `PROJECTS.md` into it; strip `<!-- Cycle: -->`
markers from PLAN.md files; flatten spec version folders, keeping the latest of each spec at the
specs root and adding TOML frontmatter; split decisions out of `CLAUDE.md` into `docs/DECISIONS.md`.

## 2.1.0

| Area | 2.0.0 | 2.1.0 |
|------|-------|-------|
| Cross-project decisions | `DECISIONS.md` (optional, manual) | `CLAUDE.md` (auto-loaded) |
| Unscoped work | No defined location | `general/` sub-project |
| SKILL.md | Duplicated overview content | Routing document; defers to `overview.md` |
| Spec structure | Informal | Standard template with project-type guidance |
| Spec-to-phase tracing | No convention | `<!-- Spec: -->` comment in phase headers |

**Migration**: rename `DECISIONS.md` → `CLAUDE.md`; create a `general/` sub-project for unscoped
work and register it in PROJECTS.md; add `<!-- Spec: -->` comments to phase headers.

## 2.0.0 and earlier

Not documented here. See git history.
