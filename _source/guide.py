#!/usr/bin/env python3
"""Build GUIDE.pdf: the step-by-step guide to the household budget project.

    python3 _source/guide.py <finished-checkout> <dryrun-dir>            # dry run: list inputs
    python3 _source/guide.py <finished-checkout> <dryrun-dir> --confirm  # write GUIDE.pdf

<finished-checkout> is a checkout of the `finished` branch (the real files the
editor panes show). <dryrun-dir> holds what the 2026-11-18 dry run produced:
answer.txt (a headless claude -p reply), total.json (total.py output),
issues.tsv (from the dry-run repo) and img/*.png (real GitHub screenshots).

Cursor and Claude Code screens are DRAWN, and say so. No pane shows output
that was not produced by a real run; prompts are the ones in STEPS.md.
"""
import base64
import html
import json
import subprocess
import sys
import tempfile
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
REPO = "github.com/bryanmarshall-com/household-budget-kit"


def esc(s):
    return html.escape(s)


def img(path):
    return "data:image/png;base64," + base64.b64encode(Path(path).read_bytes()).decode()


def tree(items, active=None):
    out = []
    for depth, name, kind in items:
        cls = "act" if name == active else ""
        icon = "▾" if kind == "dir" else "·"
        out.append(f"<div class='ti {cls}' style='padding-left:{8 + depth * 12}px'>"
                   f"<span class='tic'>{icon}</span>{esc(name)}</div>")
    return "".join(out)


def screen(caption, items, active, editor, term, mode=None, num=None):
    """A drawn Cursor window: explorer, an editor tab, and Claude Code in the terminal."""
    tab = f"<div class='tab'>{esc(active)}</div>" if active else "<div class='tab dim'>no file open</div>"
    status = (f"<div class='ccmode'>⏸ {esc(mode)}</div>" if mode else
              "<div class='ccmode dim'>? for shortcuts</div>")
    return f"""
<figure class='shot'>
 <div class='win'>
  <div class='bar'><span class='d r'></span><span class='d y'></span><span class='d g'></span>
   <span class='wt'>household-budget — Cursor</span></div>
  <div class='body'>
   <div class='side'><div class='sh'>EXPLORER</div>{tree(items, active)}</div>
   <div class='main'>
    <div class='tabs'>{tab}</div>
    <pre class='ed'>{editor}</pre>
    <div class='term'><div class='th'>TERMINAL</div><div class='tb'>{term}</div>{status}</div>
   </div>
  </div>
 </div>
 <figcaption>{('<b>Figure ' + str(num) + '.</b> ') if num else ''}{caption}
 <span class='drawn'>Drawn screen; contents are from a real run.</span></figcaption>
</figure>"""


def prompt_box(text):
    return f"<div class='pbox'><span class='gt'>&gt;</span> {esc(text)}</div>"


def tool(name, arg, out=None):
    o = f"<div class='tout'>⎿ {esc(out)}</div>" if out else ""
    return f"<div class='tool'><span class='dot'>⏺</span> <b>{esc(name)}</b>({esc(arg)}){o}</div>"


def reply(text):
    return "<div class='reply'><span class='dot w'>⏺</span> " + esc(text).replace("\n", "<br>") + "</div>"


def copybox(text):
    return f"<div class='copy'><div class='cl'>Type or paste into Claude Code</div><pre>{esc(text)}</pre></div>"


def first_lines(path, n):
    return esc("\n".join(Path(path).read_text(encoding="utf-8").splitlines()[:n]))


