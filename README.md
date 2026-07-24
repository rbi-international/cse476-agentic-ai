# CSE476 Agentic AI and Intelligent Automation

School of Computer Science and Engineering, Lovely Professional University.

Everything for this course lives here: the practicals, the lecture notebooks, the
slide handouts, the setup script and the tests. Clone it once, and `git pull`
before every session.

---

## Start here

You need about fifteen minutes and a GitHub account. Nothing else. No credit
card, no cloud subscription, no waiting on an approval from anybody.

### 1. Get the code

```bash
git clone https://github.com/rbi-international/cse476-agentic-ai.git
cd cse476-agentic-ai
```

### 2. Create the environment

**With conda**, which is what is used in class:

```bash
conda env create -f environment.yml
conda activate cse476
pip install -e .
```

**With plain venv**, if you do not have conda:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

Two things worth understanding rather than copying blindly:

- `environment.yml` pins only Python and pip. Everything else comes from
  `requirements.txt` through pip. That is deliberate, because conda-forge lags
  PyPI by weeks on exactly the agent SDKs that matter most here.
- `pip install -e .` installs this repository as an editable package. Without
  it, `from cse476.lanes import ...` fails with `ModuleNotFoundError`, and that
  is the single most common setup problem in this course.

### 3. Register the Jupyter kernel

```bash
python -m ipykernel install --user --name cse476 --display-name "Python (cse476)"
```

Then pick **Python (cse476)** in the notebook kernel picker. If you skip this,
your notebooks will run on the system Python and none of the imports will work.

### 4. Configure a lane

```bash
cp .env.example .env               # Windows: copy .env.example .env
```

Open `.env` and put a GitHub token in `GITHUB_TOKEN`. Get one at
github.com/settings/tokens: generate a classic token, tick **no scopes at all**,
copy it. That is enough for GitHub Models.

### 5. Verify

```bash
python setup_check.py
```

It checks your Python version, your packages, your configuration, every lane you
have set up, and then makes one real API call. It either prints `You are ready.`
or tells you the exact thing to fix.

If it fails, read `docs/TROUBLESHOOTING.md`, then post the **entire** output in
the course channel. Not a screenshot of one line.

---

## The four lanes

Every practical runs on all four. You change one line in `.env` and nothing else
in any notebook.

| Lane | What it is | Cost | Who uses it |
|---|---|---|---|
| `foundry` | Microsoft Foundry | billed to a subscription | demonstrated in class |
| `github` | GitHub Models | free with a GitHub account | **your default** |
| `groq` | Groq | free tier | if you want speed |
| `local` | Ollama on your laptop | free forever | when everything else fails |

Full detail, including where to get each credential and what the real limits
are, is in [`docs/LANES.md`](docs/LANES.md).

### How it works in your code

```python
from cse476.lanes import get_client, MODEL, describe

print(describe())    # Lane: GitHub Models (github, free) | Model: openai/gpt-4.1-mini
client = get_client()

reply = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "Hello"}],
)
```

That is the entire abstraction. Your notebook never names a provider.

---

## What is in here

```
docs/                setup, lanes, troubleshooting, syllabus map
notebooks/u1/        the live builds from each lecture
practicals/          the ten assessed practicals, one folder each
slides/              decks, with PDF handouts in slides/pdf
src/cse476/          the shared library everything imports
tests/               offline tests, see below
environment.yml      conda environment definition
requirements.txt     package versions
setup_check.py       run this first, and again whenever something breaks
```

### The library

| Module | What it is for | Introduced in |
|---|---|---|
| `lanes.py` | The four lane switch. One `PROVIDER` constant, four providers. | Practical 1 |
| `tiny_agent.py` | The smallest honest agent. Tools, loop, whitelist, budget guard. | Unit 1 Lecture 1 |
| `architectures.py` | Reflex, model based, goal based and utility based, on one shared loop. | Unit 1 Lecture 2 |
| `conversation.py` | Token counting, cost simulation, and three ways to trim a transcript. | Unit 1 Lecture 3 |
| `planning.py` | ReAct, plan then execute, reflection, and the no progress detector. | Unit 1 Lecture 4 |

Everything is deliberately plain. If you can read `tiny_agent.py`, you can read
any agent framework, because they are all doing that underneath.

### The notebooks

