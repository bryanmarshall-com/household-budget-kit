#!/usr/bin/env python3
"""Render the invented household's paperwork into inbox/.

Every document here is INVENTED: the household, the employer, the bank, the
utility and the grocer are made up, and every page carries a SAMPLE watermark.
The transactions live in this file so the PDFs can be regenerated and checked.

    python3 _source/build.py            # dry run: print the totals it would render
    python3 _source/build.py --confirm  # write the PDFs into inbox/

Renders with headless Chrome (CSS watermark survives; LibreOffice's HTML import
drops it). Prints JSON.
"""
import json
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INBOX = ROOT / "inbox"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

HOUSEHOLD = "Dana & Sam Okafor-Lane"
ADDRESS = "1200 Example Lane, Milledgeville, GA 31061"

# (date, description, amount, category) — negative is money out.
# Category is the answer key for checking; it never appears on a statement.
CHECKING_OCT = [
    ("2026-10-01", "PINE STREET PROPERTIES SAMPLE RENT", -1450.00, "housing"),
    ("2026-10-01", "PAYROLL PINE RIDGE SCHOOL DISTRICT SAMPLE", 2184.62, "income"),
    ("2026-10-03", "OCONEE FRESH MARKET SAMPLE #12", -148.27, "groceries"),
    ("2026-10-04", "CHICK-FIL-A #0912", -23.86, "eating-out"),
    ("2026-10-05", "SHELL OIL 57410000", -46.20, "transportation"),
    ("2026-10-06", "CITY OF MILLEDGEVILLE WATER SAMPLE", -54.10, "utilities"),
    ("2026-10-07", "PEACH MUTUAL AUTO INS SAMPLE", -132.00, "insurance"),
    ("2026-10-08", "AMAZON MKTPLACE PMTS", -38.49, "shopping"),
    ("2026-10-09", "LA FIESTA MEXICAN RESTAURANT", -61.40, "eating-out"),
    ("2026-10-10", "RIVERBEND INTERNET SAMPLE", -65.00, "utilities"),
    ("2026-10-11", "OCONEE FRESH MARKET SAMPLE #12", -126.55, "groceries"),
    ("2026-10-12", "UNITED WAY OF MIDDLE GA SAMPLE", -50.00, "giving"),
    ("2026-10-13", "CVS/PHARMACY #05520", -27.18, "health"),
    ("2026-10-14", "TRANSFER TO SAVINGS xxxx0000", -300.00, "savings"),
    ("2026-10-15", "PAYROLL PINE RIDGE SCHOOL DISTRICT SAMPLE", 2184.62, "income"),
    ("2026-10-15", "PAYROLL RIVERSIDE FAMILY CLINIC SAMPLE", 1962.40, "income"),
    ("2026-10-16", "ZAXBY'S #44", -31.12, "eating-out"),
    ("2026-10-17", "WALMART SUPERCENTER #0601", -84.33, "groceries"),
    ("2026-10-18", "BUFFINGTON'S DOWNTOWN", -88.75, "eating-out"),
    ("2026-10-19", "SHELL OIL 57410000", -41.85, "transportation"),
    ("2026-10-20", "MAGNOLIA VISA SAMPLE ONLINE PMT", -612.38, "transfer"),
    ("2026-10-21", "MIDDLE GEORGIA ELECTRIC SAMPLE AUTOPAY", -168.43, "utilities"),
    ("2026-10-21", "OCONEE FRESH MARKET SAMPLE #12", -139.02, "groceries"),
    ("2026-10-22", "PLANET FITNESS CLUB FEES", -24.99, "health"),
    ("2026-10-24", "DUNKIN #3392", -9.47, "eating-out"),
    ("2026-10-25", "ATM WITHDRAWAL 0000 N COLUMBIA ST", -60.00, "misc"),
    ("2026-10-26", "MAIN STREET GRILL SAMPLE", -67.04, "eating-out"),
    ("2026-10-27", "OCONEE FRESH MARKET SAMPLE #12", -118.64, "groceries"),
    ("2026-10-28", "PATEL FAMILY DENTAL SAMPLE", -40.00, "health"),
    ("2026-10-29", "PAPA JOHN'S #1187", -32.18, "eating-out"),
    ("2026-10-30", "PAYROLL RIVERSIDE FAMILY CLINIC SAMPLE", 1962.40, "income"),
    ("2026-10-31", "PEACH MUTUAL RENTERS INS SAMPLE", -18.00, "insurance"),
]

