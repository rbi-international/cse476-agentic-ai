"""
The smallest honest agent.

This is the reference implementation for Unit 1 Lecture 1. Everything here is
deliberately plain. No framework, no abstraction, no cleverness. If you can
read this file you can read any agent framework, because they are all doing
this underneath.

Four requirements, four sections below:
    1. a goal, not a question
    2. tools it is allowed to use
    3. a loop that carries state
    4. a way to stop
"""

from __future__ import annotations

import json
from typing import Any, Callable

# ---------------------------------------------------------------- 2. TOOLS

# WHY: a tool is an ordinary Python function. Nothing special happens to it.
# The model never touches this function. Read that sentence again in step 3.

ROOMS = {
    ("Taj Palace", "2026-08-14"): 3,
    ("Taj Palace", "2026-08-15"): 0,
    ("Radisson Blu", "2026-08-14"): 11,
    ("Radisson Blu", "2026-08-15"): 7,
}

RATES = {"Taj Palace": 14500, "Radisson Blu": 6200}


def get_room_availability(hotel: str, date: str) -> str:
    """How many rooms are free at a hotel on a date."""
    n = ROOMS.get((hotel, date))
    if n is None:
        return f"No record for {hotel} on {date}."
    return f"{hotel} on {date}: {n} rooms available."


def get_nightly_rate(hotel: str) -> str:
    """The nightly rate for a hotel, in rupees."""
    rate = RATES.get(hotel)
    if rate is None:
        return f"No rate on file for {hotel}."
    return f"{hotel}: Rs {rate} per night."


# The registry is the whitelist. If a name is not in here, it does not run.
# WHY: models sometimes invent tools that do not exist. This dict is the only
# thing standing between an invented name and an exception in your service.
REGISTRY: dict[str, Callable[..., str]] = {
    "get_room_availability": get_room_availability,
    "get_nightly_rate": get_nightly_rate,
}

# The schema is how you describe those functions to the model. It is the only
# thing the model ever sees. If the description is vague, the model picks the
# wrong tool, and that is your fault rather than the model's.
TOOL_SCHEMA: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_room_availability",
            "description": (
                "Get the number of rooms available at a specific hotel on a "
                "specific date. Use this when asked whether a hotel has space."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "hotel": {
                        "type": "string",
                        "description": "Exact hotel name, for example 'Taj Palace'.",
                    },
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format.",
                    },
                },
                "required": ["hotel", "date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_nightly_rate",
            "description": (
                "Get the nightly room rate in rupees for a hotel. Use this when "
                "asked about price or cost. Does not tell you availability."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "hotel": {
                        "type": "string",
                        "description": "Exact hotel name, for example 'Taj Palace'.",
                    }
                },
                "required": ["hotel"],
            },
        },
    },
]


# ---------------------------------------------------------------- 3 and 4. LOOP

SYSTEM = (
    "You are a hotel booking assistant. You have tools for room availability "
    "and nightly rates. Use them rather than guessing. When you have everything "
    "you need, answer the user directly and stop calling tools."
)


def run_agent(
    client: Any,
    model: str,
    goal: str,
    max_steps: int = 6,
    verbose: bool = True,
) -> str:
    """
    Run the think, act, observe loop until the goal is met or the budget runs out.

    max_steps is not a nicety. It is the only thing that turns an infinite loop
    into a bounded one, and it is the single most commonly forgotten line in
    every agent tutorial on the internet.
    """
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": goal},
    ]

    for step in range(1, max_steps + 1):
        # THINK. The model looks at everything so far and decides what happens next.
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOL_SCHEMA,
        )
        message = response.choices[0].message

        # WHY: the assistant turn goes back into the history whether or not it
        # asked for a tool. Drop it and the model loses the thread of its own
        # reasoning, then repeats the same tool call forever.
        messages.append(message.model_dump(exclude_none=True))

        # TERMINATION, condition one: the model stopped asking for tools.
        if not message.tool_calls:
            if verbose:
                print(f"[step {step}] done")
            return message.content or ""

        # ACT. Note carefully: the model did not call anything. It returned a
        # request. This loop is what actually executes the function.
        for call in message.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments or "{}")

            if name in REGISTRY:
                result = REGISTRY[name](**args)
            else:
                # The model invented a tool. Tell it so, and keep going.
                result = f"Error: no tool named '{name}'. Available: {list(REGISTRY)}"

            if verbose:
                print(f"[step {step}] {name}({args}) -> {result}")

            # OBSERVE. The result is appended as a tool message tied to the
            # exact call id, so the model knows which request it answers.
            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": result}
            )

    # TERMINATION, condition two: the budget ran out. Say so honestly rather
    # than pretending the agent succeeded.
    return (
        f"Stopped after {max_steps} steps without reaching a final answer. "
        f"This is the budget guard doing its job."
    )
