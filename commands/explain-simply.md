---
description: Boil the last response down to the one thing that must not be missed, in 2–3 short, plain, conversational sentences
version: 1.0.0
---

## Your task

Re-explain your most recent substantive response, or the topic the user names, for a reader who:

- **Knows the basics but isn't an expert.** They know what a database or an API is. They don't know the jargon, acronyms, or internal names you've been using.
- **Doesn't want to read.** Anything past a few sentences gets skimmed or skipped.
- **Can't afford a mistake.** They'll act on what you say exactly as written, so it has to be right and it can't leave out the thing that would trip them up.

If the user named a topic or focus, explain that instead of the last response: $ARGUMENTS

This is a one-shot command. After this reply, go back to your normal style.

### How to write it

1. **Find the one thing.** Ask yourself: if they remember only one point, which one keeps them from getting it wrong? That's the answer. It's often a decision, a constraint, or a warning, not the background.
2. **Say it in 2–3 sentences. That's the hard limit.** Put the most important point first. No intro, no recap, no "in short".
3. **Use everyday words.** Write it the way you'd say it out loud to a new teammate. Spell out or replace every acronym and piece of jargon. If you can't avoid a technical term, explain it in a few words right where you use it.
4. **Simple but still true.** Never simplify something into a statement that's wrong. If a shortcut would mislead them, keep the real detail and cut something else.
5. **Include the trap, if there is one.** If there's a step that's easy to get wrong, or an "unless...", and getting it wrong would hurt (data loss, a broken deploy, a wrong decision), that warning is part of the one thing. Give it one of your sentences.
6. **Be direct.** No hedging ("it's worth noting", "generally speaking"), no softening, no questions back at the end.

Format: plain prose only. No headers, no bullets, no tables, no code blocks, unless a single command or value is the whole point. If so, include it inline in backticks.

### What to leave out

- History and background ("we started by...")
- Alternatives you rejected, unless choosing between them is the point
- Every edge case except the one that would actually bite them
- Any offer to explain more. They'll ask if they want it.

### Example

Your last response was four paragraphs about migrating the user table: an online schema change with a shadow table, the backfill job, replication lag, and a cutover window.

Bad (accurate, but too long and full of jargon):

> We'll use an online DDL approach with a shadow table and dual writes, backfill via a throttled job to keep replica lag under the SLO, then do an atomic rename during a low-traffic cutover window...

Good:

> We're copying the user table into a new version in the background, so the site stays up while it happens. The one thing to watch: don't deploy any code that writes to the user table until the switch-over on Thursday night, or those writes can get lost.
