"""
Putting it together: one full multi-agent system.

Unit 4 Lecture 5, the finale. You have built each collaboration primitive on its
own: fan-out and fan-in (L1), routing (L2), the manager (L3), the blackboard
(L4). A real system is not one of these, it is all of them, composed. This module
assembles them into a single support-triage workflow you could actually ship.

The shape, in order:
  1. Intake opens a blackboard and decides which team owns the ticket.
  2. A switch-case ROUTES the ticket to that team's intake.
  3. Each team fans OUT the same independent checks, security and priority,
     which run in parallel and post their findings to the board.
  4. Fan IN gathers the checks, and a disposition step reads the whole board to
     produce the final decision.

Route, then fan out, then share on the board, then decide. Every primitive from
the unit, in one graph, running offline because the nodes are plain functions.
Swap any node for a model-backed agent and the structure is unchanged.

    build_triage_system   the full composed workflow
    run_triage_system     run one ticket end to end and read the disposition
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


# ---------------------------------------------------------------- shared board keys

FINDINGS = "findings"
ORIGINAL = "original"


def _has_any(text: str, words: tuple[str, ...]) -> bool:
    low = text.lower()
    return any(w in low for w in words)


@dataclass
class Ticket:
    """The ticket plus the team the intake decided owns it."""

    text: str
    team: str


# ---------------------------------------------------------------- 1. intake + route

@executor(id="intake")
async def intake(text: str, ctx: WorkflowContext[Ticket]) -> None:
    """
    Opens the blackboard and decides the owning team.

    This one node does two jobs from two different lectures: it opens the shared
    board (L4) and it makes the routing decision (L2). It writes the original
    ticket and an empty findings list to the board, decides the team, and sends
    a Ticket carrying that decision onward for the switch-case to route on.
    """
    ctx.set_state(FINDINGS, [])
    ctx.set_state(ORIGINAL, text)
    if _has_any(text, ("charge", "charged", "refund", "invoice")):
        team = "billing"
    elif _has_any(text, ("error", "bug", "crash", "broken", "outage")):
        team = "technical"
    else:
        team = "general"
    await ctx.send_message(Ticket(text=text, team=team))


# ---------------------------------------------------------------- 2. team intakes

# Each team intake records which team took the ticket on the board, then passes
# the ticket text on to the shared checks. In a real system these would be team
# specific agents; here they are plain functions so the whole system runs offline.

@executor(id="billing_intake")
async def billing_intake(t: Ticket, ctx: WorkflowContext[str]) -> None:
    ctx.set_state(FINDINGS, ctx.get_state(FINDINGS) + ["team: billing"])
    await ctx.send_message(t.text)


@executor(id="technical_intake")
async def technical_intake(t: Ticket, ctx: WorkflowContext[str]) -> None:
    ctx.set_state(FINDINGS, ctx.get_state(FINDINGS) + ["team: technical"])
    await ctx.send_message(t.text)


@executor(id="general_intake")
async def general_intake(t: Ticket, ctx: WorkflowContext[str]) -> None:
    ctx.set_state(FINDINGS, ctx.get_state(FINDINGS) + ["team: general"])
    await ctx.send_message(t.text)


# ---------------------------------------------------------------- 3. parallel checks

# Whatever team took the ticket, the same two independent checks run, in parallel,
# each reading the board, appending its finding, and writing back. This is fan-out
# (L1) plus the blackboard (L4) working together.

@executor(id="security_check")
async def security_check(text: str, ctx: WorkflowContext[str]) -> None:
    flag = "security: RISK" if _has_any(text, ("hack", "breach", "password")) else "security: ok"
    ctx.set_state(FINDINGS, ctx.get_state(FINDINGS) + [flag])
    await ctx.send_message(text)


@executor(id="priority_check")
async def priority_check(text: str, ctx: WorkflowContext[str]) -> None:
    flag = "priority: HIGH" if _has_any(text, ("urgent", "down", "asap")) else "priority: normal"
    ctx.set_state(FINDINGS, ctx.get_state(FINDINGS) + [flag])
    await ctx.send_message(text)


# ---------------------------------------------------------------- 4. fan in + decide

@executor(id="dispose")
async def dispose(results: list[str], ctx: WorkflowContext) -> None:
    """
    The fan-in point and the final decision.

    It receives the list of check results (fan-in, L1), but the real decision is
    made from the board (L4), which holds the team plus every finding. It reads
    the whole board and produces one disposition: escalate if there is a security
    risk or high priority, otherwise route to the normal queue.
    """
    findings = ctx.get_state(FINDINGS)
    original = ctx.get_state(ORIGINAL)
    escalate = any("RISK" in f or "HIGH" in f for f in findings)
    decision = "ESCALATE" if escalate else "queue normally"
    board = "; ".join(findings)
    await ctx.yield_output(f"Ticket: {original}\nBoard: {board}\nDecision: {decision}")


# ---------------------------------------------------------------- the system

TEAM_INTAKES = {
    "billing": billing_intake,
    "technical": technical_intake,
    "general": general_intake,
}
CHECKS = [security_check, priority_check]


def build_triage_system():
    """
    The full system: intake and route, then per team fan out to shared checks on
    a blackboard, then fan in and decide.

    Read the builder top to bottom and you can see all four primitives:
    add_switch_case_edge_group is the router (L2); the three add_fan_out_edges are
    the parallel checks (L1); the checks and every node share the board via state
    (L4); add_fan_in_edges gathers them for the decision (L1 again). The manager
    idea from L3 lives in the dispose step, which makes the final call from the
    assembled evidence.
    """
    builder = WorkflowBuilder(start_executor=intake).add_switch_case_edge_group(
        intake,
        [
            Case(condition=lambda t: t.team == "billing", target=billing_intake),
            Case(condition=lambda t: t.team == "technical", target=technical_intake),
            Default(target=general_intake),
        ],
    )
    # whichever team took it, fan out to the same shared checks
    for team_intake in TEAM_INTAKES.values():
        builder = builder.add_fan_out_edges(team_intake, CHECKS)
    return builder.add_fan_in_edges(CHECKS, dispose).build()


async def run_triage_system(ticket: str) -> str:
    """Run one ticket through the whole system and return the disposition."""
    workflow = build_triage_system()
    result = await workflow.run(ticket)
    outputs = result.get_outputs()
    return outputs[0] if outputs else "no disposition produced"


# ---------------------------------------------------------------- the unit, mapped

SYSTEM_MAP: dict[str, str] = {
    "switch-case route (L2)": "intake sends the ticket to exactly one team intake",
    "fan-out (L1)": "each team runs the same independent checks in parallel",
    "blackboard (L4)": "every node reads and appends findings to shared state",
    "fan-in (L1)": "the checks gather before the decision, and it waits for all",
    "manager decision (L3)": "dispose reads the whole board and makes the final call",
    "the whole unit": "route, then fan out, then share, then decide, in one graph",
}


def what_you_can_build_now() -> dict[str, str]:
    """
    The capability you have earned, stated plainly for the end of the unit.

    A single agent was Unit 1. Making it reliable was Unit 2. The real frameworks
    were Unit 3. And composing many agents into a coordinated system is Unit 4.
    You can now take a real problem, decompose it into specialists, and wire them
    together with routing, parallelism, and shared state into something that
    behaves like a system, not a script.
    """
    return {
        "decompose": "split a problem into narrow specialists that each do one thing",
        "route": "send each request to the specialist or team that owns it",
        "parallelise": "run independent work at once, and wait for all of it",
        "share": "let agents build on each other's findings through a board",
        "decide": "make a final call from the assembled evidence, by rule or judgement",
    }
