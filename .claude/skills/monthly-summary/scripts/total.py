#!/usr/bin/env python3
"""Total one month's categorized transactions against budget.json.

The arithmetic half of the monthly-summary skill. Claude decides each
transaction's category and writes drafts/<month>.json; this script does the
adding up, so no total is ever a model's mental arithmetic.

    python3 .claude/skills/monthly-summary/scripts/total.py drafts/2026-10.json

Read-only: changes no files. Prints JSON. Exits 1, naming the problem, on a
missing file, an unknown category or a malformed transaction. The same
description and amount twice in one month is reported as a possible duplicate.
"""
import json
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BUDGET = ROOT / "budget.json"


def fail(msg):
    print(json.dumps({"error": msg}))
    sys.exit(1)


def load(path):
    if not path.is_file():
        fail(f"file not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(f"{path} is not valid JSON: {e}")


def main():
    if len(sys.argv) != 2:
        fail("usage: total.py drafts/<YYYY-MM>.json")
    budget = load(BUDGET)
    limits = {k: Decimal(str(v)) for k, v in budget["monthly_budget"].items()}
    ignored = set(budget["not_spending"])
    draft = load(Path(sys.argv[1]))
    txns = draft.get("transactions")
    if not txns:
        fail("no transactions in the draft")

    spent = defaultdict(Decimal)
    seen = defaultdict(list)
    for i, t in enumerate(txns, 1):
        for field in ("date", "description", "amount", "category"):
            if field not in t:
                fail(f"transaction {i} has no '{field}'")
        cat = t["category"]
        if cat not in limits and cat not in ignored:
            fail(f"transaction {i} ({t['description']}): unknown category '{cat}'")
        amt = Decimal(str(t["amount"]))
        if cat in ignored:
            continue
        spent[cat] += amt
        seen[(t["description"], amt)].append(t["date"])

    by_cat = {}
    for cat, limit in limits.items():
        s = spent.get(cat, Decimal(0))
        by_cat[cat] = {"spent": float(s), "budget": float(limit),
                       "left": float(limit - s), "over": s > limit}
    total = sum(spent.values(), Decimal(0))
    print(json.dumps({
        "month": draft.get("month"),
        "transactions_counted": sum(len(v) for v in seen.values()),
        "total_spent": float(total),
        "total_budget": float(sum(limits.values(), Decimal(0))),
        "over_budget": [c for c, v in by_cat.items() if v["over"]],
        "by_category": by_cat,
        "possible_duplicates": [{"description": d, "amount": float(a), "dates": ds}
                                for (d, a), ds in seen.items()
                                if len(ds) > 1],
    }, indent=2))


if __name__ == "__main__":
    main()
