# The brain standard — household edition

How this project keeps what you **write** and what you **receive**. One page,
on purpose. Claude: follow it exactly, and run the checklist at the bottom when
you finish.

## The whole system is two sentences

> **If you wrote it, it is markdown in `brain/`, and it is in git.**
> **If you received it, it is a document in `documents/` with a `.json` beside it, and it is not in git.**

A bank statement was *received*: it goes in `documents/`. "We agreed on $400 a
month for eating out" was *decided by you*: it is a note in `brain/`.

## `brain/` — what you wrote

- **Flat.** Every note is `brain/<id>.md`. No subfolders.
- **The filename is the id**: lowercase, words joined by dashes, descriptive
  on its own. Good: `eating-out-budget.md`. Bad: `notes.md`, `budget/2026/oct.md`.
- **`type:` is the only way notes are sorted**, from this short list:
  `decision` · `goal` · `task` · `note`.
- **Every note starts with frontmatter and then a `## Summary`**, one or two
  sentences that say the point, not the topic:

```markdown
---
id: eating-out-budget
title: Eating-out budget is $400 a month
type: decision
status: current            # current | done | superseded
updated: 2026-11-18
authority: documents/2026-10-31-peach-state-bank-statement.pdf   # optional: what it rests on
---

# Eating-out budget is $400 a month

## Summary
> We agreed in August 2026 to spend at most $400 a month eating out. October came to $520.20, so we are over.

Body text, as long as it needs to be. Link other notes with [[car-repair-fund]].
```

- `[[id]]` links point at the file whose name is `id`.
- A `task` has a `due:` date. Finished things get `status: done`; **nothing is deleted.**
- `brain/README.md` is the index: one line per note, with its summary.

## `documents/` — what you received

- **Flat.** Each document is stored as the **untouched original**, named:

```
YYYY-MM-DD-<issuer>-<type>.pdf          2026-10-31-peach-state-bank-statement.pdf
YYYY-MM-DD-<issuer>-<type>.json         its sidecar, same name, right beside it
```

- **date** is the document's *own* date (statement end, pay date, bill date),
  never the day you downloaded it.
- **issuer** is who sent it, lowercase-dashed: `peach-state-bank`,
  `magnolia-visa`, `pine-ridge-school-district`, `middle-georgia-electric`,
  `oconee-fresh-market`.
- **type** is one word, no dashes: `statement`, `paystub`, `bill`, `receipt`.
- Two documents that would share a name get `-2` on the second. Never overwrite.

### The sidecar

The `.json` beside each document. It makes the document searchable and says
why it is worth keeping:

```json
{
  "source": "documents/2026-10-31-peach-state-bank-statement.pdf",
  "original_name": "eStatement_Oct2026 (1).pdf",
  "sha256": "<from: shasum -a 256 the-file>",
  "received": "2026-11-18",
  "purpose": "October checking activity for the monthly budget",
  "why_kept": "Evidence for the October spending totals",
  "text": ["line one of the page", "line two", "..."]
}
```

`text` is the document's own words, copied out of the PDF, one line per line.
**Never write a sidecar with empty text**; if a PDF has no text, say so.

## The keep test — does it belong at all?

Every incoming item is exactly one of:

- **Brain**: knowledge you will act on. Write a note.
- **Evidence**: proof you may need to show. File it in `documents/`.
- **Neither**: duplicates, drafts, junk mail. **This is the default.** The
  other two need a reason.

A handwritten or emailed note *from someone* is usually not evidence. Pull
out what it decides or asks, and write that as a brain note.

## Never

- Never put `documents/` in git (the project's `.gitignore` already blocks it).
- Never put a password, account login or full account number anywhere.
- Never change the original document. Rename it; do not edit it.

## Checklist — Claude, verify these when you're done

- [ ] Every file in `documents/` has a `.json` with the same name beside it.
- [ ] Every document name matches `YYYY-MM-DD-issuer-type.pdf`.
- [ ] Every sidecar's `text` is non-empty and its `sha256` matches `shasum -a 256`.
- [ ] Every note in `brain/` has `id` equal to its filename and a `## Summary`.
- [ ] `inbox/` is empty, and each item it held is accounted for (brain, documents, or neither — say which).
- [ ] `git status` in the project shows nothing under `documents/`.