def build(fin, dry):
    fin, dry = Path(fin), Path(dry)
    answer = (dry / "answer.txt").read_text(encoding="utf-8").split("\nexit ")[0].strip().replace("**", "")
    total = json.loads((dry / "total.json").read_text())
    issues = [l.split("\t") for l in (dry / "issues.tsv").read_text().strip().splitlines()]
    docs = sorted(p.name for p in (fin / "documents").iterdir())
    brain = sorted(p.name for p in (fin / "brain").iterdir())

    base = [(0, ".claude", "dir"), (0, "_source", "dir"), (0, "inbox", "dir"),
            (1, "eStatement_Oct2026 (1).pdf", "f"), (1, "paystub.pdf", "f"), (1, "…", "f"),
            (0, "standards", "dir"), (1, "brain-standard.md", "f"), (1, "doe.md", "f"),
            (0, "budget.json", "f"), (0, "CLAUDE.md", "f"), (0, "README.md", "f"), (0, "STEPS.md", "f")]
    after2 = ([(0, "brain", "dir")] + [(1, b, "f") for b in brain] + [(0, "documents", "dir")] +
              [(1, d, "f") for d in docs] + [(0, "inbox", "dir"), (0, "standards", "dir"),
              (0, "budget.json", "f"), (0, "CLAUDE.md", "f")])
    after3 = ([(0, ".claude", "dir"), (1, "skills", "dir"), (2, "monthly-summary", "dir"),
               (3, "SKILL.md", "f"), (3, "scripts", "dir"), (4, "total.py", "f"),
               (0, "brain", "dir"), (0, "documents", "dir"), (0, "drafts", "dir"), (1, "2026-10.json", "f"),
               (0, "standards", "dir"), (0, "budget.json", "f"), (0, "CLAUDE.md", "f"), (0, "PLAN.md", "f")])

    eo = total["by_category"]["eating-out"]
    dup = total["possible_duplicates"][0]
    total_lines = esc(json.dumps({"month": total["month"], "total_spent": total["total_spent"],
                                  "over_budget": total["over_budget"],
                                  "by_category": {"eating-out": eo, "…": "…"},
                                  "possible_duplicates": total["possible_duplicates"]}, indent=2, ensure_ascii=False))

    ms = {}
    for num, state, title, milestone in issues:
        ms.setdefault(milestone, []).append((num, state, title))
    ms_html = ""
    for name, due in (("December routine", "Due by December 5, 2026"), ("Car fund by March 1", "Due by March 1, 2027")):
        rows = "".join(f"<div class='iss {'closed' if s == 'closed' else ''}'><span class='ico'>{'✓' if s == 'closed' else '◯'}</span>"
                       f"{esc(t)} <span class='num'>#{n}</span></div>" for n, s, t in sorted(ms[name], key=lambda r: int(r[0])))
        closed = sum(1 for _, s, _ in ms[name] if s == "closed")
        pct = round(100 * closed / len(ms[name]))
        ms_html += (f"<div class='ms'><div class='mh'><b>{esc(name)}</b><span>{due}</span></div>"
                    f"<div class='prog'><div style='width:{max(pct, 1)}%'></div></div>"
                    f"<div class='small'>{pct}% complete · {len(ms[name]) - closed} open · {closed} closed</div>{rows}</div>")

    sidecar = json.loads((fin / "documents" / "2026-10-31-peach-state-bank-statement.json").read_text())
    sidecar["sha256"] = sidecar["sha256"][:16] + "…"
    sidecar["text"] = sidecar["text"][:4] + ["…"]
    sidecar_s = esc(json.dumps(sidecar, indent=2, ensure_ascii=False))

    fig = iter(range(1, 50))
    P = []  # pages / sections

    P.append(f"""
<section class='cover'>
 <div class='kicker'>AI Snack &amp; Learn · Georgia College · 18 November 2026</div>
 <h1>Your First Project:<br>a Household Budget</h1>
 <p class='lede'>A step-by-step guide to building a small, real project with <b>Cursor</b> and
 <b>Claude Code</b>: rules for the assistant, a place for what you write and what you receive,
 a skill that does the arithmetic, and a plan turned into GitHub milestones and issues.</p>
 <table class='facts'>
  <tr><th>Time</th><td>About 60 minutes</td></tr>
  <tr><th>You need</th><td>Cursor, Claude Code signed in to a paid Claude plan, a GitHub account</td></tr>
  <tr><th>Kit</th><td><b>{REPO}</b></td></tr>
  <tr><th>Stuck?</th><td>The end state of every step: <b>{REPO}/tree/finished</b></td></tr>
 </table>
 <div class='note'><b>About the pictures.</b> GitHub pages are real screenshots. Cursor and Claude Code
 screens are <i>drawn</i>, but what is inside them is real: the prompts are the ones you will type,
 and the files, answers and numbers come from a full run of this exercise on the morning of
 18 November 2026. Your Claude will word things differently. That is normal.</div>
 <div class='note warn'><b>Everything in the kit is invented.</b> The Okafor-Lane household, their bank,
 employers, utility and grocer are made up, and every page is stamped SAMPLE. Practise on them. When
 you try this with your own money, use a <b>private</b> copy and keep the documents out of git.</div>
</section>""")

    P.append(f"""
<section>
<h2>Before you start: five things to know about Claude Code</h2>
<p>Claude Code runs in Cursor's terminal panel. You type in plain English; it reads files, writes
files and runs commands in your project folder, asking permission first for anything that changes
something.</p>
<table class='keys'>
 <tr><th>Do this</th><th>To</th></tr>
 <tr><td><kbd>Enter</kbd></td><td>Send your message.</td></tr>
 <tr><td><kbd>Esc</kbd></td><td>Stop Claude mid-task. Nothing is lost; you can redirect it.</td></tr>
 <tr><td><kbd>Shift</kbd> + <kbd>Tab</kbd></td><td>Cycle modes: normal → <b>accept edits</b> → <b>plan mode</b>. The current mode shows
 under the input box. Step 4 uses plan mode.</td></tr>
 <tr><td><code>/exit</code> then <code>claude</code></td><td>Restart Claude Code. Needed after writing CLAUDE.md or a new skill, so it loads them.</td></tr>
 <tr><td><code>! command</code></td><td>Run a terminal command yourself, from inside Claude Code (for example <code>! gh auth status</code>).</td></tr>
</table>
<h3>Permission prompts</h3>
<p>When Claude wants to create a file or run a command, it stops and asks. You will see choices like
<b>1. Yes</b>, <b>2. Yes, and don't ask again</b> for this kind of action, and <b>3. No, and tell Claude what to do
differently</b>. <b>Read what it is about to do before you press 1.</b> That moment is where you stay in
charge. Choosing 2 for routine things (editing files in this folder) keeps the session moving.</p>
<h3>Windows</h3>
<p>On Windows, Claude Code runs inside WSL (Ubuntu). Open the project with Cursor's WSL connection
(bottom-left corner → <i>Connect to WSL</i>) so the terminal is a Linux one. The install steps are in the
Snack &amp; Learn kit's <b>INSTALL.md</b> (github.com/bryanmarshall-com/snack-learn-kit).</p>
<h3>The five steps</h3>
<ol class='overview'>
 <li><b>Step 0 · Your own copy</b>: a private repository from the template, opened in Cursor.</li>
 <li><b>Step 1 · CLAUDE.md</b>: the rules Claude reads every time it starts.</li>
 <li><b>Step 2 · brain/ and documents/</b>: what you write vs. what you receive; then the brain gets its own private repo.</li>
 <li><b>Step 3 · A skill</b>: Claude judges, a script does the arithmetic (DOE).</li>
 <li><b>Step 4 · A planning session</b>: a plan on paper, then GitHub milestones and issues.</li>
</ol>
</section>""")

    n = next(fig)
    P.append(f"""
<section>
<h2>Step 0 · Your own private copy <span class='mins'>5 min</span></h2>
<p><b>Why.</b> The kit is a <i>template</i>: GitHub stamps out a fresh, separate repository for you. Yours is
private, so the work you do (and later, perhaps, your own numbers) is seen by nobody else.</p>
<h3>0.1 Make the copy on GitHub</h3>
<ol>
 <li>Sign in at <b>github.com</b>, then go to <b>{REPO}</b>.</li>
 <li>Click the green <b>Use this template</b> button (top right of the file list), then <b>Create a new repository</b>.</li>
 <li><b>Repository name:</b> <code>household-budget</code>. Choose <b>Private</b>. Leave <i>Include all branches</i> unticked.</li>
 <li>Click <b>Create repository</b>. You land on your new copy: <i>github.com/&lt;you&gt;/household-budget</i>.</li>
</ol>
<figure class='real'><div class='callout' style='left:62%;top:33%'>When you are signed in, <b>Use this template</b> appears here, beside <b>Code</b>.</div>
<img src='{img(dry / "img" / "repo.png")}'><figcaption><b>Figure {n}.</b> The kit on GitHub (real screenshot, signed out).
Note <b>Public template</b> beside the name.</figcaption></figure>
</section>""")

    n = next(fig)
    P.append(f"""
<section>
<h3>0.2 Open it in Cursor</h3>
<ol>
 <li>On <b>your</b> repository's page, click <b>Code</b> and copy the HTTPS URL.</li>
 <li>In Cursor: <b>File → New Window</b>, then <b>Clone repo</b> on the welcome screen. Paste the URL, press Enter,
 and choose your <b>Documents</b> folder. When asked, click <b>Open</b>.</li>
 <li>Open the terminal: <b>View → Terminal</b> (or <kbd>Ctrl</kbd> + <kbd>`</kbd>). Drag its top edge up so it fills half the window.</li>
 <li>Type <code>claude</code> and press Enter. The first time in a folder it asks whether you trust it: choose <b>Yes</b>.</li>
</ol>
<h3>0.3 Check GitHub knows who you are</h3>
{copybox("! gh auth status")}
<p><b>What you should see:</b> <code>✓ Logged in to github.com account &lt;you&gt;</code>. If it says you are not logged in:</p>
{copybox("! gh auth login")}
<p>Choose <b>GitHub.com → HTTPS → Yes → Login with a web browser</b>. Copy the one-time code it shows,
press Enter, paste the code in the browser page that opens, and approve. If <code>gh</code> is not installed at
all, run <code>! brew install gh</code> first (Mac).</p>
{screen("Cursor with the kit open: the files on the left, Claude Code running in the terminal at the bottom.",
        base, "STEPS.md", first_lines(KIT / "STEPS.md", 16),
        prompt_box("! gh auth status"), num=n)}
<div class='tip'><b>This is where most people get stuck.</b> If <code>gh</code> will not log in, carry on with Steps 1–3
(they are all local) and pair with a neighbour for 2b and 4b.</div>
</section>""")

    n = next(fig)
    P.append(f"""
<section>
<h2>Step 1 · The rules: CLAUDE.md <span class='mins'>10 min</span></h2>
<p><b>Why.</b> <code>CLAUDE.md</code> is read automatically every time Claude Code starts in this folder. It is how you
tell the assistant what the project is, how you like to work, and what it must never do. Right now
the kit's CLAUDE.md is three empty headings.</p>
{copybox("Write a CLAUDE.md for this folder. It's my household budget. It must tell you\nto follow standards/brain-standard.md and standards/doe.md. Ask me 5 questions\nfirst.")}
<h3>What happens</h3>
<ol>
 <li>Claude reads the folder and the two standards, then asks you five questions (who the budget is for, what
 it should never do, how you want answers written…). <b>Answer in your own words.</b> Short answers are fine.</li>
 <li>It shows you the CLAUDE.md it wants to write and asks permission. Read it, then press <b>1</b>.</li>
 <li>Type <code>/exit</code>, then <code>claude</code>. It now starts with your rules loaded.</li>
</ol>
<p><b>Rules worth making sure it includes:</b> never invent a number; all money arithmetic is done by a script;
never commit a statement, pay stub or bill to git; ask before moving or renaming files.</p>
{screen("The finished CLAUDE.md from the dry run. Yours will have your own answers in it.",
        base, "CLAUDE.md", first_lines(fin / "CLAUDE.md", 40), prompt_box("Write a CLAUDE.md for this folder. It's my household budget. It must tell you to follow standards/brain-standard.md and standards/doe.md. Ask me 5 questions first."), num=n)}
<p class='check'><b>You're on track if:</b> CLAUDE.md names both standards and contains your rules, and after
restarting, asking <i>"what are your rules in this folder?"</i> gets them back.</p>
</section>""")

    n = next(fig)
    n2 = next(fig)
    P.append(f"""
<section>
<h2>Step 2 · A brain and a documents folder <span class='mins'>10 min</span></h2>
<p><b>Why.</b> The whole brain standard is two sentences:</p>
<blockquote><b>If you wrote it, it is markdown in <code>brain/</code>, and it is in git.<br>
If you received it, it is a document in <code>documents/</code> with a <code>.json</code> beside it, and it is not.</b></blockquote>
<p>A bank statement was <i>received</i>, so it is evidence. "We agreed on $400 a month for eating out" was
<i>decided by you</i>, so it is knowledge. Open <code>standards/brain-standard.md</code> and skim it: it is one page.</p>
{copybox("Read standards/brain-standard.md. Set up brain/ and documents/ exactly as it\nsays. File everything in inbox/ into documents/ with standard names and a\nsidecar for each, then write one brain note recording our eating-out budget\ndecision. Run the checklist at the end.")}
<h3>What happens</h3>
<ol>
 <li>Claude reads each item in <code>inbox/</code>. Messy download names like <code>eStatement_Oct2026 (1).pdf</code> become
 <code>2026-10-31-peach-state-bank-statement.pdf</code>: the document's <b>own</b> date, who sent it, what it is.</li>
 <li>Beside each PDF it writes a <b>sidecar</b> <code>.json</code>: the original name, a fingerprint (sha256), why it is
 kept, and the document's text, so it can be searched and read without opening the PDF.</li>
 <li><code>note-from-dana.txt</code> is <b>not</b> filed as a document. It is a note from a person, so what it decides
 becomes a brain note instead. Expect Claude to explain that.</li>
 <li>It runs the checklist at the end of the standard and reports each tick.</li>
</ol>
{screen("After Step 2: six documents, each with its sidecar, and notes in brain/. The sidecar for the October statement is open.",
        after2, "2026-10-31-peach-state-bank-statement.json", sidecar_s, reply("All six checklist items pass. inbox/ is empty: six documents filed, and Dana's note became brain/eating-out-budget.md (it records a decision, so it is knowledge, not evidence)."), num=n)}
{screen("The brain note. Frontmatter at the top, then a Summary that states the point.",
        after2, "eating-out-budget.md", first_lines(fin / "brain" / "eating-out-budget.md", 24), "", num=n2)}
<p class='check'><b>You're on track if:</b> every PDF in <code>documents/</code> has a <code>.json</code> with the same name;
<code>inbox/</code> is empty; the brain note opens with <code>## Summary</code>. Your filenames may differ slightly. What matters is the pattern.</p>
</section>""")

    n = next(fig)
    P.append(f"""
<section>
<h2>Step 2b · The brain gets its own private GitHub repository <span class='mins'>5 min</span></h2>
<p><b>Why.</b> What you write deserves a history (every change, recoverable), and it should stay private even if
the project someday is not. So <code>brain/</code> becomes a separate repository with its own private home on GitHub.
The project's <code>.gitignore</code> already lists <code>/brain/</code>, so the project never copies it.</p>
{copybox("Make brain/ its own git repository, commit what's in it, create a PRIVATE\nGitHub repository for it called household-brain, and push it. Confirm it is\nprivate before you push.")}
<h3>What happens</h3>
<ol>
 <li>Claude runs <code>git init</code> inside <code>brain/</code> and makes a first commit.</li>
 <li>It runs <code>gh repo create household-brain --private</code> and pushes. Approve each command after reading it.</li>
 <li>It checks the visibility with <code>gh repo view</code>.</li>
</ol>
{screen("Claude checks the new repository is private. The output shown is from the dry run's repository.",
        after2, "eating-out-budget.md", first_lines(fin / "brain" / "eating-out-budget.md", 12),
        tool("Bash", "gh repo view household-brain --json name,visibility", '{"name":"household-brain","visibility":"PRIVATE"}'), num=n)}
<p class='check'><b>You're on track if:</b> github.com/&lt;you&gt;/household-brain exists, shows a <b>Private</b> badge,
and contains your note. <code>documents/</code> stays out of git entirely: received paperwork needs a backup, not a history.</p>
</section>""")

    n = next(fig)
    n2 = next(fig)
    P.append(f"""
<section>
<h2>Step 3 · A skill <span class='mins'>10 min</span></h2>
<p><b>Why.</b> A skill is a routine written down once, so Claude does it the same way every time. This one
follows <b>DOE</b> (Directive · Orchestration · Execution), whose rule is:</p>
<blockquote><b>Claude does not compute, and the scripts do not reason.</b></blockquote>
<p>Claude is good at judgement ("is <i>OCONEE FRESH MARKET</i> groceries?"). It should never add up money in its
head. So the <b>directive</b> (<code>SKILL.md</code>) says what to do, Claude <b>orchestrates</b> (reads, categorizes,
runs the script), and a Python script does the <b>execution</b> (the arithmetic). Skim <code>standards/doe.md</code> first.</p>
{copybox("Read standards/doe.md. Build a skill called monthly-summary that follows it:\nyou read the statements in documents/ and put each transaction in a category\nfrom budget.json; a script in scripts/ adds up totals against the budget and\nprints JSON. Dry run by default. Show me the SKILL.md before you write the\nscript.")}
<h3>What happens</h3>
<ol>
 <li>Claude shows the <code>SKILL.md</code> first. <b>Read it.</b> The <code>description</code> line at the top is what makes Claude
 pick this skill later, so it should contain the words you will actually say.</li>
 <li>It writes <code>scripts/total.py</code>, which reads <code>budget.json</code> and refuses to guess: a missing file or an
 unknown category is an error, never a zero.</li>
 <li>Type <code>/exit</code>, then <code>claude</code>, so the new skill loads.</li>
</ol>
{screen("The SKILL.md from the dry run: the directive. The description holds the trigger phrases; further down, its Steps forbid adding numbers up by hand.",
        after3, "SKILL.md", first_lines(fin / ".claude/skills/monthly-summary/SKILL.md", 34), "", num=n)}
</section>""")

    P.append(f"""
<section>
<h3>3.2 Ask the question</h3>
{copybox("What did we spend in October, and are we over on eating out?")}
<p>Claude should say it is using <b>monthly-summary</b>, write its categorized transactions to
<code>drafts/2026-10.json</code>, and run <code>total.py</code>. The numbers in its answer come from the script's JSON:</p>
<pre class='json'>{total_lines}</pre>
{screen("The answer from a fresh Claude Code session given only the kit's files and the skill (a real headless run, 18 November 2026, shortened).",
        after3, "2026-10.json", first_lines(fin / "drafts" / "2026-10.json", 30),
        prompt_box("What did we spend in October, and are we over on eating out?") +
        tool("Bash", "python3 .claude/skills/monthly-summary/scripts/total.py drafts/2026-10.json") +
        reply("\n".join(answer.splitlines()[:3])), num=n2)}
<p class='check'><b>You're on track if:</b> eating out comes to <b>${eo['spent']:.2f} against ${eo['budget']:.0f}</b>
(${-eo['left']:.2f} over), and Claude notices <b>StreamFlix charged twice</b> (${dup['amount']} on {dup['dates'][0][5:]} and {dup['dates'][1][5:]}),
which answers Dana's other question.</p>
<div class='tip'><b>When your Claude disagrees.</b> In the dry run Claude put the $84.33 Walmart charge under <i>shopping</i>;
the answer key says <i>groceries</i>. That is a judgement call, and it said so. To change it, open
<code>drafts/2026-10.json</code>, change the category, and ask again. The script recomputes; nobody re-adds anything by hand.</div>
</section>""")

    n = next(fig)
    P.append(f"""
<section>
<h2>Step 4 · A planning session <span class='mins'>10 min</span></h2>
<p><b>Why.</b> Plan before you build. In <b>plan mode</b> Claude can read and think, but cannot change any file until you
approve the plan.</p>
<ol>
 <li>Press <kbd>Shift</kbd> + <kbd>Tab</kbd> until the line under the input box says <b>plan mode on</b>.</li>
 <li>Paste:</li>
</ol>
{copybox("Plan what this project should do next: a monthly routine for filing\nstatements and checking the budget, and a savings goal for a $1,200 car repair\nby March 1. Don't build anything. Write the plan to PLAN.md.")}
<ol start='3'>
 <li>Claude may ask a question or two, then presents the plan. <b>Push back</b> on anything you don't like ("make
 the car fund $250 a month") and it revises.</li>
 <li>When it is right, approve it. Claude leaves plan mode and writes <code>PLAN.md</code>.</li>
</ol>
{screen("PLAN.md from the dry run: two phases, each a list of concrete tasks.",
        after3, "PLAN.md", first_lines(fin / "PLAN.md", 30),
        prompt_box("Plan what this project should do next: a monthly routine for filing statements and checking the budget, and a savings goal for a $1,200 car repair by March 1. Don't build anything. Write the plan to PLAN.md."),
        mode="plan mode on (shift+tab to cycle)", num=n)}
</section>""")

    n = next(fig)
    P.append(f"""
<section>
<h2>Step 4b · Turn the plan into milestones and issues <span class='mins'>5 min</span></h2>
<p><b>Why.</b> A plan in a file gets forgotten. On GitHub, a <b>milestone</b> is a goal with a due date, and an
<b>issue</b> is one task inside it. Closing issues moves the milestone's progress bar.</p>
{copybox("Turn PLAN.md into GitHub milestones and issues on this repository: one\nmilestone per phase with a due date, one issue per task, each issue in its\nmilestone. Show me the list before you create anything.")}
<h3>What happens</h3>
<ol>
 <li>Claude shows the milestones and issues it intends to create. Check them, then say <i>go ahead</i>.</li>
 <li>It creates milestones with <code>gh api …/milestones</code> and each issue with <code>gh issue create --milestone</code>.</li>
 <li>On GitHub, open your repository → <b>Issues</b> → <b>Milestones</b>.</li>
</ol>
<p>Then close the loop:</p>
{copybox("Close the issue for setting up the budget categories — that's done.")}
<figure class='real'><div class='gh'>{ms_html}</div><figcaption><b>Figure {n}.</b> The milestones and issues created in the
dry-run repository (drawn from GitHub's data for that repository). One issue is closed; the progress bar moved.</figcaption></figure>
<div class='tip'><b>"I said December 5 but it shows December 4."</b> GitHub stores a milestone's due date as midnight UTC, which is
the evening before in Georgia. Ask Claude to set it a day later if it matters.</div>
<p class='check'><b>You're on track if:</b> your repository's Milestones page shows two milestones, each with issues, and one issue is closed.
<i>Plan → issues → work → closed.</i></p>
</section>""")

    P.append(f"""
<section>
<h2>When something goes wrong</h2>
<table class='trouble'>
 <tr><th>What you see</th><th>What to do</th></tr>
 <tr><td><code>claude: command not found</code></td><td>Claude Code isn't installed in this terminal. Follow INSTALL.md in the Snack &amp; Learn kit. On Windows, make sure the terminal is WSL (Ubuntu).</td></tr>
 <tr><td><code>gh: command not found</code></td><td><code>! brew install gh</code> (Mac) or <code>! sudo apt install gh</code> (WSL), then <code>! gh auth login</code>.</td></tr>
 <tr><td><code>You are not logged into any GitHub hosts</code></td><td><code>! gh auth login</code> → GitHub.com → HTTPS → browser. Do Steps 1–3 meanwhile.</td></tr>
 <tr><td>Claude doesn't use the skill</td><td>Restart it (<code>/exit</code>, <code>claude</code>). Then ask using words from the skill's <code>description</code>, or type <code>/monthly-summary</code>.</td></tr>
 <tr><td>Claude ignores your CLAUDE.md</td><td>Restart it. CLAUDE.md is read when Claude Code starts, not mid-conversation.</td></tr>
 <tr><td>Claude is doing something you didn't want</td><td>Press <kbd>Esc</kbd>, then say what you want instead. At a permission prompt, choose <b>No</b> and explain.</td></tr>
 <tr><td>A number looks wrong</td><td>Ask <i>"which script produced that number, and from which file?"</i> Every number should trace to a script's output.</td></tr>
 <tr><td>You fell behind</td><td>Open <b>{REPO}/tree/finished</b>, find the file for your step, and compare or copy.</td></tr>
 <tr><td>The answer is worded differently from this guide</td><td>Expected. Claude doesn't repeat itself word for word. Check the <i>You're on track if</i> line instead.</td></tr>
</table>

<h2>What you built</h2>
<table class='built'>
 <tr><th>Piece</th><th>What it is</th><th>Why it matters</th></tr>
 <tr><td><code>CLAUDE.md</code></td><td>Your rules</td><td>Claude reads them every time it starts</td></tr>
 <tr><td><code>brain/</code></td><td>What you wrote, in its own private repository</td><td>Knowledge with a history</td></tr>
 <tr><td><code>documents/</code></td><td>What you received, named, with sidecars</td><td>Evidence: findable, and kept out of git</td></tr>
 <tr><td><code>.claude/skills/monthly-summary/</code></td><td>A routine written down once</td><td>Claude judges; a script does the math</td></tr>
 <tr><td><code>PLAN.md</code> + milestones and issues</td><td>What happens next</td><td>A plan on paper before code, then tracked</td></tr>
</table>
<p class='takeaway'>You wrote the rules, Claude filed the paper, a script did the math, and the plan was on paper before the code.</p>

<h2>Glossary</h2>
<dl>
 <dt>Repository (repo)</dt><dd>A project folder that git tracks, with every change recorded. GitHub hosts a copy online.</dd>
 <dt>Template repository</dt><dd>A repository GitHub can stamp out fresh copies of. Your copy has no link back to it.</dd>
 <dt>CLAUDE.md</dt><dd>The file Claude Code reads on startup in a folder: your instructions to it.</dd>
 <dt>Sidecar</dt><dd>A <code>.json</code> file beside a document holding its text and why it is kept, like captions beside a movie.</dd>
 <dt>Skill</dt><dd>A folder in <code>.claude/skills/</code> with a <code>SKILL.md</code> (and often scripts) that teaches Claude a routine.</dd>
 <dt>DOE</dt><dd>Directive / Orchestration / Execution: Nick Saraev's framework for reliable AI routines. The written routine, the AI that runs it, and the scripts that do the exact work.</dd>
 <dt>Plan mode</dt><dd>A Claude Code mode (<kbd>Shift</kbd>+<kbd>Tab</kbd>) where it can read and plan but not change anything until you approve.</dd>
 <dt>Milestone / issue</dt><dd>On GitHub: a goal with a due date, and one task inside it.</dd>
 <dt><code>gh</code></dt><dd>GitHub's command-line tool. Claude uses it to create repositories, milestones and issues for you.</dd>
</dl>
</section>""")
    return P


