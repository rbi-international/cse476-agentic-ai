"""
The manager pattern: when the decision itself becomes an agent.

Unit 4 Lecture 3. Last lecture, routing sent work to the right specialist using
rules you wrote: if the queue is billing, go to billing. That is fast, cheap, and
completely predictable. But it can only route on what your rules can see. A ticket
that says "the thing I paid for keeps logging me out" is really billing and
account and technical at once, and no keyword rule handles that cleanly.

So we let the decision be an agent. A manager agent reads the request, and in its
own judgement decides which specialist to hand it to, using the agent-as-tool idea
from Unit 3: each specialist is an agent, wrapped as a tool the manager can call.

    build_specialists     the specialist agents, each an expert at one thing
    build_manager         a manager whose tools are those specialists
    the trade: judgement versus rules, and when each is right

The specialists and the tool wiring are inspectable offline. The manager's actual
decision needs a lane, because deciding is what the model does. That is the point:
you are paying a model to make a judgement a rule could not.
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------- the specialists

# WHY separate specialist agents instead of one big agent: each specialist has a
# narrow, focused instruction, which makes it better at its one job and easier to
# reason about. A billing specialist that only knows billing gives better billing
# answers than a generalist juggling everything. This is the same specialise then
# compose idea behind the whole unit, now applied to agents themselves.

SPECIALIST_INSTRUCTIONS: dict[str, str] = {
    "billing": (
        "You are a billing specialist. You handle charges, refunds, invoices, and "
        "payment questions. Answer only billing matters. If a request is not about "
        "billing, say it belongs to another team."
    ),
    "technical": (
        "You are a technical support specialist. You handle errors, bugs, crashes, "
        "and outages. Answer only technical matters. If a request is not technical, "
        "say it belongs to another team."
    ),
    "account": (
        "You are an account specialist. You handle logins, passwords, locked "
        "accounts, and profile changes. Answer only account matters. If a request "
        "is not about accounts, say it belongs to another team."
    ),
}


def build_specialists(client: Any) -> dict[str, Any]:
    """
    Build the three specialist agents, one per domain.

    Each is an ordinary agent with a narrow instruction. They are named because
    as_tool needs a name to identify each one when the manager calls it.
    """
    return {
        name: client.as_agent(name=f"{name}_specialist", instructions=instruction)
        for name, instruction in SPECIALIST_INSTRUCTIONS.items()
    }


def specialist_tools(specialists: dict[str, Any]) -> list[Any]:
    """
    Wrap each specialist agent as a tool the manager can call.

    This is the agent-as-tool primitive from Unit 3, doing real work now. Each
    tool gets a name and a description, and that description is what the manager
    reads to decide which specialist fits the request. As always in this course,
    the description is an instruction to the model, not documentation, so it is
    written to help the manager choose well.
    """
    descriptions = {
        "billing": "Ask the billing specialist about charges, refunds, or invoices.",
        "technical": "Ask the technical specialist about errors, bugs, or outages.",
        "account": "Ask the account specialist about logins, passwords, or lockouts.",
    }
    return [
        agent.as_tool(name=f"ask_{name}", description=descriptions[name])
        for name, agent in specialists.items()
    ]


# ---------------------------------------------------------------- the manager

MANAGER_INSTRUCTIONS = (
    "You are a support manager. You do not answer questions yourself. You read "
    "each request, decide which specialist is the right fit, and delegate to them "
    "by calling their tool. If a request spans several areas, delegate to the "
    "specialist who owns the core of the problem, or consult more than one. Return "
    "the specialist's answer to the customer."
)


def build_manager(client: Any) -> Any:
    """
    A manager agent whose tools are the specialist agents.

    The manager makes the delegation decision the way L2's classifier did, but by
    judgement rather than rules. It reads the request, weighs the specialist tool
    descriptions, and picks. Where a keyword rule sees only words, the manager can
    read intent, which is exactly what you are paying the model for.
    """
    specialists = build_specialists(client)
    return client.as_agent(
        name="support_manager",
        instructions=MANAGER_INSTRUCTIONS,
        tools=specialist_tools(specialists),
    )


def make_client() -> Any:
    """The Agent Framework client for the active lane. Only this reaches out."""
    import os

    from agent_framework.openai import OpenAIChatClient

    return OpenAIChatClient(
        model=os.environ.get("MODEL", "openai/gpt-4.1-mini"),
        api_key=os.environ["GITHUB_TOKEN"],
        base_url="https://models.github.ai/inference",
    )


# ---------------------------------------------------------------- the trade-off

MANAGER_MAP: dict[str, str] = {
    "manager agent": "the classifier from L2, but deciding by judgement not rules",
    "specialist agent": "a narrow expert, better at one job than a generalist",
    "as_tool": "wraps a specialist agent as something the manager can call",
    "the tool description": "what the manager reads to choose; an instruction, not docs",
    "delegation": "the manager calls one specialist tool, gets its answer, returns it",
    "the cost": "a model call to decide, and the manager can choose wrong",
}


def rules_vs_manager() -> dict[str, str]:
    """
    Fixed routing versus a thinking manager, stated for an interview.

    Neither is better in general. Rules are fast, free, and predictable, but blind
    to anything they were not written to see. A manager reads intent and handles
    the messy cases, but it costs a model call and can make a mistake a rule never
    would. The skill is choosing: rules for clear, high-volume routing; a manager
    for ambiguous requests where judgement earns its cost.
    """
    return {
        "fixed_routing": "fast, free, predictable; blind beyond its keywords",
        "manager_agent": "reads intent, handles ambiguity; costs a call, can err",
        "use_rules_when": "the routing is clear and high volume, and mistakes are cheap",
        "use_manager_when": "requests are ambiguous and getting the right expert matters",
        "the_honest_risk": "a manager can delegate to the wrong specialist; a rule cannot surprise you",
    }
