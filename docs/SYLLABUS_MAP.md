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
| Semantic Kernel fundamentals | U3 L1, L2 | P4, P5 |
| AutoGen framework | U3 L1, L5 | P6 |
| Bot Framework integration | U3 L1 | |
| Asynchronous workflows | U3 L3 | P4 |
| Memory management | U3 L4 | P5 |
| State handling | U3 L4 | P5 |
| Prompt templates | U3 L2 | P4 |
| Retrieval augmented generation | U3 L4 | P8 |
| Integration of external tools | U3 L2, L3 | P4 |
| Building modular AI systems | U3 L3 | |
| Framework based enterprise development | U3 L3 | |

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

| Syllabus phrase | Where | Practical |
|---|---|---|
| Introduction to multi agent systems | U4 | P7 |
| Planner executor architectures | U4 | P7 |
| Collaborative agents | U4 | P7 |
| Inter agent communication | U4 | P7 |
| Task delegation | U4 | P7 |
| Distributed problem solving | U4 | |
| Orchestration patterns | U4 | P7 |
| Agent coordination mechanisms | U4 | P7 |
| Collaborative enterprise workflows | U4 | P7 |
| Role based agents | U4 | P6, P7 |
| Scalable AI collaboration strategies | U4 | |
| Workflow optimisation for multi agent | U4 | |

## Unit 5, Testing, Monitoring and Deployment

| Syllabus phrase | Where | Practical |
|---|---|---|
| Testing AI agent workflows | U5 | P9 |
| Debugging techniques | U5 | P9 |
| Observability and monitoring | U5 | P9 |
| Telemetry collection | U5 | P9 |
| Hallucination detection | U5 | P8 |
| Validation methods | U5 | P8 |
| Deployment strategies | U5 | P10 |
| Cloud deployment on Azure | U5 | P10 |
| API deployment | U5 | P10 |
| CI/CD integration | U5 | P10 |
| Scalability considerations | U5 | |
| Performance optimisation | U5 | P9 |
| Production ready AI agent systems | U5 | P10 |

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
