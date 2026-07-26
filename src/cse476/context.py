"""
Carrying context across turns, and testing a system that will not sit still.

Unit 2 Lecture 5, the last of the unit. Two threads that belong together.

First: an agent that remembers. So far every request has been a fresh start.
A real conversation builds: "book the billing team" then "actually make it
urgent" only makes sense if the second turn knows about the first. This module
gives an agent a small, honest session memory.

Second: testing. These systems are hard to test because the same input can
produce different output. You cannot assert equals on a model's wording. So we
test the things that ARE stable: the shape of the result, the invariants that
must always hold, and the behaviour of the deterministic parts around the model.

    Session          per-conversation memory, with a bound so it cannot grow forever
    ContextAgent     resolves references like "it" and "that" against the session
    check_invariants a way to test a non-deterministic system by what must stay true
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


# ---------------------------------------------------------------- memory

@dataclass
class Turn:
    """One exchange in a conversation."""

    role: str      # user | assistant
    text: str


@dataclass
class Session:
    """
    Per-conversation memory, with two jobs and one hard limit.

    It remembers the running transcript so the agent can refer back, and it
    remembers a small set of named facts, the things that must survive even
    when the transcript is trimmed. The max_turns bound is the same lesson as
    Lecture 3 of Unit 1: memory that grows without limit is a cost bomb.
    """

    max_turns: int = 20
    turns: list[Turn] = field(default_factory=list)
    facts: dict[str, str] = field(default_factory=dict)

    def add(self, role: str, text: str) -> None:
        self.turns.append(Turn(role, text))
        # WHY trim from the front: the oldest turns are the least relevant to
        # what is happening now, so if something has to go, they go first. The
        # named facts survive separately, which is the whole point of keeping
        # them apart from the transcript.
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns:]

    def remember(self, key: str, value: str) -> None:
        """Pin a fact that must survive trimming."""
        self.facts[key] = value

    def recall(self, key: str) -> str | None:
        return self.facts.get(key)

    def transcript(self) -> str:
        return "\n".join(f"{t.role}: {t.text}" for t in self.turns)


# ---------------------------------------------------------------- context resolution

# Words that point back at something said earlier. If the user uses one of
# these, the agent has to look into the session to know what it means.
REFERENCE_WORDS = ("it", "that", "them", "this", "the ticket", "the same")


def needs_context(message: str) -> bool:
    """Does this message refer to something from an earlier turn?"""
    low = message.lower()
    return any(w in low for w in REFERENCE_WORDS)


@dataclass
class ContextAgent:
    """
    A tiny stateful agent. It does not call a model in this teaching version; it
    resolves references against the session, which is the part worth studying.
    The lesson is not the resolution logic, it is that the agent's behaviour now
    depends on history, and that history is exactly what makes it hard to test.
    """

    session: Session = field(default_factory=Session)

    def handle(self, message: str) -> str:
        self.session.add("user", message)

        # a message that sets the subject: "route ticket 12 to billing"
        if "route" in message.lower() and "to" in message.lower():
            queue = message.lower().split("to", 1)[1].strip().split()[0]
            self.session.remember("queue", queue)
            reply = f"Routed to the {queue} team."
            self.session.add("assistant", reply)
            return reply

        # a follow-up that refers back: "make it urgent"
        if needs_context(message):
            queue = self.session.recall("queue")
            if queue is None:
                reply = "I do not have an earlier ticket to refer to. Please tell me which one."
            elif "urgent" in message.lower():
                self.session.remember("priority", "urgent")
                reply = f"Marked the {queue} ticket urgent."
            else:
                reply = f"Understood, applied to the {queue} ticket."
            self.session.add("assistant", reply)
            return reply

        reply = "I can route a ticket, and then you can refer back to it."
        self.session.add("assistant", reply)
        return reply


# ---------------------------------------------------------------- testing

@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str = ""


def check_invariants(
    output: Any,
    invariants: dict[str, Callable[[Any], bool]],
) -> list[CheckResult]:
    """
    Test a non-deterministic result by what must ALWAYS be true of it.

    You cannot assert that a model returned an exact string, because it will
    word things differently every run. But you can assert the things that must
    hold no matter what: that a queue is one of the valid queues, that a
    priority is never empty, that a required field is present. Those are
    invariants, and invariants are how you test a system that will not sit still.
    """
    results: list[CheckResult] = []
    for name, predicate in invariants.items():
        try:
            passed = bool(predicate(output))
            results.append(CheckResult(name, passed))
        except Exception as e:  # noqa: BLE001
            results.append(CheckResult(name, False, f"raised: {e}"))
    return results


def all_passed(results: list[CheckResult]) -> bool:
    return all(r.passed for r in results)


# A few reusable invariant builders, so a test reads like a sentence.
VALID_QUEUES = ["billing", "technical", "account", "sales", "abuse"]


def queue_is_valid(field_name: str = "queue") -> Callable[[dict], bool]:
    return lambda out: out.get(field_name) in VALID_QUEUES


def field_present(field_name: str) -> Callable[[dict], bool]:
    return lambda out: field_name in out and out[field_name] not in (None, "")


def field_in(field_name: str, allowed: list[str]) -> Callable[[dict], bool]:
    return lambda out: out.get(field_name) in allowed