| Notebook | Lecture | What you build |
|---|---|---|
| `notebooks/u1/l1_first_agent.ipynb` | U1 L1 | A working agent in about forty lines, then break it twice |
| `notebooks/u1/l2_architectures.ipynb` | U1 L2 | The same task through four architectures, and read the difference |
| `notebooks/u1/l3_conversation.ipynb` | U1 L3 | Measure a conversation, trim it, discover what the trim broke |
| `notebooks/u1/l4_planning.ipynb` | U1 L4 | Act first versus reason first, then build the third exit condition |

Some cells are **meant to fail**. They are labelled. Running them is the lesson.

**One cost warning.** Cell 4 of `l1_first_agent.ipynb` deliberately runs an agent
with no reachable answer and an eight step budget, so it makes eight billed
calls. Run it once, in class. Do not leave it looping while you experiment.

---

## The tests

There are two kinds, and they do different jobs.

### `pytest` tests, which CI runs

```bash
pytest -q
```

`tests/test_lanes.py`. Checks that the lane switch resolves correctly and that a
misconfigured lane fails with a message you can act on rather than a stack
trace. **Runs with no API key of any kind**, which is the point: CI has no
secrets, so the abstraction has to be testable without them.

### Offline demonstration scripts, which you run by hand

```bash
python tests/mock_run.py       # Unit 1 Lecture 1
python tests/mock_run_l2.py    # Unit 1 Lecture 2
python tests/mock_run_l3.py    # Unit 1 Lecture 3
python tests/mock_run_l4.py    # Unit 1 Lecture 4
```

These stand in a fake client that replays scripted model responses, so they
prove the parts that are actually ours: the control flow, the message shapes,
the whitelist, the budget guard, the trimming. **No API key, no internet, no
cost.** Each ends in `ALL PASS` or tells you what broke.

They are named `mock_run*` rather than `test_*` on purpose, so pytest does not
collect them. They are teaching artefacts, not unit tests.

Worth running at least once each, because the assertions are the lecture's
arguments in executable form. Two are worth singling out:

- `mock_run_l3.py` scenarios 6 and 7: the same thirty turn conversation, one
  budget, and a stated allergy that survives with pinning and is silently lost
  without it.
- `mock_run_l4.py` scenario 4: the no progress detector staying **quiet** while
  an agent is working correctly. A guardrail that fires on healthy behaviour is
  worse than no guardrail, because it stops working systems and teaches you to
  ignore it. Testing that something does not fire is half the job.

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

Each folder has its own brief. Practicals 8, 9 and 10 build on **one** system:
you build a retrieval agent, instrument that same agent, then secure and deploy
that same agent. You finish with one deployed thing you can link to, not three
notebooks nobody will open.

[`docs/SYLLABUS_MAP.md`](docs/SYLLABUS_MAP.md) maps every approved syllabus topic
to where it is taught and which practical assesses it.

---

## Rules that will save you marks

**Never commit a key.** `.env` is gitignored, `setup_check.py` verifies that
before it lets you pass, and CI fails the build if `.env` ever becomes tracked.
If you paste a key into a notebook cell, rotate it immediately, because notebook
outputs get committed.

**Delete your cloud resources after every lab.** An idle deployment costs money
while you sleep. On Azure for Students the subscription simply stops when the
credit is gone, and it does not top up early.

**Pull before every session.** Content changes between sessions, including fixes
to things that broke in the previous one.

**Submit notebooks with their outputs.** A notebook with empty output cells means
it was never run, and it will be marked as such.

---

## Currency notes

Verified 24 July 2026. Three things changed recently that will confuse you when
you search for help:

- **Azure AI Foundry is now Microsoft Foundry.** Renamed at Ignite in November
  2025, formalised in the January 2026 product terms. Same platform, same
  resource type, same keys. Search both names.
- **Bot Framework SDK is retired.** Long term support ended December 2025 and
  the repository is archived. We use the Microsoft 365 Agents SDK instead.
- **Semantic Kernel and AutoGen have converged** into Microsoft Agent Framework
  1.0, shipped 3 April 2026. We still learn both, because both still run and
  both are what the certification tests, and Unit 4 covers the migration.

One more that costs money rather than confusion: **Groq reduced its free tier
during 2026**, to roughly 1,000 requests per day on most models. Older tutorials
quote a much higher figure.

---

## Help

Course channel first. Post the full error text, not a description of it, and say
which lane you are on. Somebody else has almost certainly hit it already.

[`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) covers the errors that come
up most: missing package installs, wrong model names per lane, 401s, 429s,
runaway loops, and what to do if you commit a key by accident.