CSS = """
@page { size: letter; margin: 0.55in 0.6in 0.6in; }
* { box-sizing: border-box; }
body { font-family: -apple-system, 'Helvetica Neue', Helvetica, Arial, sans-serif; font-size: 10.5pt;
       line-height: 1.45; color: #1d1d1f; }
section { break-before: page; }
section.cover { break-before: auto; padding-top: 0.6in; }
.kicker { color: #c0561b; font-weight: 600; letter-spacing: .04em; text-transform: uppercase; font-size: 9pt; }
h1 { font-size: 34pt; line-height: 1.08; margin: 10px 0 14px; }
h2 { font-size: 17pt; margin: 0 0 8px; border-bottom: 2px solid #c0561b; padding-bottom: 4px; }
h2 .mins { float: right; font-size: 10pt; color: #888; font-weight: 500; margin-top: 8px; }
h3 { font-size: 12pt; margin: 14px 0 6px; }
.lede { font-size: 13pt; color: #333; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; }
th, td { text-align: left; vertical-align: top; padding: 6px 8px; border-bottom: 1px solid #e3e3e3; }
th { background: #f6f3ef; font-size: 9.5pt; }
.facts th { width: 22%; background: none; color: #666; }
code { font-family: Menlo, monospace; font-size: 9pt; background: #f3f3f3; padding: 1px 4px; border-radius: 3px; }
kbd { font-family: Menlo, monospace; font-size: 8.5pt; border: 1px solid #bbb; border-bottom-width: 2px;
      border-radius: 4px; padding: 0 5px; background: #fafafa; }
.note { background: #f4f7fb; border-left: 4px solid #1d5f8a; padding: 9px 12px; margin: 12px 0; }
.note.warn { background: #fdf4ee; border-color: #c0561b; }
.tip { background: #fffbe8; border-left: 4px solid #d4a514; padding: 8px 12px; margin: 10px 0; }
.check { break-inside: avoid; break-before: avoid; background: #eef7ef; border-left: 4px solid #2f7d32; padding: 8px 12px; }
blockquote { margin: 8px 0; padding: 8px 14px; background: #f6f3ef; border-left: 4px solid #c0561b; }
.copy { border: 1px solid #c9c3bb; border-radius: 6px; margin: 8px 0 10px; break-inside: avoid; }
.copy .cl { background: #f6f3ef; font-size: 8pt; color: #7a6f63; padding: 3px 10px; text-transform: uppercase; letter-spacing: .05em; }
.copy pre { margin: 0; padding: 8px 10px; font-family: Menlo, monospace; font-size: 9pt; white-space: pre-wrap; }
pre.json { font-family: Menlo, monospace; font-size: 8pt; background: #f7f7f7; padding: 8px; border-radius: 4px; }
ol, ul { padding-left: 20px; margin: 6px 0; } li { margin: 3px 0; }
figure { margin: 12px 0; break-inside: avoid; }
figcaption { font-size: 8.5pt; color: #555; margin-top: 4px; }
.drawn { color: #999; font-style: italic; }
figure.real { position: relative; }
figure.real img { width: 100%; border: 1px solid #ccc; border-radius: 6px; }
.callout { position: absolute; width: 33%; background: #c0561b; color: #fff; font-size: 8.5pt; padding: 6px 8px;
           border-radius: 6px; box-shadow: 0 2px 6px rgba(0,0,0,.25); }
.win { border-radius: 8px; overflow: hidden; border: 1px solid #2b2b2b; background: #1e1e1e; color: #ccc;
       font-family: Menlo, monospace; font-size: 7.4pt; }
.bar { background: #2d2d2d; padding: 5px 8px; display: flex; align-items: center; gap: 5px; }
.d { width: 9px; height: 9px; border-radius: 50%; display: inline-block; }
.d.r { background: #ff5f57; } .d.y { background: #febc2e; } .d.g { background: #28c840; }
.wt { margin-left: auto; margin-right: auto; color: #999; font-family: -apple-system, Helvetica; font-size: 8pt; }
.body { display: flex; }
.side { width: 30%; background: #252526; padding: 4px 0 8px; border-right: 1px solid #333; min-height: 200px; }
.sh { color: #888; font-size: 6.5pt; padding: 2px 8px 4px; letter-spacing: .06em; }
.ti { line-height: 1.25; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding: 1px 6px; color: #c8c8c8; }
.ti.act { background: #37373d; color: #fff; }
.tic { color: #777; display: inline-block; width: 10px; }
.main { width: 70%; display: flex; flex-direction: column; }
.tabs { background: #252526; } .tab { display: inline-block; background: #1e1e1e; color: #fff; padding: 4px 12px; border-top: 1px solid #c0561b; }
.tab.dim { color: #777; border: none; background: none; }
.ed { margin: 0; padding: 6px 10px; max-height: 175px; overflow: hidden; white-space: pre-wrap; color: #d4d4d4;
      font-family: Menlo, monospace; font-size: 7.2pt; line-height: 1.35; }
.term { border-top: 1px solid #444; background: #181818; }
.th { color: #888; font-size: 6.5pt; padding: 3px 10px; letter-spacing: .06em; border-bottom: 1px solid #2a2a2a; }
.tb { padding: 6px 10px; }
.pbox { border: 1px solid #666; border-radius: 4px; padding: 4px 7px; color: #eee; margin: 4px 0; }
.gt { color: #888; }
.tool { margin: 4px 0; color: #ddd; } .dot { color: #4ec37b; } .dot.w { color: #eee; }
.tout { color: #999; padding-left: 14px; }
.reply { margin: 4px 0; color: #e6e6e6; font-family: -apple-system, Helvetica; font-size: 8pt; }
.ccmode { color: #6aa2ff; font-size: 6.8pt; padding: 2px 10px 5px; } .ccmode.dim { color: #666; }
.gh { border: 1px solid #d0d7de; border-radius: 6px; padding: 10px 14px; font-family: -apple-system, Helvetica; font-size: 9pt; }
.ms { margin-bottom: 12px; } .mh { display: flex; justify-content: space-between; font-size: 10.5pt; }
.mh span { color: #656d76; font-size: 8.5pt; }
.prog { height: 7px; background: #e6e9ec; border-radius: 4px; margin: 4px 0; } .prog div { height: 7px; background: #1f883d; border-radius: 4px; }
.small { color: #656d76; font-size: 8pt; }
.iss { padding: 3px 0; border-bottom: 1px solid #eef0f2; } .iss .ico { color: #1a7f37; display: inline-block; width: 16px; }
.iss.closed .ico { color: #8250df; } .iss.closed { color: #656d76; } .num { color: #656d76; }
.takeaway { font-size: 13pt; font-style: italic; text-align: center; margin: 14px 0; color: #c0561b; }
dt { font-weight: 600; margin-top: 6px; } dd { margin: 0 0 4px 14px; }
"""


