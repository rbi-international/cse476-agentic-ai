# Syllabus map

Every approved syllabus topic, and where in this repository it is taught and
assessed. Use this when you are revising and want to find the code for a topic
you only know by its syllabus name.

## Unit 1, Foundations of AI Agents and Microsoft Foundry

| Syllabus phrase | Where | Practical |
|---|---|---|
| Introduction to AI agents | U1 L1 | P1 |
| Intelligent agent architectures | U1 L2 | |
| Reactive and goal based agents | U1 L2 | |
| Perception and action models | U1 L2 | |
| Conversational AI fundamentals | U1 L3 | P2 |
| Planning and reasoning | U1 L4 | |
| Introduction to Azure AI Foundry | U1 L6 | P1, P2 |
| AI agent lifecycle | U1 L5 | |
| Prompt engineering basics | U1 L7 | P2 |
| AI services in Azure | U1 L6 | P1 |
| Agent design principles | U1 L5 | |
| Use cases of enterprise AI agents | U1 L8 | |
| Overview of Microsoft AI ecosystem | U1 L8 | |

## Unit 2, Building Intelligent Agent Workflows

| Syllabus phrase | Where | Practical |
|---|---|---|
| Agent workflows and orchestration | U2 L1, L4 | P3 |
| Task automation | U2 L1, L4 | P3 |
| Tool calling mechanisms | U2 L2 | P3, P4 |
| API integration | U2 L3 | P3 |
| Workflow chaining | U2 L4 | P3 |
| Event driven AI systems | U2 L4 | |
| Conversational workflows | U2 L5 | |
| Service integration | U2 L3 | P3 |
| Autonomous execution pipelines | U2 L4 | P3 |
| Context aware agents | U2 L5 | P5 |
| Workflow testing | U2 L5 | |
| Deployment basics | U2 L3, and Unit 5 | |
| AI powered automation in enterprise | U2 L1, L4 | P3 |

## Unit 3, Agent Development with Python and Frameworks

| Syllabus phrase | Where | Practical |
|---|---|---|
| Python programming for AI agents | U3 L1 | P4 |
| Semantic Kernel fundamentals | U3 L2 (real `kernel.py`) | P4, P5 |
| AutoGen framework | U3 L1, L5 (graph successor) | P6, P7 |
| Bot Framework integration | U3 L1 | |
| Asynchronous workflows | U3 L3 | P4 |
| Memory management | U3 L4 (real sessions) | P5 |
| State handling | U3 L4 | P5 |
| Prompt templates | U3 L2, L4 (RAG prompt) | P4 |
| Retrieval augmented generation | U3 L4 (real `rag.py`) | P8 |
| Integration of external tools | U3 L2, L3 (plain-function tools) | P4 |
| Building modular AI systems | U3 L3, L5 (agent-as-tool, graph) | P7 |
| Framework based enterprise development | U3 L3 | |

**What each Unit 3 lecture actually builds.** Every lecture uses the real
packages, not mock stand-ins: `agent-framework-core`, `agent-framework-openai`,
and `semantic-kernel`.

- **L1, Framework Landscape.** The merger, the lineage, the competitor map, and
  the `pip show` import trap. Module `frameworks.py`.
- **L2, Semantic Kernel Foundations.** Real `Kernel`, real `@kernel_function`
  plugins, invoked with no model to show the plugin layer is testable offline.
  Module `kernel.py`.
- **L3, Building on Agent Framework.** A shippable agent in three lines, tools as
  plain functions, async as mechanism. Module `agent_fw.py`.
- **L4, Memory and Retrieval.** Real sessions for memory, and RAG built from
  scratch: chunk, embed, cosine search, all offline behind an embedder seam.
  Module `rag.py`.
- **L5, Multi-Agent, the Graph Model.** The agent-as-tool manager, then a real
  `WorkflowBuilder` graph that runs offline and routes deterministically. The
  conversation-to-graph shift that defines the merger. Module `multi_agent.py`.

**Important note on the frameworks named in this unit.** The syllabus names
Semantic Kernel, AutoGen, and Bot Framework. All three changed status in 2026,
so this unit teaches them honestly rather than pretending they are current.

- **Semantic Kernel and AutoGen merged into Microsoft Agent Framework 1.0** on
  3 April 2026. Both are now in maintenance mode, bug fixes only, no new
  features. Semantic Kernel survives as the foundation layer of the new
  framework, so its kernel, plugin, and connector concepts are still exactly
  what you learn. AutoGen's multi-agent ideas were rebuilt on a graph-based
  model in the new framework, which Unit 4 uses. We teach what each framework
  was, why they merged, and then build on Agent Framework, because that is the
  production path today and what an interviewer expects a candidate to know.
- **Bot Framework SDK reached end of support** in December 2025 and its
  repository is archived. The syllabus outcome, connecting an agent to a
  conversational channel, is taught using the Microsoft 365 Agents SDK, its
  stated replacement. The retirement is covered as a short case study in SDK
  lifecycle risk, which is itself an interview-worthy topic.

The teaching principle for the whole unit: learn the lineage, understand the
merger, build on the successor. That sequence covers every syllabus phrase and
leaves you able to reason about the current landscape, including the competitors
an interviewer will raise: LangGraph, CrewAI, the community AG2 fork, and the
Claude Agent SDK.

