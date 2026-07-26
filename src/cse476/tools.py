"""
Tool calling, and what happens when a tool fails.

Unit 2 Lecture 2. In Unit 1 every tool returned a clean string on the first try.
Real tools do not. They time out, they throw, they return something the model
cannot use, and they hit rate limits. This module is about the gap between the
happy path and the real world, and it is deliberately built around tools that
misbehave on purpose.

    unreliable tools     a weather tool that fails in four different ways
    call_tool            the one place a tool actually runs, defended
    run_with_tools       a loop that survives every failure mode above

The lesson is that the loop, not the model, is responsible for turning a broken
tool into a sentence the model can read and recover from.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Callable

# ---------------------------------------------------------------- the world

# A tiny weather service. The data is fine. The tools that reach it are not,
# which is the whole point of this lecture.
WEATHER = {
    "mumbai": "Mumbai: 31C, humid, light rain.",
    "delhi": "Delhi: 38C, hazy, dry.",
    "jammu": "Jammu: 29C, clear.",
}


class ToolError(Exception):
    """A tool failed in a way the loop is expected to catch and report."""


# ---------------------------------------------------------------- tools that misbehave

def get_weather(city: str) -> str:
    """
    The happy path tool. Real data, no drama. Used to show the baseline before
    we start breaking things.
    """
    key = city.strip().lower()
    if key not in WEATHER:
        # WHY a returned message and not an exception: an unknown city is a
        # normal, expected outcome, not a fault. The model should read it and
        # adjust, so we hand it back as text rather than raising.
        return f"No weather on file for '{city}'. Known cities: {', '.join(WEATHER)}."
    return WEATHER[key]


def get_weather_that_times_out(city: str, delay: float = 2.0) -> str:
    """
    A tool that hangs. This stands in for a slow API, and it is the failure
    mode people forget, because it does not error, it just never comes back.
    """
    time.sleep(delay)
    return get_weather(city)


def get_weather_that_throws(city: str) -> str:
    """A tool that raises, the way a real client does on a bad connection."""
    raise ToolError("Connection reset by peer while reaching the weather service.")


def get_weather_that_returns_junk(city: str) -> str:
    """
    A tool that succeeds but returns something useless. The nastiest failure,
    because nothing errored and the pipeline looks healthy.
    """
    return "\x00\x00 <html>502 Bad Gateway</html> \x00"


def get_weather_that_rate_limits(city: str, _state: dict = {}) -> str:
    """
    A tool that works, then starts refusing. Fails every call after the second,
    to show why retrying blindly makes things worse.
    """
    _state["n"] = _state.get("n", 0) + 1
    if _state["n"] > 2:
        raise ToolError("429 Too Many Requests. Slow down.")
    return get_weather(city)


REGISTRY: dict[str, Callable[..., str]] = {
    "get_weather": get_weather,
}

TOOL_SCHEMA: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": (
                "Get the current weather for one city. Returns a short readable "
                "summary. Known cities are Mumbai, Delhi and Jammu."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name, for example 'Mumbai'.",
                    }
                },
                "required": ["city"],
            },
        },
    }
]


# ---------------------------------------------------------------- the defended executor

@dataclass
class ToolResult:
    """The outcome of one tool call, whether it worked or not."""

    name: str
    ok: bool
    observation: str      # always a string the model can read, even on failure
    attempts: int = 1
    seconds: float = 0.0


def call_tool(
    name: str,
    args: dict[str, Any],
    registry: dict[str, Callable[..., str]] | None = None,
    timeout: float = 5.0,
    retries: int = 2,
    backoff: float = 0.5,
) -> ToolResult:
    """
    Run one tool, and never let it take the whole system down with it.

    This is the single most important function in the lecture. Everything the
    model produces is untrusted, and everything a tool touches can fail, so this
    is where both of those truths get handled. Four defences, in order:

      1. whitelist    a name not in the registry never runs
      2. retry        a transient failure gets a second and third try, with a
                      growing pause between them, not an instant hammer
      3. catch        an exception becomes a readable observation, not a crash
      4. report       the outcome, good or bad, is always a string the model
                      can read on the next turn and reason about

    Note what is NOT here: a timeout that actually interrupts a hung call. True
    timeouts need threads or async and belong in Lecture 3. Here we measure the
    duration and flag a slow call, which is enough to teach the idea.
    """
    registry = registry if registry is not None else REGISTRY

    # defence 1: the whitelist
    if name not in registry:
        return ToolResult(
            name=name,
            ok=False,
            observation=(
                f"Error: no tool named '{name}'. Available: {list(registry)}. "
                f"Use one of those or answer without a tool."
            ),
        )

    func = registry[name]
    start = time.monotonic()
    last_error = ""

    # defence 2: retry with backoff
    for attempt in range(1, retries + 2):  # e.g. retries=2 gives 3 tries total
        try:
            result = func(**args)
            elapsed = time.monotonic() - start

            # a successful call that returned junk is still a failure to report
            if not _looks_usable(result):
                return ToolResult(
                    name=name,
                    ok=False,
                    observation=(
                        f"Tool '{name}' returned unusable output. Treat it as no "
                        f"data and either try a different approach or say so."
                    ),
                    attempts=attempt,
                    seconds=elapsed,
                )

            return ToolResult(
                name=name, ok=True, observation=result,
                attempts=attempt, seconds=elapsed,
            )

        except TypeError as e:
            # bad arguments are a permanent fault, so do not retry them
            elapsed = time.monotonic() - start
            return ToolResult(
                name=name,
                ok=False,
                observation=(
                    f"Tool '{name}' was called with wrong arguments: {e}. "
                    f"Check the required parameters and call it correctly."
                ),
                attempts=attempt,
                seconds=elapsed,
            )

        except Exception as e:  # noqa: BLE001
            # WHY catch broadly here: from the loop's point of view, any other
            # failure is a transient one worth one more try. We record it and,
            # if we have tries left, pause and retry rather than giving up.
            last_error = str(e)
            if attempt <= retries:
                time.sleep(backoff * attempt)  # defence 2: growing pause
                continue

    # defence 3 and 4: out of retries, hand back a readable failure
    elapsed = time.monotonic() - start
    return ToolResult(
        name=name,
        ok=False,
        observation=(
            f"Tool '{name}' failed after {retries + 1} attempts. "
            f"Last error: {last_error}. Proceed without it and tell the user."
        ),
        attempts=retries + 1,
        seconds=elapsed,
    )


def _looks_usable(text: Any) -> bool:
    """A crude check that a tool returned something a model can actually read."""
    if not isinstance(text, str):
        return False
    if not text.strip():
        return False
    if "\x00" in text:  # null bytes, a classic sign of a raw or broken response
        return False
    if "502" in text and "gateway" in text.lower():
        return False
    return True


# ---------------------------------------------------------------- the loop

SYSTEM = (
    "You are a weather assistant. Use the get_weather tool to answer. If a tool "
    "result says it failed or has no data, do not pretend otherwise. Tell the "
    "user plainly what you could and could not find out."
)


@dataclass
class RunResult:
    answer: str
    steps: int
    tool_calls: list[ToolResult] = field(default_factory=list)
    stopped_because: str = "goal met"


def run_with_tools(
    client, model, goal: str,
    registry: dict[str, Callable[..., str]] | None = None,
    max_steps: int = 6,
    verbose: bool = True,
) -> RunResult:
    """
    The Unit 1 loop, hardened. Every tool call goes through call_tool, so a
    broken tool becomes an observation the model can recover from rather than an
    exception that ends the request.
    """
    registry = registry if registry is not None else REGISTRY
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": goal},
    ]
    results: list[ToolResult] = []

    for step in range(1, max_steps + 1):
        message = client.chat.completions.create(
            model=model, messages=messages, tools=TOOL_SCHEMA
        ).choices[0].message
        messages.append(message.model_dump(exclude_none=True))

        if not message.tool_calls:
            return RunResult(
                answer=message.content or "",
                steps=step,
                tool_calls=results,
            )

        for call in message.tool_calls:
            name = call.function.name
            try:
                args = json.loads(call.function.arguments or "{}")
            except json.JSONDecodeError:
                # even the arguments the model produces are untrusted
                args = {}
            outcome = call_tool(name, args, registry=registry)
            results.append(outcome)
            if verbose:
                flag = "ok" if outcome.ok else "FAILED"
                print(f"  [step {step}] {name}({args}) [{flag}] -> {outcome.observation[:70]}")
            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": outcome.observation}
            )

    return RunResult(
        answer=f"Stopped after {max_steps} steps.",
        steps=max_steps,
        tool_calls=results,
        stopped_because="budget",
    )
