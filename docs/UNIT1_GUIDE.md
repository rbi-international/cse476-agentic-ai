# Unit 1 guide, Foundations of Agentic AI

This unit builds an agent **by hand**, so you understand every moving part before
any framework hides it. No framework in this unit, just Python, a model, and the
loop that turns one into an agent.

Each lecture has three things you can open and run: a **module** in `src/cse476/`
(the code we build), a **notebook** in `notebooks/u1/` (where I build it live),
and a **test** in `tests/` (proof it works, run offline). This guide lists all
three per lecture, tells you what each does, and gives you the exact command.

Before you start: `conda activate cse476`, and have one lane working
(`python setup_check.py` says you are ready). See `RUN_THIS_PROJECT.md`.

> A note on the domain. Unit 1's example code is built around a small hotel
> booking assistant. From Unit 2 onward the running example becomes support
> ticket triage. This is deliberate: Unit 1 is about the mechanics of an agent,
> and a hotel helper is an easy, familiar thing to reason about while you learn
> them. The skills transfer unchanged.

---

## Lecture 1, Your first agent

**Module** `src/cse476/tiny_agent.py`
The smallest honest agent: a registry of tools, a loop that lets the model
choose one, an observation fed back, and a budget so it cannot loop forever.
Public pieces: `get_room_availability`, `get_nightly_rate` (the tools), and
`run_agent` (the loop).

**Notebook** `notebooks/u1/l1_first_agent.ipynb`
Where we build the loop step by step and watch it call a tool.

**Test** `tests/mock_run.py`
Runs the agent's shape offline and prints `ALL PASS`.

```bash
python tests/mock_run.py
jupyter notebook notebooks/u1/l1_first_agent.ipynb
```

The one idea to leave with: an agent is a **loop** around a model that can call
tools and see the results. That is the whole definition.

---

## Lecture 2, Agent architectures

**Module** `src/cse476/architectures.py`
The same task in four classic shapes so you feel the tradeoffs: `reflex` (rule
based, no model), `ModelBasedAgent` (keeps state), `goal_based`, and
`utility_based` (scores its options).

**Notebook** `notebooks/u1/l2_architectures.ipynb`

**Test** `tests/mock_run_l2.py`

```bash
python tests/mock_run_l2.py
jupyter notebook notebooks/u1/l2_architectures.ipynb
```

Leave with: there is no one right architecture. You pick the simplest shape that
solves the problem, and often that is not the fanciest one.

---

## Lecture 3, Conversation and memory

**Module** `src/cse476/conversation.py`
The mechanics of a conversation you can measure and control: counting tokens
(`count_tokens`, `transcript_tokens`), simulating cost (`simulate_cost`), and
keeping a transcript from exploding with a `sliding_window`, `summarise_older`,
and `pin` for facts that must survive trimming.

**Notebook** `notebooks/u1/l3_conversation.ipynb`

**Test** `tests/mock_run_l3.py`

```bash
python tests/mock_run_l3.py
jupyter notebook notebooks/u1/l3_conversation.ipynb
```

Leave with: memory is not free. Every turn costs tokens, so a real agent trims
and pins on purpose rather than remembering everything.

---

## Lecture 4, Planning and reasoning

**Module** `src/cse476/planning.py`
Four ways an agent can think before it acts: `act_only` (no planning),
`react` (reason then act, in a loop), `plan_then_execute` (plan the whole thing
first), and `reflect` (check its own work). `compare` puts them side by side,
and `NoProgress` is the guard that catches an agent going in circles.

**Notebook** `notebooks/u1/l4_planning.ipynb`

**Test** `tests/mock_run_l4.py`

```bash
python tests/mock_run_l4.py
jupyter notebook notebooks/u1/l4_planning.ipynb
```

Leave with: planning is a spectrum. More planning is not always better; it costs
tokens and time, and sometimes acting and checking beats planning everything up
front.

---

## Lecture 5, Design review, as code

**Module** `src/cse476/design.py`
A design linter that inspects an agent **before** it runs and reports problems:
`audit_tools` and `audit_guards` produce `Finding`s against an `AgentSpec`, and
`report` prints them. This is the by hand ancestor of the schema checking that
Semantic Kernel does for you in Unit 3.

**Notebook** `notebooks/u1/l5_design_review.ipynb`

**Test** `tests/mock_run_l5.py`

```bash
python tests/mock_run_l5.py
jupyter notebook notebooks/u1/l5_design_review.ipynb
```

Leave with: you can catch a whole class of agent bugs by inspecting the design
before you ever spend a token running it.

---

## Run all of Unit 1 at once

```bash
for f in mock_run mock_run_l2 mock_run_l3 mock_run_l4 mock_run_l5; do
  echo "== $f =="; python tests/$f.py | tail -1
done
```

Every line should read `ALL PASS`. If one does not, your environment is not set
up correctly; go back to `RUN_THIS_PROJECT.md` section 1 and
`docs/TROUBLESHOOTING.md`.

---

## What you can do after Unit 1

You can build an agent from nothing: a loop, tools, memory, planning, and a
design check, all by hand. You do not yet know how to make it reliable when
tools fail or inputs are messy. That is Unit 2. And you have not touched a
framework yet, on purpose, because now you know exactly what a framework will be
doing for you when you meet one in Unit 3.
