"""
Building a real agent on Microsoft Agent Framework.

Unit 3 Lecture 3. Two lectures of foundation, now the payoff: a real agent on
the successor framework, the one you would actually ship. This uses the real
agent-framework package.

The pleasant surprise of this framework: a tool is just a plain Python function
with type hints and a docstring. You pass it to the agent and the framework
reads the schema off the signature. No decorator, no schema dict, no class. It
is the cleanest expression yet of the tool idea you built by hand in Unit 1.

    triage_tools        plain functions, the agent's tools, testable alone
    build_support_agent a real ChatAgent with instructions and tools
    the mapping: everything here has a hand-built twin from Units 1 and 2

The tools run offline (they are plain functions). Building the agent needs the
package. Running the agent needs a lane, because that is a live model call.
"""

from __future__ import annotations

import os
from typing import Annotated, Any


# ---------------------------------------------------------------- the tools

# WHY plain functions with type hints: this is Agent Framework's tool model, and
# it is the simplest of the three you have seen. Unit 1 was a REGISTRY dict plus
# a hand-written TOOL_SCHEMA. Semantic Kernel was a decorated class. Here a tool
# is just a documented function. The framework reads the name from the function
# name, the description from the docstring, and the parameters from the type
# hints. One thing, no duplication.

QUEUES = ["billing", "technical", "account", "sales", "abuse"]
_SLA = {"billing": 24, "technical": 4, "account": 12, "sales": 48, "abuse": 1}


def classify_ticket(
    text: Annotated[str, "The full text of the support ticket."],
) -> str:
    """Decide which support queue a ticket belongs in, from its text."""
    low = text.lower()
    rules = [
        ("abuse", ("spam", "hacked", "security")),
        ("billing", ("charged", "refund", "invoice", "money")),
        ("account", ("login", "password", "locked")),
        ("sales", ("upgrade", "pricing", "quote")),
        ("technical", ("error", "bug", "broken", "not working")),
    ]
    for queue, words in rules:
        if any(w in low for w in words):
            return f"This ticket belongs in the {queue} queue."
    return "No rule matched; route to technical for a human to sort."


def get_sla(
    queue: Annotated[str, "The queue name, for example 'billing'."],
) -> str:
    """Get the service level agreement in hours for a support queue."""
    hours = _SLA.get(queue.strip().lower())
    if hours is None:
        return f"No SLA on file for '{queue}'."
    return f"The {queue} queue has a {hours} hour SLA."


def list_queues() -> str:
    """List every support queue a ticket can be routed to. Takes no arguments."""
    return "Queues: " + ", ".join(QUEUES)


# The tools as a plain list. This is the whole tool suite, and every function in
# it can be unit tested on its own, with no framework and no model.
TRIAGE_TOOLS = [classify_ticket, get_sla, list_queues]


# ---------------------------------------------------------------- the agent

SUPPORT_INSTRUCTIONS = (
    "You are a support triage assistant. Given a ticket, use your tools to "
    "classify it into a queue and report the SLA for that queue. Be concise. "
    "If a tool tells you something failed or has no data, say so plainly rather "
    "than guessing."
)


def build_support_agent(client: Any) -> Any:
    """
    A real support agent on Microsoft Agent Framework.

    Read the three arguments and recognise them: instructions is your system
    prompt from Lecture 3, tools is your REGISTRY from Unit 1, and the client is
    your connector, your lane. as_agent assembles them into the thing that, in
    Unit 1, took you forty lines of loop to write by hand.

    The client is passed in rather than built here so the caller controls the
    lane, and so this function can be reasoned about without a live connection.
    """
    return client.as_agent(
        name="support_triage",
        instructions=SUPPORT_INSTRUCTIONS,
        tools=TRIAGE_TOOLS,
    )


def make_client() -> Any:
    """
    Build the Agent Framework chat client from the same env vars as our lanes.

    Kept separate from build_support_agent so the agent builder stays lane
    agnostic. This is the only piece that reaches out, so it is the only piece
    that needs credentials.
    """
    from agent_framework.openai import OpenAIChatClient

    return OpenAIChatClient(
        model=os.environ.get("MODEL", "openai/gpt-4.1-mini"),
        api_key=os.environ["GITHUB_TOKEN"],
        base_url="https://models.github.ai/inference",
    )


# ---------------------------------------------------------------- the mapping

# The point of the whole course, one more time: nothing in the framework is a new
# idea. Each framework concept on the left is something you built on the right.
AGENT_FRAMEWORK_MAP: dict[str, str] = {
    "OpenAIChatClient": "your get_client from lanes.py, the connection to a model",
    "as_agent(instructions=...)": "your system prompt, from Unit 1 Lecture 3",
    "tools=[functions]": "your REGISTRY, but the schema is read from the function",
    "await agent.run(...)": "your whole for-step-in-range loop from Unit 1",
    "AgentSession": "your Session from Unit 2 Lecture 5, memory across turns",
    "middleware": "your defended call_tool from Unit 2 Lecture 2",
    "agent.as_tool()": "an agent used as another agent's tool, the seed of Unit 4",
}


def async_matters() -> dict[str, str]:
    """
    Why agent.run is awaited, explained as a fact the notebook can show.

    Unit 1's loop was synchronous: each model call blocked until it returned.
    Real agent frameworks are async, because an agent often waits on the network,
    and while it waits, other work can proceed. await is how you say 'pause here
    until this returns, but let other things run meanwhile'. It is not
    decoration; it is what lets one process handle many agents without one slow
    call freezing all of them.
    """
    return {
        "unit_1": "synchronous: client.chat.completions.create(...) blocks",
        "framework": "async: await agent.run(...) yields while it waits",
        "why": "an agent mostly waits on the network; async frees that wait",
        "cost_of_ignoring": "a sync agent handles one request at a time; async scales",
    }
