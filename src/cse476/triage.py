"""
One problem, three shapes.

Unit 2 Lecture 1. The whole unit turns on a single decision: when is something
an agent, and when is a plain workflow or a router the better answer. So this
module solves the identical support-ticket problem three ways, and the point is
the diff between them.

    workflow   fixed steps, same order every time, model fills in content
    router     one model decision picks a branch, then ordinary code runs
    agent      the model decides the whole path from what it observes

The lesson is not that the agent is best. It is that two of these three are
usually the right engineering choice, and choosing the agent when a router
would do is a mistake that costs money, latency and reliability.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable

# ---------------------------------------------------------------- the world

# A tiny knowledge base the triage system can look things up in. In a real
# system this is a database or an API. Here it is a dict, so the lesson stays
# about control flow rather than infrastructure.
QUEUES = ["billing", "technical", "account", "sales", "abuse"]

KB = {
    "billing": "Billing issues: refunds, wrong charges, invoices. SLA 24h.",
    "technical": "Technical issues: outages, bugs, errors. SLA 4h.",
    "account": "Account issues: login, password, profile. SLA 12h.",
    "sales": "Sales: upgrades, new plans, quotes. SLA 48h.",
    "abuse": "Abuse: spam, security, policy violations. SLA 1h, escalate.",
}

# A few sample tickets, including deliberately awkward ones.
SAMPLE_TICKETS = {
    "easy": "I was charged twice for my subscription this month.",
    "ambiguous": "Nothing works and I want my money back.",
    "urgent": "Someone has logged into my account and is sending spam from it.",
    "vague": "hello",
}


def lookup_queue_policy(queue: str) -> str:
    """The policy and SLA for one queue. Says nothing about which queue to pick."""
    return KB.get(queue, f"No policy on file for queue '{queue}'.")


def list_queues() -> str:
    """Every queue a ticket can be routed to. Takes no arguments."""
    return "Queues: " + ", ".join(QUEUES)


REGISTRY: dict[str, Callable[..., str]] = {
    "lookup_queue_policy": lookup_queue_policy,
    "list_queues": list_queues,
}

TOOL_SCHEMA: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "list_queues",
            "description": "List every support queue a ticket can be routed to. Takes no arguments.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_queue_policy",
            "description": (
                "Get the handling policy and SLA for one named support queue. "
                "Use this to check how a queue is handled, not to decide routing."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "queue": {
                        "type": "string",
                        "description": "Exact queue name, for example 'billing'.",
                    }
                },
                "required": ["queue"],
            },
        },
    },
]


@dataclass
class Triage:
    """What the triage produced, however it was produced."""

    queue: str
    reason: str
    shape: str  # workflow | router | agent
    model_calls: int
    escalate: bool = False


# ---------------------------------------------------------------- 1. workflow

# WHY no model at all in the pure step: a workflow's defining feature is that
# YOU wrote the path. The model may fill in a field, but it never chooses the
# order. To make the contrast sharp, this version routes by plain keyword rules,
# the way a hand-written script would.
KEYWORD_RULES = [
    ("abuse", ("spam", "hacked", "logged into my account", "security", "breach")),
    ("billing", ("charged", "refund", "invoice", "payment", "money back")),
    ("account", ("login", "password", "sign in", "profile", "locked out")),
    ("sales", ("upgrade", "pricing", "quote", "new plan", "buy")),
    ("technical", ("error", "bug", "outage", "not working", "broken", "crash")),
]


def triage_workflow(ticket: str) -> Triage:
    """
    Fixed rules, same order every time. No model, no ambiguity, no surprises.

    This is the baseline the whole unit measures against. It is fast, free,
    perfectly testable, and completely inflexible. For a large share of real
    routing, it is also entirely sufficient, which is the uncomfortable point.
    """
    text = ticket.lower()
    for queue, keywords in KEYWORD_RULES:
        if any(k in text for k in keywords):
            return Triage(
                queue=queue,
                reason=f"Matched a keyword rule for '{queue}'.",
                shape="workflow",
                model_calls=0,
                escalate=(queue == "abuse"),
            )
    return Triage(
        queue="technical",
        reason="No rule matched, defaulted to technical for a human to sort.",
        shape="workflow",
        model_calls=0,
    )


# ---------------------------------------------------------------- 2. router

ROUTER_SYSTEM = (
    "You are a support ticket router. Read the ticket and choose exactly one "
    "queue from this list: " + ", ".join(QUEUES) + ". "
    "Reply with only the queue name, nothing else. Do not explain."
)


def triage_router(client, model, ticket: str) -> Triage:
    """
    One model call picks a branch. Then ordinary code takes over.

    This is the sweet spot most 'AI routing' systems actually live in, and most
    of them are mislabelled as agents. The model makes exactly one decision,
    from a fixed menu, and everything after that is deterministic. One call, so
    the cost and latency are bounded and known in advance.
    """
    reply = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": ROUTER_SYSTEM},
            {"role": "user", "content": ticket},
        ],
    ).choices[0].message.content or ""

    choice = reply.strip().lower()
    # WHY this guard: the model was asked for one word from a fixed list, but a
    # language model can always return something off-menu. Validate against the
    # whitelist rather than trusting the output, exactly as with tool names.
    queue = choice if choice in QUEUES else "technical"
    reason = (
        f"Model chose '{choice}'."
        if choice in QUEUES
        else f"Model returned '{choice}', which is not a valid queue. Defaulted to technical."
    )
    return Triage(
        queue=queue,
        reason=reason,
        shape="router",
        model_calls=1,
        escalate=(queue == "abuse"),
    )


# ---------------------------------------------------------------- 3. agent

AGENT_SYSTEM = (
    "You are a support triage agent. You are given a ticket and tools to inspect "
    "the available queues and their policies. Decide which single queue the "
    "ticket belongs in. You may look up the queue list and policies if it helps "
    "you decide. When you are sure, give your final answer in the form "
    "'QUEUE: <name>' followed by one sentence of reasoning."
)


def triage_agent(client, model, ticket: str, max_steps: int = 5) -> Triage:
    """
    The model decides the whole path, using tools, until it is sure.

    This is the only one of the three that is actually an agent. It can look up
    the queues, read a policy, change its mind, and decide when it is done. It
    is also the slowest and most expensive of the three, and for a simple
    routing task that flexibility buys you almost nothing. That gap is the whole
    lesson of the lecture.
    """
    messages = [
        {"role": "system", "content": AGENT_SYSTEM},
        {"role": "user", "content": ticket},
    ]
    calls = 0

    for _ in range(1, max_steps + 1):
        calls += 1
        message = client.chat.completions.create(
            model=model, messages=messages, tools=TOOL_SCHEMA
        ).choices[0].message
        messages.append(message.model_dump(exclude_none=True))

        if not message.tool_calls:
            content = message.content or ""
            queue = _parse_queue(content)
            return Triage(
                queue=queue,
                reason=content.strip()[:200],
                shape="agent",
                model_calls=calls,
                escalate=(queue == "abuse"),
            )

        for call in message.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments or "{}")
            result = (
                REGISTRY[name](**args)
                if name in REGISTRY
                else f"Error: no tool named '{name}'."
            )
            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": result}
            )

    return Triage(
        queue="technical",
        reason=f"Did not decide within {max_steps} steps, defaulted to technical.",
        shape="agent",
        model_calls=calls,
    )


def _parse_queue(text: str) -> str:
    """Pull the queue out of a 'QUEUE: name' answer, defended against noise."""
    lowered = text.lower()
    if "queue:" in lowered:
        after = lowered.split("queue:", 1)[1].strip()
        for q in QUEUES:
            if after.startswith(q):
                return q
    # fall back to the first queue name mentioned anywhere
    for q in QUEUES:
        if q in lowered:
            return q
    return "technical"


# ---------------------------------------------------------------- compare

def compare(results: dict[str, Triage]) -> str:
    """Put the three shapes side by side for a notebook."""
    lines = [f"{'shape':<10} {'calls':>6} {'queue':<12} reason"]
    for _, t in results.items():
        lines.append(
            f"{t.shape:<10} {t.model_calls:>6} {t.queue:<12} {t.reason[:52]}"
        )
    return "\n".join(lines)
