"""
The blackboard: a shared workspace agents build on together.

Unit 4 Lecture 4. So far, agents have passed a single message down an edge: one
hands the next a result. That is fine for a line, but real collaboration is
richer. Several agents work the same problem, and each needs to see what the
others have found. A security check should be able to read what triage decided;
a summary should see everything gathered so far.

The pattern for that is a blackboard: a shared space every agent can read from
and write to. One agent posts a finding, another reads it and adds its own, and a
final agent reads the whole board. This module builds a real blackboard on
Microsoft Agent Framework using the workflow's shared state.

    build_blackboard      a workflow where agents accumulate findings in shared state
    run_blackboard        run it and read the assembled board
    the discipline that keeps a shared board from becoming a mess

The whole thing runs offline, because the agents are plain functions writing to
shared state. The state API is the real ctx.set_state and ctx.get_state; the
findings just happen to be computed by simple code here instead of a model.
"""

from __future__ import annotations

from agent_framework import WorkflowBuilder, WorkflowContext, executor


# ---------------------------------------------------------------- the board keys

# WHY name the keys as constants: a blackboard is shared, so every agent must
# agree on what to call things. If one agent writes "findings" and another reads
# "finding", they silently miss each other. Fixed key names are the contract that
# keeps a shared workspace honest, the same discipline as agreeing on column names
# in a shared spreadsheet.
TICKET = "ticket"
FINDINGS = "findings"


def _has_any(text: str, words: tuple[str, ...]) -> bool:
    low = text.lower()
    return any(w in low for w in words)


# ---------------------------------------------------------------- the agents

@executor(id="intake")
async def intake(ticket: str, ctx: WorkflowContext[str]) -> None:
    """
    The first agent. It puts the ticket on the board and opens an empty findings
    list for the others to add to.

    Note the two writes: the ticket itself, so later agents can re-read the
    original, and an empty findings list, so the agents that follow have
    something to append to rather than each inventing their own storage.
    """
    ctx.set_state(TICKET, ticket)
    ctx.set_state(FINDINGS, [])
    await ctx.send_message(ticket)


@executor(id="security_scan")
async def security_scan(ticket: str, ctx: WorkflowContext[str]) -> None:
    """
    Reads the board, adds a security finding, writes the board back.

    This is the read, modify, write cycle at the heart of a blackboard. It reads
    the current findings, appends its own, and writes the updated list back. It
    does not overwrite the board; it adds to it, so the next agent sees both the
    earlier findings and this one.
    """
    findings = ctx.get_state(FINDINGS)
    verdict = "security: RISK" if _has_any(ticket, ("hack", "breach", "password")) else "security: ok"
    ctx.set_state(FINDINGS, findings + [verdict])
    await ctx.send_message(ticket)


@executor(id="priority_scan")
async def priority_scan(ticket: str, ctx: WorkflowContext[str]) -> None:
    """
    Reads the board (including the security finding), adds a priority finding.

    Because this runs after security_scan on the same board, when it reads
    FINDINGS it already sees the security verdict. Each agent builds on the ones
    before it. That accumulation is the point of the blackboard.
    """
    findings = ctx.get_state(FINDINGS)
    verdict = "priority: HIGH" if _has_any(ticket, ("urgent", "down", "asap")) else "priority: normal"
    ctx.set_state(FINDINGS, findings + [verdict])
    await ctx.send_message(ticket)


@executor(id="summarise")
async def summarise(ticket: str, ctx: WorkflowContext) -> None:
    """
    The last agent. It reads the whole board and produces the final summary.

    It reads nothing from its incoming message except as a trigger; everything it
    needs is on the board, written by the agents before it. This is the reader at
    the end of a blackboard: it sees the accumulated work of everyone.
    """
    original = ctx.get_state(TICKET)
    findings = ctx.get_state(FINDINGS)
    board = "; ".join(findings) if findings else "no findings"
    await ctx.yield_output(f"Ticket: {original}\nBoard: {board}")


# ---------------------------------------------------------------- the workflow

def build_blackboard():
    """
    A workflow where three agents accumulate findings on a shared board, then a
    fourth reads the whole board.

    The edges make a line, intake to security to priority to summary, but the
    real communication is not down the edges, it is through the shared board.
    Each agent reads the board, adds to it, and passes control on. The final
    agent reads everything. That is a blackboard: the edges carry control, the
    state carries the collaboration.
    """
    return (
        WorkflowBuilder(start_executor=intake)
        .add_edge(intake, security_scan)
        .add_edge(security_scan, priority_scan)
        .add_edge(priority_scan, summarise)
        .build()
    )


async def run_blackboard(ticket: str) -> str:
    """Run the blackboard workflow on a ticket and return the final summary."""
    workflow = build_blackboard()
    result = await workflow.run(ticket)
    outputs = result.get_outputs()
    return outputs[0] if outputs else "no summary produced"


# ---------------------------------------------------------------- the mapping

BLACKBOARD_MAP: dict[str, str] = {
    "ctx.set_state(key, value)": "post something to the shared board",
    "ctx.get_state(key)": "read what other agents put on the board",
    "read, modify, write": "read the board, add your finding, write it back",
    "agreed key names": "the contract that lets agents find each other's work",
    "the edges carry control": "who runs next; the collaboration is in the state",
    "append not overwrite": "add to the board so earlier findings survive",
}


def message_vs_blackboard() -> dict[str, str]:
    """
    Passing a message versus sharing a board, stated for an interview.

    A message goes to one place and is gone once read. A board persists and is
    visible to everyone. Use a message when one agent hands exactly one thing to
    the next. Use a board when several agents need to see and build on a growing
    picture. The cost of a board is discipline: shared state that everyone writes
    to can become a tangle if nobody agrees on what goes where.
    """
    return {
        "message": "point to point, consumed once, private to sender and receiver",
        "blackboard": "shared, persistent, visible to every agent in the workflow",
        "use_a_message": "when one agent hands one result to the next",
        "use_a_board": "when several agents build on a shared, growing picture",
        "the_cost": "shared state needs agreed keys and discipline, or it tangles",
    }
