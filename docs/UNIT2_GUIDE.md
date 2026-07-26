# Unit 2 guide, Building Reliable Agents

Unit 1 built an agent. Unit 2 makes it **survive the real world**: tools that
fail, APIs that lie, inputs that are messy, and the need to test something that
does not behave the same way twice. Still no framework; these are the reliability
skills a framework assumes you already have.

The running example from here on is **support ticket triage**: a ticket comes in,
it gets routed to a queue, and each queue has a service level agreement. Same
domain all the way through Unit 3, so your attention stays on the ideas.

Each lecture: a **module** in `src/cse476/`, a **notebook** in `notebooks/u2/`,
and a **test** in `tests/`. `conda activate cse476` first.

---

## Lecture 1, Workflow versus agency

**Module** `src/cse476/triage.py`
One problem in three shapes, so you learn when an agent is the wrong tool.
`triage_workflow` (fixed code, zero model calls), `triage_router` (one model
call to classify), and `triage_agent` (a full loop). `compare` runs all three on
the same ticket so you see the cost of each. `list_queues` and
`lookup_queue_policy` are the shared helpers.

**Notebook** `notebooks/u2/l1_workflow_vs_agency.ipynb`
**Test** `tests/mock_run_u2l1.py`

```bash
python tests/mock_run_u2l1.py
jupyter notebook notebooks/u2/l1_workflow_vs_agency.ipynb
```

Leave with: the same ticket routed to the same queue costs zero, one, or several
model calls depending on the shape you chose. Agency is powerful and expensive;
use it only where you need it.

---

## Lecture 2, Tool calling in depth

**Module** `src/cse476/tools.py`
What happens when a tool misbehaves, and how to defend against it. Four broken
weather tools model the four failure modes: `get_weather_that_throws`,
`_that_times_out`, `_that_returns_junk`, `_that_rate_limits`. `call_tool` wraps
any tool with four defences (whitelist, retry with backoff, catch, report), and
`run_with_tools` is the hardened loop.

**Notebook** `notebooks/u2/l2_tool_calling.ipynb`
**Test** `tests/mock_run_u2l2.py`

```bash
python tests/mock_run_u2l2.py
jupyter notebook notebooks/u2/l2_tool_calling.ipynb
```

Leave with: the nastiest failure is not a crash, it is a tool that **lies**,
returning junk that looks like a real answer. Defending against that is the job.

---

## Lecture 3, API integration

**Module** `src/cse476/api.py`
Turning a real, messy API into a tool an agent can trust. `HttpClient` puts the
network behind a `Transport` seam (so you can test offline), distinguishes real
errors (401 versus 429 versus 503), and `weather_api_tool` wraps the raw API,
Kelvin, codes, nested JSON, into one clean sentence. `FakeTransport` lets you
test every failure without a network.

**Notebook** `notebooks/u2/l3_api_integration.ipynb`
**Test** `tests/mock_run_u2l3.py`

```bash
python tests/mock_run_u2l3.py
jupyter notebook notebooks/u2/l3_api_integration.ipynb
```

Leave with: wrap a messy API in a clean tool (an anti corruption layer), and put
the network behind a seam so you can test every fault offline.

---

## Lecture 4, Workflow chaining and events

**Module** `src/cse476/pipeline.py`
Chaining named steps into a `Pipeline` that threads state, stops on failure but
keeps the work already done, and logs every step (`RunLog`). The four intake
steps are `validate_ticket`, `classify_ticket`, `enrich_ticket`,
`assign_ticket`. `EventBus` shows the other shape: emit events, and one broken
handler does not silence the rest.

**Notebook** `notebooks/u2/l4_workflow_chaining.ipynb`
**Test** `tests/mock_run_u2l4.py`

```bash
python tests/mock_run_u2l4.py
jupyter notebook notebooks/u2/l4_workflow_chaining.ipynb
```

Leave with: a pipeline is a chain of steps that stops cleanly on failure. This is
the by hand ancestor of the graph you build in Unit 3 Lecture 5.

---

## Lecture 5, Context and testing

**Module** `src/cse476/context.py`
Carrying context across turns, and testing something that will not sit still. A
`Session` holds a bounded transcript plus pinned facts, `ContextAgent` resolves
references like "it", and the invariant checkers (`check_invariants`,
`queue_is_valid`, `field_present`, `field_in`) test by properties rather than
exact strings, because a model's exact words vary.

**Notebook** `notebooks/u2/l5_context_and_testing.ipynb`
**Test** `tests/mock_run_u2l5.py`

```bash
python tests/mock_run_u2l5.py
jupyter notebook notebooks/u2/l5_context_and_testing.ipynb
```

Leave with: you cannot test a model by exact match, because its words vary. You
test by **invariants**: properties that must hold no matter the exact wording.

---

## Run all of Unit 2 at once

```bash
for n in 1 2 3 4 5; do
  echo "== u2l$n =="; python tests/mock_run_u2l$n.py | tail -1
done
```

Every line should read `ALL PASS`.

---

## What you can do after Unit 2

You can build an agent that stays standing when tools fail, APIs lie, and inputs
are messy, and you can test it honestly. You have done all of this by hand. In
Unit 3 you meet the frameworks that package these exact patterns, and because you
built them yourself, you will recognise every piece a framework hands you.
