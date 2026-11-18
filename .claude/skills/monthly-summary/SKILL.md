---
name: monthly-summary
description: >
  Total a month's household spending by category against budget.json, from the
  statements in documents/. Use when asked "what did we spend", "are we over
  budget", "are we over on eating out", "monthly summary", "how did October
  go", or /monthly-summary.
---

# Monthly Summary

You are the household's bookkeeper. Your job is to put every transaction for
one month into a category, then let a script do all the arithmetic.

## Rules

- Categories come from `budget.json` (`monthly_budget` keys, plus
  `not_spending`). **Never invent a category.** If nothing fits, use `misc`
  and say so.
- **Paying the Visa from checking is a `transfer`**, not spending. The Visa
  statement shows what was actually bought; counting both would double it.
- Paychecks are `income`. Moving money to savings is `savings`.
- Read the **sidecar** (`documents/*.json`, its `text`) rather than the PDF.
  Use the checking statement and the Visa statement for the month.
- A receipt explains a transaction; it is not a second transaction.

## Steps

1. Find the month's checking and Visa sidecars in `documents/`.
2. For each transaction, decide its category. Write them all to
   `drafts/<YYYY-MM>.json`:
   ```json
   {"month": "2026-10",
    "transactions": [
      {"date": "2026-10-04", "description": "CHICK-FIL-A #0912",
       "amount": 23.86, "category": "eating-out",
       "source": "documents/2026-10-31-peach-state-bank-statement.json"}]}
   ```
   `amount` is **positive for money out**, negative for money in. Copy the
   amounts exactly as printed.
3. Run:
   ```bash
   python3 .claude/skills/monthly-summary/scripts/total.py drafts/2026-10.json
   ```
4. Report from the script's JSON: total spent, each category against its
   budget, which are over, and any `possible_duplicates`. **Never add numbers
   up yourself.** If the script errors, fix the JSON and run it again.

## Scripts

| Script | Does | Changes files? |
|---|---|---|
| `scripts/total.py <drafts/month.json>` | Totals by category against `budget.json`, flags over-budget and duplicate charges, prints JSON | No |

## Safety

- The script is read-only. The only file this skill writes is `drafts/<month>.json`.
- A missing file or unknown category is an error. Do not guess past it.
- Never move money, pay a bill or contact anyone.
