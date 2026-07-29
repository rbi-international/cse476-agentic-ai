"""
Many agents at once: fan-out, fan-in, and the coordination you stop writing.

Unit 4 Lecture 1. Unit 3 ended with a graph that ran its nodes one after another,
classify then enrich then assign. That is a line. Real multi-agent systems are
not lines. Several specialists look at the same problem at the same time, and
something gathers their answers back together. That shape is fan-out and fan-in,
and it is the first thing a plain pipeline genuinely cannot express.

This module builds it for real, on Microsoft Agent Framework, and it runs offline
because the workers are plain functions. Swap any worker for an agent when it
needs judgement; the shape does not change.

    build_review_workflow   one ticket, three reviewers in parallel, then a join
    run_review              run it and get the combined verdict
    the coordination the framework does for you, made explicit and testable

The deep idea of the lecture: fan-in does not just collect results, it
synchronises. The join step does not run until every worker has finished. That
"wait for everyone" is the coordination you would otherwise write by hand, with
all the bugs that come with it, and the graph does it for you.
"""

from __future__ import annotations

from agent_framework import WorkflowBuilder, WorkflowContext, executor


# ---------------------------------------------------------------- the workers

# WHY three separate reviewers instead of one: each looks at the ticket through a
# different lens, and they do not depend on each other, so there is no reason to
# run them in sequence. Running them together is faster, and more honest about
# the fact that these are independent judgements. In a line, you would waste time
# making security wait for sentiment to finish for no reason.

def _has_any(text: str, words: tuple[str, ...]) -> bool:
    low = text.lower()
    return any(w in low for w in words)


@executor(id="dispatch")
async def dispatch(ticket: str, ctx: WorkflowContext[str]) -> None:
    """
    The fan-out point. It sends the same ticket to every reviewer downstream.

    Notice it sends one message and the framework delivers it to all three
    reviewers. You do not loop over the reviewers or manage threads. You declare
    the edges, and fan-out is what those edges mean.
    """
    await ctx.send_message(ticket)


@executor(id="security_review")
async def security_review(ticket: str, ctx: WorkflowContext[str]) -> None:
    """One reviewer: is this a security problem?"""
    risky = _has_any(ticket, ("hack", "breach", "password", "phish", "leak"))
    await ctx.send_message("SECURITY_RISK" if risky else "security_ok")


@executor(id="priority_review")
async def priority_review(ticket: str, ctx: WorkflowContext[str]) -> None:
    """Another reviewer, running at the same time: how urgent is this?"""
    urgent = _has_any(ticket, ("urgent", "down", "asap", "immediately", "critical"))
    await ctx.send_message("HIGH_PRIORITY" if urgent else "normal_priority")


@executor(id="sentiment_review")
async def sentiment_review(ticket: str, ctx: WorkflowContext[str]) -> None:
    """A third reviewer, also concurrent: how upset is the customer?"""
    angry = _has_any(ticket, ("furious", "terrible", "worst", "unacceptable", "angry"))
    await ctx.send_message("ANGRY_CUSTOMER" if angry else "calm_customer")


@executor(id="combine")
async def combine(findings: list[str], ctx: WorkflowContext) -> None:
    """
    The fan-in point. It receives a LIST of every reviewer's finding, at once.

    This is the part that surprises people. combine is not called three times,
    once per reviewer. It is called once, with all three findings already
    gathered into a list. The framework waited for every reviewer to finish, then
    handed you the complete set. You did not write that wait. That is the
    coordination you are no longer responsible for.
    """
    verdict = ", ".join(sorted(findings))
    await ctx.yield_output(f"Review complete: {verdict}")


# ---------------------------------------------------------------- the workflow

REVIEWERS = [security_review, priority_review, sentiment_review]


def build_review_workflow():
    """
    A real fan-out then fan-in workflow: one ticket, three parallel reviewers,
    one combined verdict.

    Read the two lines in the middle and you have the whole shape:
    add_fan_out_edges sends the ticket to every reviewer, and add_fan_in_edges
    gathers their findings into the combine step. There is no thread pool, no
    lock, no "have all three finished yet" flag. The graph expresses the
    parallelism, and the framework runs it.
    """
    return (
        WorkflowBuilder(start_executor=dispatch)
        .add_fan_out_edges(dispatch, REVIEWERS)
        .add_fan_in_edges(REVIEWERS, combine)
        .build()
    )


async def run_review(ticket: str) -> str:
    """Run the review workflow on one ticket and return the combined verdict."""
    workflow = build_review_workflow()
    result = await workflow.run(ticket)
    outputs = result.get_outputs()
    return outputs[0] if outputs else "no verdict produced"


# ---------------------------------------------------------------- the mapping

# Every new idea in this lecture, tied to what you already know.
ORCHESTRATION_MAP: dict[str, str] = {
    "fan-out": "one input to many workers, from your Unit 2 EventBus emit, but ordered",
    "fan-in": "many results gathered into one step, which the pipeline could not do",
    "add_fan_out_edges": "declare the one-to-many edges; the framework does delivery",
    "add_fan_in_edges": "declare the many-to-one join; the framework does the waiting",
    "the list at combine": "every worker's output, gathered, so you decide with all of it",
    "synchronisation": "combine runs only after every worker finishes; you wrote none of it",
}


def sequential_vs_concurrent() -> dict[str, str]:
    """
    Why concurrent is not just faster, stated for an interview.

    Speed is the obvious win, but it is not the real one. The real one is that
    independent work should be expressed as independent, so the structure of the
    code matches the structure of the problem. A line forces a false order onto
    things that have no order, and that false order is where bugs and wasted time
    hide.
    """
    return {
        "sequential": "each step waits for the one before, even when it need not",
        "concurrent": "independent steps run together, and a join waits for all",
        "the_real_win": "the code's shape matches the problem's shape, not just speed",
        "the_cost": "you must decide what truly is independent; not everything is",
    }
