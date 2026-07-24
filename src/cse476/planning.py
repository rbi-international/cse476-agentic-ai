"""
Planning and reasoning.

Unit 1 Lecture 4. Four things live here:

    act_only        the naive shape, acts without reasoning first
    react           reasons briefly before each action, and recovers
    plan_then_execute   decides the whole route up front, then walks it
    reflect         checks its own answer before handing it over

Plus NoProgress, which is exit condition three from Lecture 1. We promised to
come back to it. This is that.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from cse476.architectures import REGISTRY, TOOL_SCHEMA


# ---------------------------------------------------------------- exit 3

@dataclass
class NoProgress:
    """
    Detects an agent going round in circles.

    Lecture 1 gave two exit conditions: the goal is met, and the budget ran out.
    This is the third. It catches the realistic failure, which is not an agent
    that runs forever doing nothing, but an agent that runs forever doing the
    same useful looking thing.

    Two signals, because they catch different bugs:

      repeat     the same tool with the same arguments, again and again.
                 Usually means the model did not register the result.
      stuck      different calls, but every observation says the same thing.
                 Usually means the data cannot answer the question at all.
    """

    repeat_limit: int = 3
    stuck_limit: int = 4
    _calls: list[str] = field(default_factory=list)
    _observations: list[str] = field(default_factory=list)

    def record(self, tool_name: str, args: dict[str, Any], observation: str) -> None:
        self._calls.append(f"{tool_name}({json.dumps(args, sort_keys=True)})")
        self._observations.append(observation.strip())

    def verdict(self) -> str | None:
        """Return a reason to stop, or None to carry on."""
        if len(self._calls) >= self.repeat_limit:
            recent = self._calls[-self.repeat_limit:]
            if len(set(recent)) == 1:
                return (
                    f"Repeated the same call {self.repeat_limit} times: {recent[0]}. "
                    f"The result is not changing, so neither will the answer."
                )

        if len(self._observations) >= self.stuck_limit:
            recent = self._observations[-self.stuck_limit:]
            if len(set(recent)) == 1:
                return (
                    f"Last {self.stuck_limit} observations were identical. "
                    f"The available tools cannot answer this."
                )
        return None

    def reset(self) -> None:
        self._calls.clear()
        self._observations.clear()


# ---------------------------------------------------------------- shared loop

def _run(
    client, model, system: str, goal: str,
    max_steps: int,
    detector: NoProgress | None = None,
    verbose: bool = True,
    tag: str = "",
) -> dict[str, Any]:
    """
    One loop for every strategy below, so behaviour differences come from the
    strategy rather than from the plumbing.

    Returns a dict rather than a string, because from here on we care about how
    the answer was reached as much as what it was. Unit 5 turns this into a
    trace you can put on a dashboard.
    """
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": goal},
    ]
    thoughts: list[str] = []
    steps = 0

    for step in range(1, max_steps + 1):
        steps = step
        message = client.chat.completions.create(
            model=model, messages=messages, tools=TOOL_SCHEMA
        ).choices[0].message
        messages.append(message.model_dump(exclude_none=True))

        if message.content:
            thoughts.append(message.content)
            if verbose and message.tool_calls:
                print(f"  {tag}[{step}] thought: {message.content[:90]}")

        if not message.tool_calls:
            return {
                "answer": message.content or "",
                "steps": steps,
                "thoughts": thoughts,
                "stopped_because": "goal met",
            }

        for call in message.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments or "{}")
            observation = (
                REGISTRY[name](**args)
                if name in REGISTRY
                else f"Error: no tool named '{name}'."
            )
            if verbose:
                print(f"  {tag}[{step}] {name}({args or ''}) -> {observation}")
            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": observation}
            )

            if detector is not None:
                detector.record(name, args, observation)

        if detector is not None:
            reason = detector.verdict()
            if reason:
                return {
                    "answer": f"Stopping early. {reason}",
                    "steps": steps,
                    "thoughts": thoughts,
                    "stopped_because": "no progress",
                }

    return {
        "answer": f"Stopped after {max_steps} steps without a final answer.",
        "steps": steps,
        "thoughts": thoughts,
        "stopped_because": "budget",
    }


# ---------------------------------------------------------------- strategies

ACT_ONLY_SYSTEM = (
    "You are a booking assistant. Call tools immediately. Do not explain your "
    "thinking, do not narrate, do not plan. Act first."
)

REACT_SYSTEM = (
    "You are a booking assistant using the ReAct pattern.\n"
    "Before every tool call, state in one short sentence what you are about to "
    "check and why it moves you towards the goal.\n"
    "After each result, say briefly what it tells you and what that changes.\n"
    "If a result blocks your current approach, say so and choose a different "
    "one rather than repeating the same call.\n"
    "When you have enough, give the final answer and stop."
)

PLANNER_SYSTEM = (
    "You are a planner. Given a goal and a list of available tools, write a "
    "short numbered plan of the tool calls needed, in order. Do not call any "
    "tools. Do not explain. Output only the numbered plan, at most five steps."
)

EXECUTOR_SYSTEM = (
    "You are an executor. You have been given a goal and a plan. Follow the "
    "plan using the tools. If a step fails or the plan turns out to be wrong, "
    "say so explicitly, then adapt. When done, give the final answer."
)


def act_only(client, model, goal: str, max_steps: int = 8, verbose: bool = True):
    """Acts without reasoning. The baseline, and the one that thrashes."""
    return _run(client, model, ACT_ONLY_SYSTEM, goal, max_steps,
                verbose=verbose, tag="act    ")


def react(
    client, model, goal: str,
    max_steps: int = 8,
    detector: NoProgress | None = None,
    verbose: bool = True,
):
    """
    Reason briefly, act, observe, reason again.

    WHY the reasoning helps at all: the thought is appended to the transcript,
    so on the next turn the model reads its own stated intention alongside the
    result. That is what makes "this hotel is full, so try another" happen
    without you writing that rule anywhere.
    """
    return _run(client, model, REACT_SYSTEM, goal, max_steps,
                detector=detector, verbose=verbose, tag="react  ")


def plan_then_execute(client, model, goal: str, max_steps: int = 8, verbose: bool = True):
    """
    Decide the whole route first, then walk it.

    Cheaper and more auditable than ReAct when the route is predictable. Worse
    when it is not, because a plan written before the first observation cannot
    account for what that observation says.
    """
    tool_names = ", ".join(REGISTRY)
    plan = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM},
            {"role": "user", "content": f"Goal: {goal}\nTools available: {tool_names}"},
        ],
    ).choices[0].message.content or ""

    if verbose:
        print("  plan:")
        for line in plan.strip().splitlines():
            print(f"    {line}")

    result = _run(
        client, model, EXECUTOR_SYSTEM,
        f"Goal: {goal}\n\nPlan:\n{plan}",
        max_steps, verbose=verbose, tag="exec   ",
    )
    result["plan"] = plan
    return result


def reflect(
    client, model, goal: str, draft: str,
    critic_system: str | None = None,
) -> dict[str, str]:
    """
    Check an answer before handing it over.

    The evaluator and optimizer pattern, in its smallest form. One call asks
    what is wrong with the draft, a second call fixes it.

    The honest limitation, which belongs on the slide next to this: the same
    model that produced the draft is judging it. It shares the draft's blind
    spots. Self critique catches sloppiness reliably and catches confident
    wrongness far less often, which is why Unit 5 uses independent checks
    instead of trusting this alone.
    """
    critic_system = critic_system or (
        "You are a strict reviewer. Given a goal and a draft answer, list what "
        "is missing, unsupported or wrong. If the draft is fine, say APPROVED "
        "and nothing else. Be brief."
    )

    critique = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": critic_system},
            {"role": "user", "content": f"Goal: {goal}\n\nDraft:\n{draft}"},
        ],
    ).choices[0].message.content or ""

    if critique.strip().upper().startswith("APPROVED"):
        return {"critique": critique, "final": draft, "revised": False}

    revised = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Rewrite the draft to address every point of the critique. Output only the improved answer."},
            {"role": "user", "content": f"Goal: {goal}\n\nDraft:\n{draft}\n\nCritique:\n{critique}"},
        ],
    ).choices[0].message.content or draft

    return {"critique": critique, "final": revised, "revised": True}


def compare(results: dict[str, dict[str, Any]]) -> str:
    """Small table for putting two strategies side by side in a notebook."""
    lines = [f"{'strategy':<20} {'steps':>6} {'stopped because':<16} answer"]
    for name, r in results.items():
        lines.append(
            f"{name:<20} {r['steps']:>6} {r['stopped_because']:<16} "
            f"{(r['answer'] or '')[:48]}"
        )
    return "\n".join(lines)
