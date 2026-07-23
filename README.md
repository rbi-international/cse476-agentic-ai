# CSE476 Agentic AI and Intelligent Automation

School of Computer Science and Engineering, Lovely Professional University.

Everything for this course lives here: the practicals, the notebooks, the setup
script, and the slide handouts. Clone it once and pull before every session.

---

## Start here

You need about fifteen minutes and a GitHub account. Nothing else. No credit
card, no cloud subscription, no institutional approval.

```bash
git clone https://github.com/rbi-international/cse476-agentic-ai.git
cd cse476-agentic-ai

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
pip install -e .

cp .env.example .env               # Windows: copy .env.example .env
```

Now open `.env`, put a GitHub token in `GITHUB_TOKEN`, and run:

```bash
python setup_check.py
```

It checks your Python, your packages, your configuration and every lane, then
either says `You are ready.` or tells you the exact thing to fix. If it fails,
paste its entire output into the course channel. Do not paste a screenshot of
one line, and do not spend three hours on it alone.

**Getting a GitHub token:** github.com/settings/tokens, generate a classic
token, tick no scopes at all, copy it. That is enough for GitHub Models.

---

## The four lanes

Every practical runs on all four. You choose one line in `.env` and change
nothing else in any notebook.

| Lane | What it is | Cost | Who uses it |
|---|---|---|---|
| `foundry` | Microsoft Foundry | billed to a subscription | demonstrated in class |
| `github` | GitHub Models | free with a GitHub account | **your default** |
| `groq` | Groq | free tier | if you want speed |
| `local` | Ollama on your laptop | free forever | when everything else fails |

Full detail, including where to get each credential and what each one's limits
actually are, is in [`docs/LANES.md`](docs/LANES.md).

### How it works in your code

```python
from cse476.lanes import get_client, MODEL, describe

print(describe())          # Lane: GitHub Models (github, free) | Model: openai/gpt-4.1-mini
client = get_client()

reply = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "Hello"}],
)
```

That is the entire abstraction. Your notebook never mentions a provider.

---

## Layout

```
practicals/          the ten assessed practicals, one folder each
notebooks/           in class live builds, by unit
src/cse476/          the shared library the practicals import
docs/                setup, lanes, troubleshooting, syllabus map
slides/              handouts for each session
tests/               tests that run in CI
setup_check.py       run this first, and again whenever something breaks
```

---

## The ten practicals

| # | Practical | Unit |
|---|---|---|
| 1 | Development environment, Foundry and VS Code | 1 |
| 2 | Conversational hotel information agent | 1 |
| 3 | Intelligent workflow automation agent | 2 |
| 4 | Tool calling and API integration, Semantic Kernel | 3 |
| 5 | Agent with memory and context management | 3 |
| 6 | Medical information agent with responsible AI | 4 |
| 7 | Multi agent collaborative workflow system | 4 |
| 8 | Retrieval augmented generation workflows | 5 |
| 9 | Monitoring and observability for agents | 5 |
| 10 | Secure deployment and governance | 6 |

Practicals 8, 9 and 10 build on **one** system. You will build a retrieval
agent, instrument that same agent, then secure and deploy that same agent. At
the end you have one deployed thing you can link to, not three notebooks.

---

## Rules that will save you marks

**Never commit a key.** `.env` is gitignored and `setup_check.py` verifies that
before it lets you pass. If you ever paste a key into a notebook cell, rotate it
immediately, because notebook outputs get committed.

**Delete your cloud resources after every lab.** An idle deployment costs money
while you sleep. On Azure for Students the subscription simply stops when the
credit is gone, and it does not top up early.

**Pull before every session.** Content changes between sessions, including
fixes to things that broke in the previous one.

**When something is deprecated, this repo says so.** This field renames and
retires things quickly. If a file contradicts a tutorial you found online,
check the date on the tutorial first.

---

## Currency notes

Verified 23 July 2026. Things that changed recently and will confuse you if you
search for help:

- **Azure AI Foundry is now Microsoft Foundry.** Renamed at Ignite in November
  2025, formalised in the January 2026 product terms. Same platform, same
  resource type, same keys. Search both names.
- **Bot Framework SDK is retired.** Long term support ended December 2025 and
  the repository is archived. We use the Microsoft 365 Agents SDK instead.
- **Semantic Kernel and AutoGen have converged** into Microsoft Agent Framework
  1.0, shipped 3 April 2026. We still learn both, because both still run and
  both are what the certification tests, and Unit 4 covers the migration.

---

## Help

Course channel first. Post the full error text, not a description of it, and
say which lane you are on. Somebody else has almost certainly hit it already.

[`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) covers the errors that come
up most.