CHECKING_SEP = [
    ("2026-09-01", "PINE STREET PROPERTIES SAMPLE RENT", -1450.00, "housing"),
    ("2026-09-01", "PAYROLL PINE RIDGE SCHOOL DISTRICT SAMPLE", 2184.62, "income"),
    ("2026-09-02", "OCONEE FRESH MARKET SAMPLE #12", -131.40, "groceries"),
    ("2026-09-05", "SHELL OIL 57410000", -44.10, "transportation"),
    ("2026-09-06", "CITY OF MILLEDGEVILLE WATER SAMPLE", -51.85, "utilities"),
    ("2026-09-07", "PEACH MUTUAL AUTO INS SAMPLE", -132.00, "insurance"),
    ("2026-09-08", "CHICK-FIL-A #0912", -21.40, "eating-out"),
    ("2026-09-10", "RIVERBEND INTERNET SAMPLE", -65.00, "utilities"),
    ("2026-09-12", "OCONEE FRESH MARKET SAMPLE #12", -142.18, "groceries"),
    ("2026-09-12", "UNITED WAY OF MIDDLE GA SAMPLE", -50.00, "giving"),
    ("2026-09-14", "TRANSFER TO SAVINGS xxxx0000", -300.00, "savings"),
    ("2026-09-15", "PAYROLL PINE RIDGE SCHOOL DISTRICT SAMPLE", 2184.62, "income"),
    ("2026-09-15", "PAYROLL RIVERSIDE FAMILY CLINIC SAMPLE", 1962.40, "income"),
    ("2026-09-17", "LA FIESTA MEXICAN RESTAURANT", -54.75, "eating-out"),
    ("2026-09-19", "SHELL OIL 57410000", -39.66, "transportation"),
    ("2026-09-20", "MAGNOLIA VISA SAMPLE ONLINE PMT", -488.12, "transfer"),
    ("2026-09-21", "MIDDLE GEORGIA ELECTRIC SAMPLE AUTOPAY", -192.77, "utilities"),
    ("2026-09-22", "OCONEE FRESH MARKET SAMPLE #12", -121.09, "groceries"),
    ("2026-09-22", "PLANET FITNESS CLUB FEES", -24.99, "health"),
    ("2026-09-26", "OCONEE FRESH MARKET SAMPLE #12", -109.33, "groceries"),
    ("2026-09-27", "BUFFINGTON'S DOWNTOWN", -76.20, "eating-out"),
    ("2026-09-30", "PAYROLL RIVERSIDE FAMILY CLINIC SAMPLE", 1962.40, "income"),
]

VISA_OCT = [
    ("2026-10-02", "STREAMFLIX*SAMPLE 855-555-0100", 14.99, "subscriptions"),
    ("2026-10-03", "SPOTIFY USA", 11.99, "subscriptions"),
    ("2026-10-06", "OLIVE GARDEN #1234", 72.45, "eating-out"),
    ("2026-10-09", "TARGET 00012345", 56.12, "shopping"),
    ("2026-10-12", "STREAMFLIX*SAMPLE 855-555-0100", 14.99, "subscriptions"),
    ("2026-10-14", "MOE'S SOUTHWEST GRILL", 28.40, "eating-out"),
    ("2026-10-17", "AUTOZONE #4410", 89.99, "transportation"),
    ("2026-10-19", "STARBUCKS STORE 10000", 12.65, "eating-out"),
    ("2026-10-22", "AMAZON MKTPLACE PMTS", 23.97, "shopping"),
    ("2026-10-23", "TACO BELL #0315", 18.73, "eating-out"),
    ("2026-10-26", "MAIN STREET GRILL SAMPLE", 64.30, "eating-out"),
    ("2026-10-28", "THE HOME DEPOT #0000", 47.88, "household"),
    ("2026-10-30", "STARBUCKS STORE 10000", 9.85, "eating-out"),
]
VISA_PREVIOUS = 612.38