def main():
    if len(sys.argv) < 3:
        sys.exit(json.dumps({"error": "usage: guide.py <finished-checkout> <dryrun-dir> [--confirm]"}))
    fin, dry = sys.argv[1], sys.argv[2]
    for need in [Path(fin) / "CLAUDE.md", Path(dry) / "answer.txt", Path(dry) / "total.json",
                 Path(dry) / "issues.tsv", Path(dry) / "img" / "repo.png"]:
        if not need.exists():
            sys.exit(json.dumps({"error": f"missing input: {need}"}))
    sections = build(fin, dry)
    doc = (f"<!doctype html><html><head><meta charset='utf-8'><title>Household Budget — Guide</title>"
           f"<style>{CSS}</style></head><body>{''.join(sections)}</body></html>")
    out = KIT / "GUIDE.pdf"
    if "--confirm" not in sys.argv:
        print(json.dumps({"would_write": str(out), "sections": len(sections), "html_bytes": len(doc)}))
        return
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "guide.html"
        src.write_text(doc, encoding="utf-8")
        (Path(dry) / "guide.html").write_text(doc, encoding="utf-8")
        r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                            f"--user-data-dir={tmp}/p", f"--print-to-pdf={out}", src.as_uri()],
                           capture_output=True, text=True, timeout=180)
    if r.returncode != 0 or not out.exists():
        sys.exit(json.dumps({"error": "chrome failed", "stderr": r.stderr[-400:]}))
    pages = subprocess.run(["pdfinfo", str(out)], capture_output=True, text=True).stdout
    print(json.dumps({"wrote": str(out), "bytes": out.stat().st_size,
                      "pages": next((l.split()[-1] for l in pages.splitlines() if l.startswith("Pages")), "?")}))


if __name__ == "__main__":
    main()
