"""
The same task, four architectures.

Unit 1 Lecture 2. Each function below solves an identical booking problem and
differs only in how much the agent knows and how far ahead it looks. Run them
side by side and the classical taxonomy stops being exam vocabulary.

    reflex        no memory, one rule fires per observation
    model_based   carries internal state across observations
    goal_based    holds a goal and works out its own steps
    utility_based holds a goal AND scores competing options against preferences

The point of the file is the diff between them, so the shared parts are kept
identical on purpose.
"""

from __future__ import annotations

import json
from typing import Any, Callable

# ---------------------------------------------------------------- world

HOTELS = {
    "Taj Palace":   {"rate": 14500, "km_from_campus": 2.1, "rating": 4.8},
    "Radisson Blu": {"rate": 6200,  "km_from_campus": 8.4, "rating": 4.2},
    "Hotel Meera":  {"rate": 2800,  "km_from_campus": 14.9, "rating": 3.4},
}

ROOMS = {
    ("Taj Palace", "2026-08-14"): 0,
    ("Radisson Blu", "2026-08-14"): 11,
    ("Hotel Meera", "2026-08-14"): 6,
}


def get_room_availability(hotel: str, date: str) -> str:
    """Rooms free at one hotel on one date. Says nothing about price."""
    n = ROOMS.get((hotel, date))
    if n is None:
        return f"No record for {hotel} on {date}."
    return f"{hotel} on {date}: {n} rooms available."


def get_hotel_details(hotel: str) -> str:
    """Rate, distance and rating for one hotel. Says nothing about availability."""
    d = HOTELS.get(hotel)
    if d is None:
        return f"No details on file for {hotel}."
    return (
        f"{hotel}: Rs {d['rate']} per night, {d['km_from_campus']} km from "
        f"campus, guest rating {d['rating']} out of 5."
    )


def list_hotels() -> str:
    """Every hotel on file. The starting point when no hotel has been named."""
    return "Hotels on file: " + ", ".join(HOTELS)


REGISTRY: dict[str, Callable[..., str]] = {
    "get_room_availability": get_room_availability,
    "get_hotel_details": get_hotel_details,
    "list_hotels": list_hotels,
}

TOOL_SCHEMA: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "list_hotels",
            "description": "List every hotel we have on file. Takes no arguments.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_room_availability",
            "description": (
                "Number of rooms free at one hotel on one date. Tells you nothing "
                "about price, distance or rating."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "hotel": {"type": "string", "description": "Exact hotel name."},
                    "date": {"type": "string", "description": "Date as YYYY-MM-DD."},
                },
                "required": ["hotel", "date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_hotel_details",
            "description": (
                "Nightly rate, distance from campus and guest rating for one hotel. "
                "Tells you nothing about availability."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "hotel": {"type": "string", "description": "Exact hotel name."}
                },
                "required": ["hotel"],
            },
        },
    },
]


# ---------------------------------------------------------------- shared loop

def _loop(client, model, messages, max_steps, tools=True, verbose=True, tag=""):
    """
    One loop, used by every architecture below.

    WHY: keeping the loop identical is the whole experiment. If the loop varied
    too, you could not tell whether a behaviour difference came from the
    architecture or from the plumbing. Only the system prompt and the tool list
    change between the four functions.
    """
    for step in range(1, max_steps + 1):
        kwargs = {"model": model, "messages": messages}
        if tools:
            kwargs["tools"] = TOOL_SCHEMA

        message = client.chat.completions.create(**kwargs).choices[0].message
        messages.append(message.model_dump(exclude_none=True))

        if not getattr(message, "tool_calls", None):
            return message.content or ""

        for call in message.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments or "{}")
            result = (
                REGISTRY[name](**args)
                if name in REGISTRY
                else f"Error: no tool named '{name}'."
            )
            if verbose:
                print(f"  {tag}[{step}] {name}({args or ''}) -> {result}")
            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": result}
            )

    return f"Stopped after {max_steps} steps."


# ---------------------------------------------------------------- 1. reflex

REFLEX_SYSTEM = (
    "You are a lookup service. Answer using exactly one tool call, then stop. "
    "Never make a second tool call. Never reason about what to do next. If one "
    "tool call cannot answer the question, say you cannot answer it."
)


def reflex(client, model, request: str, verbose: bool = True) -> str:
    """
    Simple reflex agent. One percept in, one action out, no memory.

    Condition, action. The classical form is a rule table. Here the rule table
    is a very tight instruction, and the max_steps of 2 enforces it structurally
    rather than trusting the prompt.
    """
    return _loop(
        client, model,
        [{"role": "system", "content": REFLEX_SYSTEM},
         {"role": "user", "content": request}],
        max_steps=2, verbose=verbose, tag="reflex ",
    )


# ---------------------------------------------------------------- 2. model based

MODEL_BASED_SYSTEM = (
    "You are a lookup service with a memory of this conversation. Answer using "
    "tools. You may refer back to anything already established earlier in the "
    "conversation rather than looking it up again. Do not plan ahead; answer "
    "only what was asked."
)


class ModelBasedAgent:
    """
    Model based reflex agent. Same reflex behaviour, plus internal state.

    WHY a class and not a function: the internal state IS the architecture. The
    conversation persists between calls, so "what about the 15th" resolves
    against something the agent already knows.
    """

    def __init__(self, client, model, verbose: bool = True):
        self.client, self.model, self.verbose = client, model, verbose
        self.messages = [{"role": "system", "content": MODEL_BASED_SYSTEM}]

    def ask(self, request: str) -> str:
        self.messages.append({"role": "user", "content": request})
        return _loop(
            self.client, self.model, self.messages,
            max_steps=4, verbose=self.verbose, tag="model  ",
        )


# ---------------------------------------------------------------- 3. goal based

GOAL_SYSTEM = (
    "You are a booking assistant. You are given a goal, not a set of steps. "
    "Work out for yourself which tools to call and in what order. Keep going "
    "until the goal is satisfied, then give a final answer and stop."
)


def goal_based(client, model, goal: str, max_steps: int = 8, verbose: bool = True) -> str:
    """
    Goal based agent. Holds a desired end state and chooses its own path there.

    The difference from reflex is not the tools. It is that nothing in the
    prompt tells it the order, so the number of steps varies with what it finds.
    """
    return _loop(
        client, model,
        [{"role": "system", "content": GOAL_SYSTEM},
         {"role": "user", "content": goal}],
        max_steps=max_steps, verbose=verbose, tag="goal   ",
    )


# ---------------------------------------------------------------- 4. utility based

UTILITY_SYSTEM = (
    "You are a booking assistant. You are given a goal and a set of preferences "
    "with weights. Several options may satisfy the goal. Gather what you need, "
    "score every viable option against the weighted preferences, show the scores, "
    "then recommend the highest scoring one and explain the trade off you made."
)


def utility_based(
    client, model, goal: str, preferences: dict[str, float],
    max_steps: int = 10, verbose: bool = True,
) -> str:
    """
    Utility based agent. A goal is not enough when several outcomes satisfy it.

    WHY this matters: a goal based agent stops at the first hotel with a free
    room. A utility based agent asks which free room is best, which is a
    different and usually harder question. The weights are the utility function,
    made explicit so the trade off is auditable rather than hidden in a prompt.
    """
    pref_text = "\n".join(f"  {k}: weight {v}" for k, v in preferences.items())
    return _loop(
        client, model,
        [{"role": "system", "content": UTILITY_SYSTEM},
         {"role": "user", "content": f"{goal}\n\nMy preferences:\n{pref_text}"}],
        max_steps=max_steps, verbose=verbose, tag="utility",
    )
