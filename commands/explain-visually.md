---
description: Redraw the last response as a simple diagram so the decision or current state is easy to see at a glance
version: 1.0.0
---

## Your task

Take your most recent substantive response and the topic you're working on, and draw them. The reader thinks in pictures. A block of text describing options, flows, or how things fit together makes them hold it all in their head. A diagram lets them see it at once and decide faster.

If the user named a focus, draw only that part: $ARGUMENTS

If no focus was given, draw the main point of the last response. If that response covered several things, draw the one the user most needs to understand or decide on, and say in one line what you left out.

This is a one-shot command. After this reply, go back to your normal style.

### Step 1: Find the shape of the content

Before drawing, decide what kind of thing the last response was describing. Pick the diagram that matches that shape:

| The response was about...                       | Draw a...                                                      |
|-------------------------------------------------|----------------------------------------------------------------|
| A choice between options                        | Side-by-side comparison, with what each option costs and gives |
| A decision that depends on conditions           | Decision tree: questions at the branches, outcomes at the leaves |
| How data or a request moves through the system  | Flow diagram: boxes for components, arrows for what moves      |
| Who calls whom, in what order                   | Sequence diagram: one column per actor, time goes down         |
| How the parts are structured or depend on each other | Box-and-arrow diagram or tree                            |
| States and what moves between them              | State diagram                                                  |
| A change: how it is now vs. how it would be     | Before / after, side by side, with the differences marked      |
| Steps over time, or phases                      | Timeline                                                       |
| Trade-offs along two axes                       | 2×2 grid with each option placed in it                         |

If the content has two shapes (for example, how it works today *and* a choice about changing it), draw at most two diagrams, the current state first and then the choice.

### Step 2: Draw it

Choose how to render it:

- **If you have a tool that renders diagrams or visuals inline** (an SVG/HTML visualization tool, a canvas, an artifact viewer), use it. A real rendered diagram beats text art.
- **Otherwise**, draw it in a fenced code block with plain text and box-drawing characters (`┌ ─ ┐ │ └ ┘ ├ ┤ → ← ↓ ↑ ▼ ▶`). Keep it within 80 columns so it doesn't wrap in a terminal. Don't use Mermaid or other diagram source code unless you know the output will be rendered. Unrendered diagram code is not a picture.

Drawing rules:

1. **Use the same names as the response and the code.** If the response said `OrderService`, the box says `OrderService`. Don't rename things or invent labels.
2. **Draw only what's in the response.** Don't add new components, options, or facts. If drawing it shows a gap or a contradiction in what you said, point it out under the diagram instead of quietly fixing it.
3. **Keep it small.** Aim for at most ~12 boxes. Collapse the less important parts into one box ("auth + logging middleware") rather than drawing every detail.
4. **Label the arrows.** An arrow should say what moves or what triggers it (`HTTP POST`, `writes row`, `on timeout`). Leave a label off only when it's obvious.
5. **Make the important part stand out.** Mark the part that matters: the problem spot (`✗`), the recommended option (`★`), the thing that changes (`[NEW]`, `[REMOVED]`), or the open decision (`?`).
6. **For choices, show the trade-off right on the diagram.** Under each option, list 2–3 short pros (`+`) and cons (`−`). The reader should be able to compare options without reading anything else.

### Step 3: Add a short caption

Under the diagram, write at most 3–4 short lines:

- **How to read it**, but only if the notation isn't obvious.
- **The key takeaway** in one sentence: what the picture shows that the text made hard to see.
- **The decision**, if there is one: what the user needs to choose, and your recommendation if you made one.

Don't repeat the full explanation in prose. The diagram is the explanation.

### Example

Your last response was three paragraphs explaining whether to cache user profiles in Redis or in process memory. The command produces:

```
                 Where should user profiles be cached?
                                 │
              ┌──────────────────┴──────────────────┐
              ▼                                     ▼
   ┌──────────────────────┐           ┌──────────────────────┐
   │  In-process memory   │           │      Redis  ★        │
   ├──────────────────────┤           ├──────────────────────┤
   │ + no network hop     │           │ + shared by all pods │
   │ + nothing to run     │           │ + one place to evict │
   │ − each pod has its   │           │ − extra service to   │
   │   own copy           │           │   operate            │
   │ − stale after edits ✗│           │ − ~1ms per lookup    │
   └──────────────────────┘           └──────────────────────┘
```

**Takeaway:** with 6 pods, in-process caching means 6 copies that drift apart after a profile edit.
**Decision:** Redis (★), unless you're willing to accept up to 5 minutes of stale profiles.