## Unit 4, Multi Agent Systems and Collaboration

| Syllabus phrase | Lecture | Module |
|---|---|---|
| Introduction to multi agent systems | L1 | orchestration |
| Orchestration patterns | L1 | orchestration |
| Distributed problem solving | L1 | orchestration |
| Inter agent communication | L2, L4 | routing, blackboard |
| Agent coordination mechanisms | L2 | routing |
| Task delegation | L3 | manager |
| Planner executor architectures | L3 | manager |
| Role based agents | L3 | manager |
| Collaborative agents | L4 | blackboard |
| Collaborative enterprise workflows | L4, L5 | blackboard, triage_system |
| Scalable AI collaboration strategies | L5 | triage_system |
| Workflow optimisation for multi agent | L5 | triage_system |

**What each Unit 4 lecture actually builds.** Every lecture uses the real
`agent-framework` package, and every module runs offline because the nodes are
plain functions writing to real workflow state.

- **L1, `orchestration.py`.** Fan-out and fan-in: one ticket to three reviewers
  in parallel, gathered by a fan-in that synchronises (a barrier that waits for
  all). Real `add_fan_out_edges` and `add_fan_in_edges`.
- **L2, `routing.py`.** A switch-case router: classify once, send to exactly one
  handler, with a required `Default`. Real `add_switch_case_edge_group`, `Case`,
  `Default`. Teaches that the framework enforces a default, and hand-rolled
  conditional edges silently drop unmatched work.
- **L3, `manager.py`.** The manager pattern: specialist agents wrapped with
  `as_tool`, a manager that delegates by judgement. The honest trade-off against
  fixed rules. Specialists and tool wiring run offline; the manager decision
  needs a lane.
- **L4, `blackboard.py`.** Shared state: agents read and append findings to a
  common board via `set_state` and `get_state`. Read-modify-write, and the
  overwrite bug when an agent forgets to read first.
- **L5, `triage_system.py`.** The finale: all four primitives composed into one
  system. Route to a team, fan out the checks onto a shared board, fan in, and
  decide. The blackboard is the connective tissue that makes composition work.

## Unit 5, Testing, Monitoring and Deployment

| Syllabus phrase | Lecture | Module |
|---|---|---|
| Testing AI agent workflows | L1 | testing_agents |
| Debugging techniques | L1 | testing_agents |
| Hallucination detection | L2 | validation |
| Validation methods | L2 | validation |
| Observability and monitoring | L3 | observability |
| Telemetry collection | L3 | observability |
| Performance optimisation | L1, L3 | testing_agents, observability |
| API deployment | L4 | serving |
| Production ready AI agent systems | L4, L5 | serving, deployment |
| Scalability considerations | L4, L5 | serving, deployment |
| Deployment strategies | L5 | deployment |
| Cloud deployment on Azure | L5 | deployment (Dockerfile, portable image) |
| CI/CD integration | L5 | deployment (real .github/workflows/ci.yml) |

**What each Unit 5 lecture builds.** Every module runs offline and is tested
deterministically, the same discipline the whole course uses.

- **L1, `testing_agents.py`.** The split: test the deterministic skeleton exactly,
  and the model-dependent part with a fake model behind a seam. Plus debugging:
  reproduce with a ReplayClient, isolate the layer with diagnose_route, and the
  reproduce-isolate-fix-lock-in recipe. The testing pyramid.
- **L2, `validation.py`.** Testing checks your code; validation checks the model's
  output. Three checks: structural (on the menu), grounding (traceable to the
  source, the heart of hallucination detection), and cross-check (a tool holds the
  truth). The validator as a gate.
- **L3, `observability.py`.** The three pillars: a trace (one run, timed, find the
  slow step), metrics (many runs, latency and failure rate), and structured logs
  (searchable). Metrics alert, logs locate, a trace explains.
- **L4, `serving.py`.** An API is a contract. A real FastAPI serves the agent with
  a typed request and response and a health endpoint, tested offline with a
  TestClient. The contract rejects malformed requests for free.
- **L5, `deployment.py`.** Shipping it: a Dockerfile packages the service to run
  anywhere, and a CI/CD pipeline of gates ships every change safely (a failing
  test stops the ship). A production-readiness checklist gathers the whole unit,
  and the real ci.yml has run on every push all along.

## Unit 6, Responsible AI, Security and Enterprise Governance

| Syllabus phrase | Where | Practical |
|---|---|---|
| Responsible AI principles | U6 | P6, P10 |
| Ethical AI systems | U6 | P6 |
| Enterprise governance | U6 | P10 |
| AI safety mechanisms | U6 | P6 |
| Prompt injection prevention | U6 | P10 |
| Authentication and authorisation | U6 | P10 |
| Azure security practices | U6 | P10 |
| Compliance and auditing | U6 | P10 |
| Secure deployment architectures | U6 | P10 |
| Risk mitigation | U6 | P10 |
| Monitoring AI behaviour | U6 | P9 |
| Enterprise AI governance models | U6 | |
| Secure multi agent systems | U6 | P7, P10 |
