# How to run this project

This is the one file to open first. It tells you how to get the course code
running on your own machine, what every file is for, and how we run the model
calls in this course. If you read nothing else, read the first two sections.

The per unit guides in `docs/unit1`, `docs/unit2`, and `docs/unit3` then walk
you through every file we build, lecture by lecture, so you can run each piece
alongside me in class.

---

## 1. Get it running in ten minutes

You need three things: the code, a Python environment, and one working lane (a
way to reach a model). None of this costs money.

```bash
# 1. get the code
git clone https://github.com/rbi-international/cse476-agentic-ai.git
cd cse476-agentic-ai

# 2. create the environment (this is the clean, reliable way)
conda env create -f environment.yml
conda activate cse476
pip install -e .

# 3. make your own .env from the template, then add one key (see section 3)
cp .env.example .env        # Windows: copy .env.example .env

# 4. check everything
python setup_check.py
```

When `setup_check.py` prints **You are ready**, you are ready. If it does not,
it tells you exactly what to fix, and `docs/TROUBLESHOOTING.md` covers the
common cases. Do not skip the check and hope; the check exists so you never
debug in the dark.

One more step so notebooks find the environment:

```bash
python -m ipykernel install --user --name cse476 --display-name "Python (cse476)"
```

Then in any notebook, pick the **Python (cse476)** kernel.

---

## 2. How we run models in this course, the Foundry way

This is a Microsoft Foundry course. The skill you are here to build is running
agents on Microsoft Foundry the way you would in a real job, so **Foundry is the
path I want you on**, and it is the path I use in every live demo.

I have set Foundry up myself, carefully, and written down exactly how, so you
can follow the same steps rather than guess. That full walkthrough is
`docs/FOUNDRY_SETUP.md`. Read its first section before you enter a card number
anywhere, because a Pay As You Go account has no spending limit and the only
real cost control is a setting most people never touch. The guide shows you the
setting.

The short version of the Foundry path:

1. Start on the **Azure free account**, which has a spending limit on by
   default, so it disables itself rather than billing you.
2. Create a **Foundry project** in the new Foundry portal.
3. Deploy **one** small model with a **deliberately low tokens per minute cap**.
   That cap is the real spend control. `docs/FOUNDRY_SETUP.md` shows the exact
   slider and the arithmetic.
4. Put the endpoint and key in your `.env` with `PROVIDER=foundry`.
5. Run `python setup_check.py` and confirm the `foundry` lane passes.

I know Foundry has more setup than a free token. That setup is the point: it is
the same account, quota, and deployment work you will do on day one of a job
that uses Foundry. Doing it once, safely, with me, is the course.

---

## 3. If you cannot use Foundry yet, keep working on a free lane

Nobody should be blocked from doing the coursework because a Foundry account is
still pending. The code is written around a **lane** abstraction: one setting,
`PROVIDER`, chooses where model calls go, and **nothing else in the code
changes**. So you can develop on a free lane today and switch to Foundry the
moment your account is ready, with a one line change.

There are four lanes. `docs/LANES.md` has the full detail; here is how to get a
key for each, quickest first.

**GitHub Models, the easy free lane. Recommended while you wait for Foundry.**
Free, no card, and enough for all the coursework.
1. Go to `github.com/settings/tokens`
2. Generate a new token (classic). Tick **no** scopes at all.
3. Copy it into `GITHUB_TOKEN` in your `.env`, and set `PROVIDER=github`.

**Groq, a fast free lane.** Also free.
1. Go to `console.groq.com` and sign in.
2. Create an API key.
3. Copy it into `GROQ_API_KEY` in your `.env`, and set `PROVIDER=groq`.

**Ollama, fully offline on your own machine.** No key, no internet, no cost,
but you need a machine that can run a small model locally.
1. Install Ollama from `ollama.com`.
2. Pull a small model, for example `ollama pull llama3.2`.
3. Set `PROVIDER=local`. There is no key to set.

**Foundry, the one this course is really about.** See section 2 and
`docs/FOUNDRY_SETUP.md`.

The whole point of the lane design: **do your daily work on GitHub Models if you
must, but move to Foundry as soon as you can, because Foundry is what this course
is preparing you for.** Switching is one line in `.env`. Your code never changes.

