# Household Budget Kit

A first Claude Code project for the **AI Snack & Learn** series at Georgia
College: a simple household budget, built in five steps.

**Start with [`STEPS.md`](STEPS.md).**

| | What it is |
|---|---|
| [`STEPS.md`](STEPS.md) | The handout: one prompt per step, and what you should see |
| [`inbox/`](inbox/) | An invented household's paperwork: two bank statements, a Visa statement, a pay stub, an electric bill, a grocery receipt and a note |
| [`standards/`](standards/) | The two one-page rulebooks Claude follows: the **brain standard** and **DOE** |
| [`budget.json`](budget.json) | The monthly budget, one amount per category |
| `CLAUDE.md` | Empty on purpose. Step 1 writes it. |
| `finished` branch | The end state of every step, if you get stuck: `git checkout finished` |

## Get it

On GitHub: **Use this template → Create a new repository → Private**. Then
clone your copy in Cursor (**File → New Window → Clone repo**) and type
`claude` in the terminal. New to Cursor and Claude Code? Install with the
[Snack & Learn kit's INSTALL.md](https://github.com/bryanmarshall-com/snack-learn-kit/blob/main/INSTALL.md).

## Everything here is invented

The Okafor-Lane household, Peach State Bank, Magnolia Visa, Middle Georgia
Electric, Oconee Fresh Market, Pine Ridge School District and Riverside Family
Clinic are all made up for this exercise. Every page is watermarked
SAMPLE and every account number is `0000`. `_source/build.py` regenerates them.

**Never put your own statements in a public repository.** If you use this for
real money, use a private copy, and keep the documents out of git (the
`.gitignore` already does).
