# Unit 3 guide, Agent Development with Python and Frameworks

Now the frameworks, for real. Every module in this unit runs against the actual
packages the industry uses: `agent-framework-core`, `agent-framework-openai`, and
`semantic-kernel`. Nothing here is a mock stand in.

A theme you will notice: **a surprising amount runs offline, with no model.**
Plugin functions, graph nodes, and retrieval mechanics are ordinary code the
framework dispatches, so you can test them without spending a token. Only the
steps where a model actually decides or generates need a lane. Each lecture below
says which parts are which.

The frameworks story in one line: on 3 April 2026, Semantic Kernel and AutoGen
merged into Microsoft Agent Framework. We learn the lineage, understand the
merger, and build on the successor. `docs/SYLLABUS_MAP.md` has the full history.

Each lecture: a **module** in `src/cse476/`, a **notebook** in `notebooks/u3/`,
and a **test** in `tests/`. `conda activate cse476` first.

---

## Lecture 1, The framework landscape

**Module** `src/cse476/frameworks.py`
The map. `describe_landscape` records six frameworks and their real status
(Agent Framework current, Semantic Kernel and AutoGen maintenance, AG2 the fork,
LangGraph and CrewAI the competitors). `CONCEPT_MAP` shows the same idea across
frameworks, and `ImportTrap` captures the `pip show` gotcha that tells old
package names from current ones.

**Notebook** `notebooks/u3/l1_framework_landscape.ipynb`
**Test** `tests/mock_run_u3l1.py` (all offline)

```bash
python tests/mock_run_u3l1.py
jupyter notebook notebooks/u3/l1_framework_landscape.ipynb
```

Leave with: you can explain the merger, place every framework, and avoid the
import trap. This is interview knowledge.

---

## Lecture 2, Semantic Kernel foundations

**Module** `src/cse476/kernel.py`
Real Semantic Kernel. `build_kernel` creates an actual `Kernel` with two plugins
(`WeatherPlugin`, `TicketPlugin`) whose methods are decorated with
`@kernel_function`. The key surprise: `invoke_directly` calls a plugin function
**with no model**, because the model only chooses which function to call, the
calling is ordinary code. `function_metadata` shows the schema the framework
generated from your type hints.

**Offline:** building the kernel, registering plugins, invoking functions,
reading the generated schema. **Needs a lane:** letting the model choose a
function (the last notebook cell).

**Notebook** `notebooks/u3/l2_semantic_kernel.ipynb`
**Test** `tests/mock_run_u3l2.py` (all offline)

```bash
python tests/mock_run_u3l2.py
jupyter notebook notebooks/u3/l2_semantic_kernel.ipynb
```

Leave with: a plugin is a decorated class, its schema is generated not written,
and the whole plugin layer is testable with no model.

---

## Lecture 3, Building on Agent Framework

**Module** `src/cse476/agent_fw.py`
A real, shippable agent. The tools (`classify_ticket`, `get_sla`, `list_queues`)
are **plain functions**, the simplest tool model you will see. `build_support_agent`
assembles a real agent in three arguments: client, instructions, tools.
`AGENT_FRAMEWORK_MAP` ties every framework word to the hand built code it
replaces.

**Offline:** the tools (they are plain functions), building the agent, reading
the mapping. **Needs a lane:** running the agent (`await agent.run(...)`), a live
model call.

**Notebook** `notebooks/u3/l3_agent_framework.ipynb`
**Test** `tests/mock_run_u3l3.py` (tools and construction offline)

```bash
python tests/mock_run_u3l3.py
jupyter notebook notebooks/u3/l3_agent_framework.ipynb
```

Leave with: a tool is just a documented function, an agent is three arguments,
and `await agent.run` is your entire Unit 1 loop, handled.

---

## Lecture 4, Memory, state, and retrieval

**Module** `src/cse476/rag.py`
Two fixes. Memory comes from the framework's session (shown in the notebook).
Retrieval is built from scratch here: `chunk_text`, an `Embedder` seam with a
`HashingEmbedder` for offline testing, `cosine_similarity`, and a `RagStore`
that embeds documents and searches them by meaning. `build_rag_prompt` and
`answer_with_context` complete the retrieve then generate shape.

**Offline:** chunking, embedding with the toy embedder, cosine search, ranking,
the whole retrieval layer. **Needs a lane:** the real embedder and the final
answer.

**Notebook** `notebooks/u3/l4_memory_and_rag.ipynb`
**Test** `tests/mock_run_u3l4.py` (retrieval mechanics offline)

```bash
python tests/mock_run_u3l4.py
jupyter notebook notebooks/u3/l4_memory_and_rag.ipynb
```

Leave with: do not ask the model to know your facts, retrieve them and ask it to
read. Retrieval is chunk, embed, cosine search, and it is all arithmetic until
the final answer.

---

## Lecture 5, Multi-agent systems, the graph model

**Module** `src/cse476/multi_agent.py`
Two multi agent shapes. `build_manager` is the simple one: a manager agent that
delegates to specialist agents handed to it as tools. `build_triage_graph` is the
real one: an actual Agent Framework `WorkflowBuilder` graph with three executor
nodes (`classify_node`, `enrich_node`, `assign_node`). `conversation_vs_graph`
states the shift that defines the merger.

**Offline:** the entire graph. `run_triage_graph` builds and runs the real graph
with no model, deterministically, because the nodes are plain functions.
**Needs a lane:** the manager (its specialists are model backed agents).

**Notebook** `notebooks/u3/l5_multi_agent.ipynb`
**Test** `tests/mock_run_u3l5.py` (the graph runs fully offline)

```bash
python tests/mock_run_u3l5.py
jupyter notebook notebooks/u3/l5_multi_agent.ipynb
```

Leave with: the AutoGen model was a conversation you hoped converged; Agent
Framework is a graph you can see, test, and trust. That shift is the heart of the
merger.

---

## Run all of Unit 3 at once

```bash
for n in 1 2 3 4 5; do
  echo "== u3l$n =="; python tests/mock_run_u3l$n.py | tail -1
done
```

Every line should read `ALL PASS`. Note that these tests use the real frameworks,
so this also confirms `agent-framework-core`, `agent-framework-openai`, and
`semantic-kernel` installed correctly.

---

## Running the live cells against Foundry

The notebook cells marked as needing a lane make a real model call. Run them on
whatever lane you have set, and prefer Foundry once your account is ready: set
`PROVIDER=foundry` in `.env` per `docs/FOUNDRY_SETUP.md`, and the exact same
notebook cells now run on Microsoft Foundry with no code change. That is the
lane design paying off, and it is the setup you will use in a real job.

---

## What you can do after Unit 3

You can build on the real, current frameworks: a shippable agent, real memory,
retrieval from scratch, and a real multi agent graph that runs and is testable.
You understand the merger well enough to explain it. Unit 4 makes multi agent
systems the main subject, where the graph model you just met earns its keep at
scale.