To see which lane you are on at any time:

```bash
python -c "from cse476.lanes import describe; print(describe())"
```

---

## 4. What is in this repository

A quick map so nothing is a mystery. The per unit guides go deeper.

```
RUN_THIS_PROJECT.md   this file, start here
README.md             the course overview and the thinking behind the design
setup_check.py        run first, and whenever something breaks

src/cse476/           the shared library every notebook imports
notebooks/u1/         Unit 1, the code I build live, one notebook per lecture
notebooks/u2/         Unit 2, same
notebooks/u3/         Unit 3, built on the real frameworks
tests/                tests that prove the code works, mostly offline
practicals/           the ten assessed practicals, one folder each
slides/               NOT in this repo, see the note below. Shared per lecture.

docs/FOUNDRY_SETUP.md   how I set up Foundry, so you can follow exactly
docs/LANES.md           the four lanes, and how to get a key for each
docs/TROUBLESHOOTING.md what to do when something will not run
docs/SYLLABUS_MAP.md    every syllabus phrase, pinned to the lecture that covers it
docs/WHY_THIS_COURSE.md why the course is shaped the way it is
docs/unit1/GUIDE.md     every Unit 1 file, what it does, how to run it
docs/unit2/GUIDE.md     every Unit 2 file, same
docs/unit3/GUIDE.md     every Unit 3 file, same
docs/unit4/GUIDE.md     every Unit 4 file, same

environment.yml       the conda environment definition
requirements.txt      the exact packages
.env.example          the template you copy to make your own .env
.env                  YOUR keys. Never shared, never committed.
```

**About the slides.** The lecture decks and their PDF handouts are not in this
repository. I share each lecture's slides separately, one at a time, as we reach
that lecture (through the class channel or however we agree in class). So if you
do not see a `slides/` folder, nothing is broken; the code is here, the slides
come from me per lecture.

---

## 5. The shared library, in one glance

Everything in `src/cse476/` is code we build together in a lecture and then
reuse. One module per lecture, plus `lanes.py`, which every module leans on.

**Shared, used everywhere**
- `lanes.py` picks where model calls go, from one `PROVIDER` setting.

**Unit 1, building an agent by hand**
- `tiny_agent.py` the smallest honest agent: a loop, tools, a budget.
- `architectures.py` the same task in four shapes, so you feel the tradeoffs.
- `conversation.py` multi turn memory, and keeping a transcript from exploding.
- `planning.py` planning and reasoning before acting.
- `design.py` a design linter that checks an agent before it runs.

**Unit 2, making it reliable**
- `triage.py` one problem in three shapes: workflow, router, agent.
- `tools.py` tool calling, and the four ways a tool fails, handled.
- `api.py` wrapping a messy real API into a tool an agent can trust.
- `pipeline.py` chaining steps, stopping on failure, reacting to events.
- `context.py` carrying context across turns, and testing by invariants.

**Unit 3, the real frameworks**
- `frameworks.py` the landscape: the merger, the map, the import trap.
- `kernel.py` real Semantic Kernel: kernel, plugins, connectors.
- `agent_fw.py` a real, shippable agent on Microsoft Agent Framework.
- `rag.py` real sessions for memory, and retrieval built from scratch.
- `multi_agent.py` a manager over specialists, and a real graph that runs.

---

## 6. Run the tests, and see the code prove itself

Every module has a test that runs offline and prints `ALL PASS`. This is not
busywork; it is how you confirm your setup works before class, and how you see
each piece behave without spending a token.

```bash
# the pytest suite (the lanes abstraction)
python -m pytest

# any single lecture's demonstration, run directly
python tests/mock_run_u3l5.py     # the multi-agent graph, for example
```

The `mock_run_*.py` files are standalone demonstrations, not pytest tests, so
you run them directly with `python`. Each one exercises a lecture's module and
ends in `ALL PASS`. The per unit guides tell you which file goes with which
lecture.

---

## 7. The one rule that saves the most pain

Do all of this in the `cse476` environment, not in your base Python and not in
an environment you also use for other projects. A shared environment is the
single most common reason an install that works for everyone else fails for you.
`conda activate cse476` before you work, every time.
