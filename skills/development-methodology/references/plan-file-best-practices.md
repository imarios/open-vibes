# Working with a Large PLAN.md

`PLAN.md` is the central planning document, and for most projects reading it whole is the right thing to do — across real projects the median is under 200 lines, and even the largest observed (about 2,300 lines) fits comfortably in a modern context window. Do not ration reads of a file this size.

For a very large PLAN.md — past roughly 1,000 lines — read the section you need rather than the whole file:

```bash
grep -n "^## Phase" docs/planning/PLAN.md          # where each phase starts
grep -n "\[ \]" docs/planning/PLAN.md               # open tasks, with line numbers
```

Then read the line range of the phase you are working on, and make targeted edits to that range. Nothing else in the methodology depends on the file being small.

If PLAN.md is that large, the project is probably past the point where it should have been split — see `references/sub-project-structure.md`.