RECEIPT = [  # Oconee Fresh Market, 2026-10-03; bank shows 148.27 = this + $5.00 cash back
    ("MILK 2% GAL", 3.89), ("EGGS LG 18CT", 5.49), ("BREAD WHOLE WHEAT", 3.29),
    ("CHICKEN THIGHS 3.2LB", 11.17), ("GROUND BEEF 2LB", 12.98), ("BANANAS 2.6LB", 1.66),
    ("APPLES GALA 3LB", 4.99), ("SPINACH 10OZ", 3.49), ("RICE JASMINE 5LB", 8.99),
    ("PASTA PENNE x3", 4.47), ("PASTA SAUCE x2", 5.98), ("CHEESE CHEDDAR 2LB", 9.49),
    ("YOGURT GREEK x6", 7.14), ("COFFEE GROUND 24OZ", 11.99), ("CEREAL x2", 8.58),
    ("PAPER TOWELS 6PK", 9.99), ("DISH SOAP", 3.49), ("LAUNDRY DET 92OZ", 13.99),
    ("FROZEN PIZZA x2", 12.20),
]

PAYSTUB = {
    "employer": "Pine Ridge School District SAMPLE",
    "employee": "Dana Okafor-Lane", "id": "E-000000", "pay_date": "2026-10-15",
    "period": "2026-10-01 to 2026-10-15", "gross": 2916.67,
    "deductions": [("Federal income tax", 168.40), ("Georgia income tax", 110.00),
                   ("Social Security (6.2%)", 180.83), ("Medicare (1.45%)", 42.29),
                   ("TRS retirement (6%)", 175.00), ("Health insurance", 55.53)],
}

ELECTRIC = {"bill_date": "2026-10-01", "due": "2026-10-21", "kwh": 1214,
            "period": "2026-08-29 to 2026-09-29", "previous": 192.77,
            "charges": [("Basic service charge", 14.00), ("Energy 1,214 kWh", 131.70),
                        ("Fuel recovery", 15.31), ("Taxes & fees", 7.42)]}

CSS = """
@page { size: letter; margin: 0.6in; }
body { font-family: Helvetica, Arial, sans-serif; font-size: 10.5pt; color: #222; }
.wm { position: fixed; top: 40%; left: -5%; width: 110%; text-align: center;
      transform: rotate(-30deg); font-size: 54pt; font-weight: bold;
      color: rgba(200,0,0,0.13); z-index: 9; }
.top { display: flex; justify-content: space-between; border-bottom: 3px solid VAR;
       padding-bottom: 8px; margin-bottom: 14px; }
.brand { font-size: 20pt; font-weight: bold; color: VAR; }
.small { font-size: 8.5pt; color: #666; }
table { width: 100%; border-collapse: collapse; margin-top: 8px; }
th { text-align: left; background: #f0f0f0; padding: 5px; font-size: 9pt; }
td { padding: 4px 5px; border-bottom: 1px solid #eee; }
td.n, th.n { text-align: right; font-variant-numeric: tabular-nums; }
.box { border: 1px solid #ccc; padding: 10px; margin: 10px 0; }
.foot { margin-top: 18px; font-size: 8pt; color: #888; }
"""


def money(x):
    return f"-${abs(x):,.2f}" if x < 0 else f"${x:,.2f}"


def page(title, color, body):
    return (f"<!doctype html><html><head><meta charset='utf-8'><title>{title}</title>"
            f"<style>{CSS.replace('VAR', color)}</style></head><body>"
            f"<div class='wm'>SAMPLE — INVENTED DATA</div>{body}"
            "<div class='foot'>This document is invented for a training exercise. "
            "No real person, account or institution is represented.</div></body></html>")


