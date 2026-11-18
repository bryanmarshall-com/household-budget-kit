# DOE — how a skill is built in this project

**D**irective · **O**rchestration · **E**xecution. One page. Claude: follow
it whenever you build or change a skill.

## The idea in one line

> **Claude does not compute, and the scripts do not reason.**

Claude is good at judgement: *"is KROGER #412 groceries or eating out?"*
Claude is not a calculator, and a budget that is off by $40 because a model
added in its head is worse than no budget. So the work is split in three:

| Layer | What it is | Its job |
|---|---|---|
| **Directive** | `.claude/skills/<name>/SKILL.md` | The written routine: when to use the skill, the rules, which script to run. Read by you *and* Claude. |
| **Orchestration** | Claude Code | Reads the directive, reads the documents, makes the judgement calls, runs the script. |
| **Execution** | `.claude/skills/<name>/scripts/*.py` | The arithmetic and the file work. Same input, same answer, every time. Never "figures it out". |

**Worked example.** Claude reads the October statement and decides that
`OCONEE FRESH MARKET SAMPLE #12` is `groceries` and `MAIN STREET GRILL SAMPLE`
is `eating-out`, writing each decision into a JSON file. Then
`scripts/total.py` adds them up against `budget.json` and prints the totals.
*Claude judged; the script added.*

## What a skill looks like

```
.claude/skills/monthly-summary/
├── SKILL.md            the directive
└── scripts/
    └── total.py        the execution: math only, Python standard library only
```

Restart Claude Code (`/exit`, then `claude`) after creating a skill so it loads.

### `SKILL.md` skeleton — copy this

```markdown
---
name: <skill-name>
description: >
  One sentence on what this skill does. Then the exact phrases that should
  trigger it, e.g. "Use when asked 'what did we spend', 'are we over budget',
  'monthly summary', or /<skill-name>."
---

# <Skill Name>

You are the <role>. Your job is to <one-sentence mission>.

## Rules
- <A rule about the domain, e.g. a Visa payment from checking is a transfer, not spending.>
- <Another.>

## Steps
1. <Read …>
2. <Decide … and write the decisions to …json>
3. Run `python3 .claude/skills/<skill-name>/scripts/<script>.py <file>`.
4. Report using the script's numbers. **Never add numbers up yourself.**

## Scripts
| Script | Does | Changes files? |
|---|---|---|
| `scripts/<script>.py <file>` | <what it computes> | No |

## Safety
- Dry run by default. Anything that writes or changes a file needs `--confirm`.
- If a file it needs is missing, stop and say which. Never guess a number.
```

**The `description` is what makes Claude pick the skill.** Write it with the
words you will actually say. "Handles budget stuff" never triggers; "Use when
asked 'are we over budget'" does.

## Four rules every script follows

1. **Dry run by default.** A script that changes anything prints what it
   *would* do and stops. It acts only with `--confirm`.
2. **No silent fallbacks.** A missing file or an unknown category is an error
   that names what is missing. Never a zero, never a guess. A silent zero looks
   exactly like "we spent nothing".
3. **Rules live in data, not code.** Budget amounts and categories live in
   `budget.json`. Change the budget by editing that file, never the script.
4. **Scripts print JSON or a table**, not paragraphs. Claude turns it into
   sentences for you.

## Checklist — Claude, verify these when you're done

- [ ] `SKILL.md` has `name` and a `description` with real trigger phrases.
- [ ] Every number in the final answer came from a script's output.
- [ ] The script reads its rules from `budget.json`; no amounts are typed into the code.
- [ ] The script exits with an error, naming the problem, on a missing file or unknown category.
- [ ] The script uses only the Python standard library (it runs with `python3` on a fresh Mac).
- [ ] Run it once and show the output.
