"""
Conversation mechanics: measuring a transcript, and keeping it from exploding.

Unit 1 Lecture 3. The whole module exists to make one invisible thing visible:
you resend the entire transcript on every single request, so a conversation
that feels linear costs you something closer to quadratic.

Nothing here is clever. It is a tape measure and three pairs of scissors.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable

# ---------------------------------------------------------------- counting

_ENCODER = None
_ENCODER_TRIED = False


def _encoder():
    """
    Load a real tokenizer once, or fall back to an estimate.

    WHY the fallback: tiktoken downloads its encoding file on first use and
    caches it. On a locked down lab machine, or offline, that download fails.
    An agent that crashes because it could not measure itself is worse than one
    that measures itself approximately, so we degrade rather than raise.
    """
    global _ENCODER, _ENCODER_TRIED
    if _ENCODER_TRIED:
        return _ENCODER
    _ENCODER_TRIED = True
    try:
        import tiktoken

        _ENCODER = tiktoken.get_encoding("cl100k_base")
    except Exception:  # noqa: BLE001
        _ENCODER = None
    return _ENCODER


def count_tokens(text: str) -> int:
    """
    Tokens in a string.

    Exact when tiktoken is available. Otherwise roughly four characters per
    token, which is close enough for English prose and wrong for code and for
    Indian language text. Print `tokenizer_is_exact()` before you quote a
    number to anybody.
    """
    enc = _encoder()
    if enc is not None:
        return len(enc.encode(text))
    return max(1, len(text) // 4)


def tokenizer_is_exact() -> bool:
    return _encoder() is not None


# WHY a per message overhead at all: the provider wraps every message in role
# markers and separators before the model sees it, so a transcript always costs
# more than the sum of its visible text. Four is the commonly used figure for
# OpenAI style chat formats. Treat it as an estimate, not a guarantee.
PER_MESSAGE_OVERHEAD = 4


def message_tokens(message: dict[str, Any]) -> int:
    """Tokens for one message, including its tool calls if it has any."""
    total = PER_MESSAGE_OVERHEAD
    total += count_tokens(str(message.get("content") or ""))
    for call in message.get("tool_calls") or []:
        fn = call.get("function", {}) if isinstance(call, dict) else {}
        total += count_tokens(str(fn.get("name", "")))
        total += count_tokens(str(fn.get("arguments", "")))
    return total


def transcript_tokens(messages: list[dict[str, Any]]) -> int:
    """Tokens for the whole transcript, which is what you actually pay for."""
    return sum(message_tokens(m) for m in messages)


# ---------------------------------------------------------------- measuring

@dataclass
class TurnCost:
    turn: int
    sent: int          # tokens sent on this request
    new: int           # tokens genuinely new this turn
    cumulative: int    # everything sent so far, across all turns


def simulate_cost(turn_sizes: list[int], system_tokens: int = 120) -> list[TurnCost]:
    """
    What a conversation costs if you never trim it.

    Pass the size of each new turn. Get back what you actually send each time.
    This runs offline and spends nothing, which is the point: you can show a
    student the shape of the problem before they pay to discover it.
    """
    out: list[TurnCost] = []
    running = system_tokens
    cumulative = 0
    for i, size in enumerate(turn_sizes, start=1):
        running += size
        cumulative += running
        out.append(TurnCost(turn=i, sent=running, new=size, cumulative=cumulative))
    return out


# ---------------------------------------------------------------- trimming

def sliding_window(
    messages: list[dict[str, Any]],
    max_tokens: int,
    keep_system: bool = True,
) -> list[dict[str, Any]]:
    """
    Keep the system message and as many recent messages as fit.

    Cheap, predictable, and it forgets. Use when the useful context is recent,
    which for a booking assistant it usually is, and not when the user told you
    something important twenty turns ago.

    WHY tool messages are handled carefully: a tool result with no preceding
    assistant tool_call is invalid to most providers and will be rejected. So a
    naive slice is not safe, and this function drops orphans rather than
    sending a transcript the API will refuse.
    """
    if not messages:
        return []

    head = []
    body = list(messages)
    if keep_system and body and body[0].get("role") == "system":
        head = [body.pop(0)]

    budget = max_tokens - transcript_tokens(head)
    kept: list[dict[str, Any]] = []
    for m in reversed(body):
        cost = message_tokens(m)
        if cost > budget:
            break
        kept.insert(0, m)
        budget -= cost

    # drop leading tool messages whose assistant turn did not survive
    valid_ids: set[str] = set()
    for m in kept:
        for call in m.get("tool_calls") or []:
            cid = call.get("id") if isinstance(call, dict) else None
            if cid:
                valid_ids.add(cid)
    kept = [
        m for m in kept
        if m.get("role") != "tool" or m.get("tool_call_id") in valid_ids
    ]

    return head + kept


def summarise_older(
    messages: list[dict[str, Any]],
    keep_recent: int,
    summariser: Callable[[str], str],
) -> list[dict[str, Any]]:
    """
    Replace everything except the last `keep_recent` messages with a summary.

    Keeps the gist of old turns at a fraction of the tokens. Costs one extra
    model call, and loses exact wording, so never summarise anything you may
    need to quote back, such as a booking reference or a price the user agreed.
    """
    if not messages:
        return []

    head = []
    body = list(messages)
    if body and body[0].get("role") == "system":
        head = [body.pop(0)]

    if len(body) <= keep_recent:
        return head + body

    older, recent = body[:-keep_recent], body[-keep_recent:]
    transcript = "\n".join(
        f"{m.get('role')}: {m.get('content') or json.dumps(m.get('tool_calls'))}"
        for m in older
    )
    summary = summariser(transcript)

    # Recent messages may reference tool calls that are now inside the summary,
    # so run the same orphan check the sliding window uses.
    valid_ids: set[str] = set()
    for m in recent:
        for call in m.get("tool_calls") or []:
            cid = call.get("id") if isinstance(call, dict) else None
            if cid:
                valid_ids.add(cid)
    recent = [
        m for m in recent
        if m.get("role") != "tool" or m.get("tool_call_id") in valid_ids
    ]

    note = {
        "role": "system",
        "content": f"Summary of earlier conversation:\n{summary}",
    }
    return head + [note] + recent


PINNED_MARKER = "__pinned__"


def pin(message: dict[str, Any]) -> dict[str, Any]:
    """
    Mark a message as never droppable.

    For the things that must survive any trimming: a confirmed booking
    reference, an allergy, a budget the user stated once. Losing these is the
    failure mode that makes users abandon a product, and no trimming strategy
    protects them unless you say so explicitly.
    """
    out = dict(message)
    out[PINNED_MARKER] = True
    return out


def sliding_window_with_pins(
    messages: list[dict[str, Any]], max_tokens: int
) -> list[dict[str, Any]]:
    """Sliding window that always retains pinned messages, in original order."""
    pinned = [m for m in messages if m.get(PINNED_MARKER)]
    rest = [m for m in messages if not m.get(PINNED_MARKER)]
    reserved = transcript_tokens(pinned)
    kept = sliding_window(rest, max_tokens - reserved)

    order = {id(m): i for i, m in enumerate(messages)}
    merged = kept + pinned
    merged.sort(key=lambda m: order.get(id(m), 0))
    return merged