def statement(month_label, period, rows, opening):
    bal, trs = opening, []
    for d, desc, amt, _ in rows:
        bal = round(bal + amt, 2)
        trs.append(f"<tr><td>{d[5:]}</td><td>{desc}</td>"
                   f"<td class='n'>{money(amt) if amt < 0 else ''}</td>"
                   f"<td class='n'>{money(amt) if amt > 0 else ''}</td>"
                   f"<td class='n'>{money(bal)}</td></tr>")
    dep = sum(a for *_x, a, _c in [(r[0], r[1], r[2], r[3]) for r in rows] if a > 0)
    wd = sum(r[2] for r in rows if r[2] < 0)
    body = f"""
<div class='top'><div><div class='brand'>Peach State Bank SAMPLE</div>
<div class='small'>PO Box 0000 · Macon, GA 31201 · 478-555-0100</div></div>
<div style='text-align:right'><b>Checking Statement</b><br>{month_label}<br>
<span class='small'>Account ****0000</span></div></div>
<div>{HOUSEHOLD}<br>{ADDRESS}</div>
<div class='box'><b>Statement period:</b> {period}<br>
Opening balance {money(opening)} · Deposits {money(dep)} · Withdrawals {money(wd)} ·
<b>Closing balance {money(bal)}</b></div>
<table><tr><th>Date</th><th>Description</th><th class='n'>Withdrawals</th>
<th class='n'>Deposits</th><th class='n'>Balance</th></tr>{''.join(trs)}</table>"""
    return page(f"Peach State Bank SAMPLE {month_label}", "#c0561b", body), bal


def visa():
    new = round(sum(r[2] for r in VISA_OCT), 2)
    trs = "".join(f"<tr><td>{d[5:]}</td><td>{desc}</td><td class='n'>{money(a)}</td></tr>"
                  for d, desc, a, _ in VISA_OCT)
    body = f"""
<div class='top'><div><div class='brand'>Magnolia Visa SAMPLE</div>
<div class='small'>Customer service 800-555-0199</div></div>
<div style='text-align:right'><b>Monthly Statement</b><br>October 2026<br>
<span class='small'>Card ending 0000</span></div></div>
<div>{HOUSEHOLD}<br>{ADDRESS}</div>
<div class='box'><b>Billing period:</b> 2026-10-01 to 2026-10-31<br>
Previous balance {money(VISA_PREVIOUS)} · Payment received 10/20 {money(-VISA_PREVIOUS)} ·
New purchases {money(new)}<br><b>New balance {money(new)}</b> · Minimum due $35.00 ·
Payment due 2026-11-20</div>
<table><tr><th>Date</th><th>Description</th><th class='n'>Amount</th></tr>
<tr><td>10-20</td><td>PAYMENT - THANK YOU</td><td class='n'>{money(-VISA_PREVIOUS)}</td></tr>
{trs}</table>"""
    return page("Magnolia Visa SAMPLE October 2026", "#5b2a86", body), new


def paystub():
    p = PAYSTUB
    ded = round(sum(a for _, a in p["deductions"]), 2)
    net = round(p["gross"] - ded, 2)
    rows = "".join(f"<tr><td>{n}</td><td class='n'>{money(a)}</td></tr>" for n, a in p["deductions"])
    body = f"""
<div class='top'><div><div class='brand'>{p['employer']}</div>
<div class='small'>Payroll Office · 478-555-0142</div></div>
<div style='text-align:right'><b>Earnings Statement</b><br>Pay date {p['pay_date']}</div></div>
<div class='box'>Employee: <b>{p['employee']}</b> ({p['id']}) · Position: Teacher, Grade 4<br>
Pay period: {p['period']} · Paid twice monthly</div>
<table><tr><th>Earnings</th><th class='n'>Amount</th></tr>
<tr><td>Regular salary</td><td class='n'>{money(p['gross'])}</td></tr></table>
<table><tr><th>Deductions</th><th class='n'>Amount</th></tr>{rows}
<tr><td><b>Total deductions</b></td><td class='n'><b>{money(ded)}</b></td></tr></table>
<div class='box'><b>Net pay {money(net)}</b> — direct deposit to Peach State Bank SAMPLE ****0000</div>"""
    return page("Earnings statement SAMPLE", "#1d5f8a", body), net


def electric():
    e = ELECTRIC
    total = round(sum(a for _, a in e["charges"]), 2)
    rows = "".join(f"<tr><td>{n}</td><td class='n'>{money(a)}</td></tr>" for n, a in e["charges"])
    body = f"""
<div class='top'><div><div class='brand'>Middle Georgia Electric SAMPLE</div>
<div class='small'>Member services 478-555-0177</div></div>
<div style='text-align:right'><b>Electric Bill</b><br>Bill date {e['bill_date']}<br>
<span class='small'>Account 0000-0000</span></div></div>
<div>{HOUSEHOLD}<br>{ADDRESS}</div>
<div class='box'>Service period {e['period']} · Usage <b>{e['kwh']:,} kWh</b><br>
Previous bill {money(e['previous'])} — paid, thank you.</div>
<table><tr><th>Charges</th><th class='n'>Amount</th></tr>{rows}
<tr><td><b>Amount due</b></td><td class='n'><b>{money(total)}</b></td></tr></table>
<div class='box'><b>Due {e['due']}</b> · Enrolled in AutoPay from Peach State Bank SAMPLE ****0000</div>"""
    return page("Middle Georgia Electric SAMPLE bill", "#2f7d32", body), total


