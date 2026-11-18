# Your first project — a household budget

Five steps, about 10 minutes each. **Copy each prompt exactly** into Claude
Code, then compare what you get with *What you should see*.

Everything in `inbox/` is **invented**: the Okafor-Lane household, their bank,
their employer and their grocer are all made up, and every page says SAMPLE.
Practise on them. When you try this with your own money, use a **private**
copy and keep it off any public repository.

> **Stuck?** Every step's finished result is on the `finished` branch:
> `git checkout finished`. Nobody falls behind for good.

---

## Step 0 — Your own copy (5 min)

1. On this repository's GitHub page click **Use this template → Create a new
   repository**. Name it `household-budget`, choose **Private**, and create it.
2. On your new repository click **Code** and copy the URL.
3. In Cursor: **File → New Window → Clone repo**, paste the URL, and save it in
   **Documents**. Open it.
4. Open the terminal (**View → Terminal**) and type `claude`.
5. Inside Claude Code, check that GitHub knows who you are:

```
! gh auth status
```

If it says you are not logged in, run `! gh auth login`, choose
**GitHub.com → HTTPS → Login with a web browser**, and follow the code it
gives you. (If `gh` is not installed: `! brew install gh`.)

**What you should see:** `Logged in to github.com account <you>`.

---

## Step 1 — The rules: CLAUDE.md (10 min)

`CLAUDE.md` is read by Claude every time it starts in this folder. It is how
you stay in charge.

```
Write a CLAUDE.md for this folder. It's my household budget. It must tell you
to follow standards/brain-standard.md and standards/doe.md. Ask me 5 questions
first.
```

Answer its questions in your own words. Good rules to end up with:

- Never invent a number. If something isn't in a document, say so.
- All money arithmetic is done by a script, never in your head.
- Never commit a statement, pay stub or bill to git.
- Ask before moving or renaming files.

**What you should see:** a `CLAUDE.md` with your answers in it and the two
standards named. Type `/exit`, then `claude` again: it now starts with your
rules loaded.

---

## Step 2 — A brain and a documents folder (10 min)

```
Read standards/brain-standard.md. Set up brain/ and documents/ exactly as it
says. File everything in inbox/ into documents/ with standard names and a
sidecar for each, then write one brain note recording our eating-out budget
decision. Run the checklist at the end.
```

**What you should see:**

- `documents/` holds six PDFs with names like
  `2026-10-31-peach-state-bank-statement.pdf`, each with a `.json` beside it.
- `note-from-dana.txt` did **not** go to `documents/`. It is a note from a
  person, so what it decides became a brain note instead.
- `brain/eating-out-budget.md` starts with frontmatter and a `## Summary`.
- `inbox/` is empty, and the checklist is all ticks.

### Step 2b — The brain gets its own private GitHub repository

What you write deserves a history, and it should stay private even if the
project someday isn't.

```
Make brain/ its own git repository, commit what's in it, create a PRIVATE
GitHub repository for it called household-brain, and push it. Confirm it is
private before you push.
```

**What you should see:** a new repository on github.com/<you> with a
**Private** badge and your note in it. `brain/` is already in the project's
`.gitignore`, so the project never copies it.

---

## Step 3 — A skill (10 min)

A skill is a routine you write down once, so Claude runs it the same way
every time.

```
Read standards/doe.md. Build a skill called monthly-summary that follows it:
you read the statements in documents/ and put each transaction in a category
from budget.json; a script in scripts/ adds up totals against the budget and
prints JSON. Dry run by default. Show me the SKILL.md before you write the
script.
```

Read the `SKILL.md` it shows you; that is the **D**irective. Then type
`/exit` and `claude` to load the skill, and ask:

```
What did we spend in October, and are we over on eating out?
```

**What you should see:**

- Claude says it is using **monthly-summary**: it is the **O**rchestrator.
- It runs `total.py`: the **E**xecution. *Claude judged; the script added.*
- Eating out comes to **$520.20 against a $400 budget**.
- Bonus, if it noticed: **StreamFlix is charged twice** on the Visa
  ($14.99 on 10/02 and again on 10/12), which answers Dana's other question.

---

## Step 4 — A planning session (10 min)

Plan before you build. Press **Shift + Tab** until the bottom of the screen
says **plan mode**, then:

```
Plan what this project should do next: a monthly routine for filing
statements and checking the budget, and a savings goal for a $1,200 car repair
by March 1. Don't build anything. Write the plan to PLAN.md.
```

Read the plan. Push back on anything you don't like; it's yours. Approve it
when it's right.

### Step 4b — Turn the plan into milestones and issues

A plan in a file gets forgotten. Issues with due dates get done.

```
Turn PLAN.md into GitHub milestones and issues on this repository: one
milestone per phase with a due date, one issue per task, each issue in its
milestone. Show me the list before you create anything.
```

**What you should see:** on your repository's **Issues → Milestones** page,
two or three milestones (for example *December routine* and *Car fund by
March 1*), each with a handful of issues.

Then close the loop:

```
Close the issue for setting up the budget categories — that's done.
```

*Plan → issues → work → closed.*

---

## What you built

| | What | Why |
|---|---|---|
| `CLAUDE.md` | Your rules | Claude reads them every time |
| `brain/` | What you wrote, in its own private repository | Knowledge with a history |
| `documents/` | What you received, named and searchable | Evidence, kept out of git |
| `.claude/skills/monthly-summary/` | A routine, written down once | Claude judges, a script adds |
| `PLAN.md` + milestones and issues | What happens next | Planning on paper before code |

> *You wrote the rules, Claude filed the paper, a script did the math, and the
> plan was on paper before the code.*
