"""
Routing: sending work to the right one, not to everyone.

Unit 4 Lecture 2. Last lecture, fan-out sent the ticket to every reviewer. That
is right when every reviewer should look. But most of the time you want the
opposite: look at the work, decide what kind it is, and send it to exactly one
specialist. A billing ticket goes to the billing agent, not to all of them.

That is routing, and the graph expresses it with conditional edges. This module
builds a real switch-case router on Microsoft Agent Framework: one classifier
decides the queue, and the graph delivers the ticket to a single matching
handler, with a default for anything that matches nothing.

    build_router          classify once, then route to one handler of several
    run_router            run it and get the single handler's result
    the Case and Default primitives, and why a default is not optional

Runs offline because the classifier and handlers are plain functions. Swap the
classifier for an agent when the decision needs real judgement; the routing
structure does not change.
"""

from __future__ import annotations

from dataclasses import dataclass

from agent_framework import (
    Case,
    Default,
    WorkflowBuilder,
    WorkflowContext,
    executor,
)


# ---------------------------------------------------------------- the message

# WHY a small dataclass instead of a bare string: routing needs two things to
# travel together, the original ticket and the decision made about it. The
# classifier attaches its decision, and every downstream edge reads that decision
# to choose the path. Passing a structured message instead of a string is the
# habit that keeps a growing graph honest.
@dataclass
class Routed:
    """A ticket plus the queue the classifier decided it belongs in."""

    ticket: str
    queue: str


QUEUES = ("billing", "technical", "account", "general")


# ---------------------------------------------------------------- the classifier

@executor(id="classify")
async def classify(ticket: str, ctx: WorkflowContext[Routed]) -> None:
    """
    Decide the queue, attach it to the ticket, and send it on.

    This is the one node that makes the decision. Everything after it just reads
    the decision and reacts. That separation, decide in one place, act in
    another, is what keeps routing readable as it grows: you always know where
    the choice is made.
    """
    low = ticket.lower()
    if any(w in low for w in ("charge", "charged", "refund", "invoice", "payment")):
        queue = "billing"
    elif any(w in low for w in ("error", "bug", "crash", "broken", "outage")):
        queue = "technical"
    elif any(w in low for w in ("login", "password", "locked", "account")):
        queue = "account"
    else:
        queue = "general"
    await ctx.send_message(Routed(ticket=ticket, queue=queue))


# ---------------------------------------------------------------- the handlers

# Each handler is the end of one route. In a real system each of these would be a
# specialist agent; here they are plain functions so the whole router runs and
# tests offline. The routing structure is identical either way.

@executor(id="billing_handler")
async def billing_handler(r: Routed, ctx: WorkflowContext) -> None:
    await ctx.yield_output(f"Billing team handling: {r.ticket}")


@executor(id="technical_handler")
async def technical_handler(r: Routed, ctx: WorkflowContext) -> None:
    await ctx.yield_output(f"Technical team handling: {r.ticket}")


@executor(id="account_handler")
async def account_handler(r: Routed, ctx: WorkflowContext) -> None:
    await ctx.yield_output(f"Account team handling: {r.ticket}")


@executor(id="general_handler")
async def general_handler(r: Routed, ctx: WorkflowContext) -> None:
    """The default route. Everything that matched no specific queue lands here."""
    await ctx.yield_output(f"General queue handling: {r.ticket}")


# ---------------------------------------------------------------- the router

def build_router():
    """
    A real switch-case router: classify once, then send to exactly one handler.

    Read the cases and you can see the whole routing table. Each Case pairs a
    condition with a target: if the queue is billing, go to the billing handler,
    and so on. The conditions are checked in order, and the FIRST match wins, so
    order matters. Default catches anything that matched nothing.

    Unlike fan-out, this delivers the ticket to a single handler. The graph made
    a choice, and only one path runs.
    """
    return (
        WorkflowBuilder(start_executor=classify)
        .add_switch_case_edge_group(
            classify,
            [
                Case(condition=lambda r: r.queue == "billing", target=billing_handler),
                Case(condition=lambda r: r.queue == "technical", target=technical_handler),
                Case(condition=lambda r: r.queue == "account", target=account_handler),
                Default(target=general_handler),
            ],
        )
        .build()
    )


async def run_router(ticket: str) -> str:
    """Route one ticket and return the single handler's result. No model needed."""
    workflow = build_router()
    result = await workflow.run(ticket)
    outputs = result.get_outputs()
    return outputs[0] if outputs else "no handler produced output"


# ---------------------------------------------------------------- the mapping

ROUTING_MAP: dict[str, str] = {
    "Case(condition, target)": "one branch of a switch: this condition sends here",
    "Default(target)": "the else branch: everything that matched no case",
    "first match wins": "conditions are checked in order, like an if/elif chain",
    "one path runs": "unlike fan-out, exactly one handler receives the ticket",
    "the classifier decides": "the choice is made in one node, read by the edges",
    "swap a handler for an agent": "the route stays; only the endpoint gets smarter",
}


def fan_out_vs_route() -> dict[str, str]:
    """
    The two shapes side by side, stated for an interview.

    Both are how a graph directs work, and knowing when to use which is a real
    design decision. Fan-out is for when every specialist should weigh in. Routing
    is for when one specialist owns the work. Most real systems use both: route to
    the right team, and within a team, fan out the independent checks.
    """
    return {
        "fan_out": "send to everyone; all run; gather all results",
        "route": "decide, then send to one; only that one runs",
        "use_fan_out_when": "every specialist genuinely should look at the work",
        "use_route_when": "one specialist owns this kind of work; the rest should not see it",
        "the_default_matters": "switch-case requires a default; hand-rolled routing can drop work",
    }