def receipt():
    sub = round(sum(a for _, a in RECEIPT), 2)
    rows = "".join(f"<tr><td>{n}</td><td class='n'>{a:.2f}</td></tr>" for n, a in RECEIPT)
    body = f"""
<div style='width:3.4in;margin:0 auto;font-family:Courier,monospace'>
<div style='text-align:center'><b>OCONEE FRESH MARKET SAMPLE</b><br>STORE #12 · MILLEDGEVILLE GA<br>
478-555-0123<br>10/03/2026 5:42 PM</div>
<table>{rows}</table>
<table><tr><td><b>TOTAL</b></td><td class='n'><b>{sub:.2f}</b></td></tr>
<tr><td>CASH BACK</td><td class='n'>5.00</td></tr>
<tr><td>DEBIT CARD ****0000</td><td class='n'>{sub + 5:.2f}</td></tr></table>
<div style='text-align:center'>THANK YOU FOR SHOPPING<br>ITEMS SOLD {len(RECEIPT)}</div></div>"""
    return page("Receipt SAMPLE", "#444", body), sub


NOTE = """Sam —

Back in August we said $400 a month on eating out, tops. I have a feeling
October blew past that. Can you check before we decide on the car repair
money? The mechanic quoted $1,200 for the transmission work and said it can
wait until March, but not much longer.

Also, are we paying for StreamFlix twice? I thought we cancelled the old one.

— D.
"""

# messy, download-style names: naming them to the standard is part of step 2
OUTPUTS = {
    "eStatement_Sep2026.pdf": "sep",
    "eStatement_Oct2026 (1).pdf": "oct",
    "MagnoliaVisa_Statement.pdf": "visa",
    "paystub.pdf": "stub",
    "electric bill.pdf": "electric",
    "IMG_0412 receipt.pdf": "receipt",
}


def render(html, out):
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "doc.html"
        src.write_text(html, encoding="utf-8")
        r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                            f"--user-data-dir={tmp}/profile", f"--print-to-pdf={out}", src.as_uri()],
                           capture_output=True, text=True, timeout=120)
        if r.returncode != 0 or not out.exists():
            sys.exit(json.dumps({"error": f"chrome failed for {out.name}", "stderr": r.stderr[-500:]}))


def main():
    confirm = "--confirm" in sys.argv
    sep_html, sep_close = statement("September 2026", "2026-09-01 to 2026-09-30", CHECKING_SEP, 1104.55)
    oct_html, oct_close = statement("October 2026", "2026-10-01 to 2026-10-31", CHECKING_OCT, sep_close)
    docs = {"sep": sep_html, "oct": oct_html, "visa": visa()[0], "stub": paystub()[0],
            "electric": electric()[0], "receipt": receipt()[0]}

    by_cat = defaultdict(float)
    for _d, _desc, amt, cat in CHECKING_OCT:
        by_cat[cat] += -amt
    for _d, _desc, amt, cat in VISA_OCT:
        by_cat[cat] += amt
    report = {
        "october_spending_by_category": {k: round(v, 2) for k, v in sorted(by_cat.items())},
        "checks": {
            "paystub_net_equals_deposit": paystub()[1] == 2184.62,
            "electric_due_equals_autopay": electric()[1] == 168.43,
            "receipt_plus_cashback_equals_bank": round(receipt()[1] + 5, 2) == 148.27,
            "september_close_feeds_october": True,
        },
        "closing_balances": {"sep": sep_close, "oct": oct_close},
        "would_write" if not confirm else "wrote": list(OUTPUTS) + ["note-from-dana.txt"],
    }
    if confirm:
        INBOX.mkdir(exist_ok=True)
        for name, key in OUTPUTS.items():
            render(docs[key], INBOX / name)
        (INBOX / "note-from-dana.txt").write_text(NOTE, encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not all(report["checks"].values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
