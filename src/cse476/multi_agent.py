"""
Many agents: delegation, and the graph model.

Unit 3 Lecture 5, the finale of the unit. In Lecture 3 you saw the door: an
agent can be another agent's tool. Today you walk through it, twice.

First, the simple multi-agent shape: a manager agent that delegates to
specialist agents, each handed to it as a tool. Easy, and often enough.

Then the harder, more powerful shape, and the real point of the lecture: the
graph model. AutoGen's old idea was agents holding a conversation and hoping it
converged. Agent Framework replaces that with a graph you draw explicitly:
nodes do work, edges say what happens next. Control flow you can see, test, and
reason about, instead of a conversation you hope goes right.

    build_manager        the agent-as-tool pattern, a manager over specialists
    build_triage_graph   a real Agent Framework graph, runnable with no model
    the conversation-to-graph shift, made concrete

The graph of plain-function nodes runs offline, no model, so its structure is
fully testable. The manager and any agent-backed node need a lane.
"""

from __future__ import annotations

from typing import Any

from agent_framework import WorkflowBuilder, WorkflowContext, executor


# ---------------------------------------------------------------- 1. agent as tool

MANAGER_INSTRUCTIONS = (
    "You are a support manager. You have specialist agents available as tools: "
    "a triage specialist and a billing specialist. Delegate each request to the "
    "right specialist and return their answer. Do not try to answer yourself."
)


def build_manager(client: Any) -> Any:
    """
    A manager agent that delegates to specialist agents handed to it as tools.

    This is the simplest multi-agent shape and it is the L3 seed made real. Each
    specialist is an ordinary agent; as_tool() turns it into something the
    manager can call exactly like any function tool. The manager decides who
    handles what. Every agent here needs a name so as_tool can identify it.
    """
    triage = client.as_agent(
        name="triage_specialist",
        instructions="You classify a support ticket into one queue and explain why.",
    )
    billing = client.as_agent(
        name="billing_specialist",
        instructions="You answer billing questions: refunds, invoices, charges.",
    )
    return client.as_agent(
        name="support_manager",
        instructions=MANAGER_INSTRUCTIONS,
        tools=[triage.as_tool(), billing.as_tool()],
    )


# WHY the agent-as-tool shape has a ceiling: the manager holds the whole plan in
# its own head, as one model deciding every hop. That is fine for two or three
# specialists and a simple flow. But when the flow has real structure, steps
# that must happen in order, branches, work that fans out and rejoins, you want
# that structure written down and enforced, not left to a model to remember.
# That is what the graph gives you.


# ---------------------------------------------------------------- 2. the graph

# Each node is a plain async function decorated as an executor. It receives a
# message and a context, does its work, and sends a message onward or yields the
# final output. No model is involved in THESE nodes, which is why the whole graph
# is testable offline. In a real system some nodes would be agents; the point of
# the lecture is the structure, so we keep the nodes as ordinary code.

VALID_QUEUES = ["billing", "technical", "account", "abuse"]
_SLA = {"billing": 24, "technical": 4, "account": 12, "abuse": 1}


@executor(id="classify")
async def classify_node(ticket: str, ctx: WorkflowContext[str]) -> None:
    """Node one: decide the queue from the ticket text, then send it onward."""
    low = ticket.lower()
    rules = [
        ("abuse", ("spam", "hacked", "security")),
        ("billing", ("charged", "refund", "invoice", "money")),
        ("account", ("login", "password", "locked")),
        ("technical", ("error", "bug", "broken", "outage")),
    ]
    queue = "technical"
    for name, words in rules:
        if any(w in low for w in words):
            queue = name
            break
    await ctx.send_message(queue)


@executor(id="enrich")
async def enrich_node(queue: str, ctx: WorkflowContext[str]) -> None:
    """Node two: attach the SLA. Receives the queue that node one sent."""
    hours = _SLA.get(queue, 4)
    await ctx.send_message(f"{queue}:{hours}")


@executor(id="assign")
async def assign_node(payload: str, ctx: WorkflowContext) -> None:
    """Node three, terminal: produce the assignment as the workflow output."""
    queue, hours = payload.split(":")
    priority = "urgent" if queue == "abuse" else "normal"
    await ctx.yield_output(
        f"Assigned to {queue}-team, {hours}h SLA, priority {priority}."
    )


def build_triage_graph():
    """
    A real Agent Framework graph: classify, then enrich, then assign.

    Read the edges and you can see the entire control flow at a glance, which is
    the whole advantage over a conversation. The structure is explicit and
    fixed: this node, then that node, then done. Compare the pipeline you built
    by hand in Unit 2 Lecture 4; this is the same idea, now a first-class graph
    the framework runs, with the door open to branches and fan-out that a plain
    pipeline could not express as cleanly.
    """
    return (
        WorkflowBuilder(start_executor=classify_node)
        .add_edge(classify_node, enrich_node)
        .add_edge(enrich_node, assign_node)
        .build()
    )


async def run_triage_graph(ticket: str) -> str:
    """Run the graph on a ticket and return its single output. No model needed."""
    workflow = build_triage_graph()
    result = await workflow.run(ticket)
    outputs = result.get_outputs()
    return outputs[0] if outputs else "no output produced"


# ---------------------------------------------------------------- the mapping

# The last mapping of the unit: the graph model, tied to what you already built.
GRAPH_MAP: dict[str, str] = {
    "Executor / node": "one step of work, like a step in your Unit 2 Pipeline",
    "Edge": "the 'what happens next' you wrote as pipeline order",
    "WorkflowBuilder": "your Pipeline builder, now a real graph you can branch",
    "ctx.send_message": "passing state to the next step, your Pipeline state dict",
    "ctx.yield_output": "the pipeline's final return value",
    "fan-out / fan-in": "one input to many workers and back, new with the graph",
}


def conversation_vs_graph() -> dict[str, str]:
    """
    The shift that defines the AutoGen to Agent Framework migration, as facts.

    This is the single most important idea for an interview about the merger:
    the old model was agents talking until they converged; the new model is an
    explicit graph. State it clearly and you sound like someone who understands
    why the frameworks changed, not just which one is current.
    """
    return {
        "autogen_old": "agents hold a conversation and you hope it converges",
        "agent_framework_new": "an explicit graph: nodes do work, edges route",
        "why_it_changed": "a graph is inspectable, testable, and reproducible; "
        "a free conversation is none of those",
        "the_cost": "the graph is more to set up, but you can see and trust it",
    }
