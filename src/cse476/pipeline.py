"""
Chaining steps into a pipeline, and reacting to events.

Unit 2 Lecture 4. So far every tool call has stood alone. Real automation chains
them: the output of one step becomes the input of the next, and a failure
halfway through has to be handled without losing the work already done. This
module builds a small, honest pipeline engine and then shows the event-driven
shape, where work starts because something happened rather than because someone
asked.

    Step            one named unit of work, with a clear success or failure
    Pipeline        runs steps in order, passing state along, stopping on failure
    EventBus        the event-driven shape: publish an event, handlers react

The running example stays support-ticket triage from Lecture 1, now grown from a
single routing decision into a real intake pipeline: validate, classify,
enrich, and assign.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


# ---------------------------------------------------------------- one step

@dataclass
class StepResult:
    """The outcome of one step: did it work, and what did it produce."""

    ok: bool
    output: dict[str, Any] = field(default_factory=dict)
    note: str = ""


# A step takes the running state and returns a StepResult. It never raises for
# an expected failure; it returns ok=False, so the pipeline can decide what to
# do rather than the whole thing crashing.
Step = Callable[[dict[str, Any]], StepResult]


# ---------------------------------------------------------------- the pipeline

@dataclass
class RunLog:
    """A record of what the pipeline did, step by step. This is observability."""

    steps: list[tuple[str, bool, str]] = field(default_factory=list)
    completed: bool = False
    stopped_at: str = ""

    def add(self, name: str, ok: bool, note: str) -> None:
        self.steps.append((name, ok, note))

    def __str__(self) -> str:
        lines = []
        for name, ok, note in self.steps:
            mark = "ok  " if ok else "FAIL"
            lines.append(f"  [{mark}] {name}: {note}")
        tail = "completed" if self.completed else f"stopped at {self.stopped_at}"
        return "\n".join(lines) + f"\n  -> {tail}"


class Pipeline:
    """
    Run named steps in order, threading a shared state dict through them.

    The defining property of a workflow, from Lecture 1: YOU wrote the order, in
    advance. The pipeline does not decide anything. It just runs your steps and,
    crucially, stops cleanly the moment one fails rather than feeding a broken
    result into the next step.
    """

    def __init__(self, name: str):
        self.name = name
        self._steps: list[tuple[str, Step]] = []

    def step(self, name: str, fn: Step) -> Pipeline:
        """Add a named step. Returns self so calls can be chained."""
        self._steps.append((name, fn))
        return self

    def run(self, initial: dict[str, Any]) -> tuple[dict[str, Any], RunLog]:
        """
        Execute the steps in order. Each step reads and extends the shared state.

        WHY stop on the first failure: step three usually assumes step two
        succeeded. Running step three on a half-built state produces a confident,
        wrong result, which is worse than a clean stop. Fail fast, fail loud, and
        keep the work that did succeed.
        """
        state = dict(initial)
        log = RunLog()

        for name, fn in self._steps:
            try:
                result = fn(state)
            except Exception as e:  # noqa: BLE001
                # a step that raises unexpectedly is still a stop, not a crash
                log.add(name, False, f"unexpected error: {e}")
                log.stopped_at = name
                return state, log

            log.add(name, result.ok, result.note)
            if not result.ok:
                log.stopped_at = name
                return state, log

            state.update(result.output)

        log.completed = True
        return state, log


# ---------------------------------------------------------------- the steps

VALID_QUEUES = ["billing", "technical", "account", "sales", "abuse"]


def validate_ticket(state: dict[str, Any]) -> StepResult:
    """Step 1. A ticket with no text cannot be processed. Stop early if so."""
    text = (state.get("text") or "").strip()
    if not text:
        return StepResult(ok=False, note="ticket has no text")
    if len(text) < 3:
        return StepResult(ok=False, note="ticket text is too short to classify")
    return StepResult(ok=True, output={"clean_text": text}, note="ticket is well formed")


def classify_ticket(state: dict[str, Any]) -> StepResult:
    """
    Step 2. Decide the queue. Keyword rules stand in for the router from L1, so
    this module stays testable without a model. The point here is the chaining,
    not the classification.
    """
    text = state["clean_text"].lower()
    rules = [
        ("abuse", ("spam", "hacked", "security")),
        ("billing", ("charged", "refund", "invoice", "money")),
        ("account", ("login", "password", "locked")),
        ("sales", ("upgrade", "pricing", "quote")),
        ("technical", ("error", "bug", "broken", "not working")),
    ]
    for queue, words in rules:
        if any(w in text for w in words):
            return StepResult(ok=True, output={"queue": queue}, note=f"classified as {queue}")
    return StepResult(ok=True, output={"queue": "technical"},
                      note="no rule matched, defaulted to technical")


SLA_HOURS = {"billing": 24, "technical": 4, "account": 12, "sales": 48, "abuse": 1}


def enrich_ticket(state: dict[str, Any]) -> StepResult:
    """Step 3. Attach the SLA for the chosen queue. Depends on step 2's output."""
    queue = state.get("queue")
    if queue not in SLA_HOURS:
        return StepResult(ok=False, note=f"cannot enrich unknown queue '{queue}'")
    return StepResult(ok=True, output={"sla_hours": SLA_HOURS[queue]},
                      note=f"SLA is {SLA_HOURS[queue]}h")


def assign_ticket(state: dict[str, Any]) -> StepResult:
    """Step 4. The final step. Produce the assignment record."""
    queue = state["queue"]
    priority = "urgent" if queue == "abuse" else "normal"
    return StepResult(
        ok=True,
        output={"assigned_to": f"{queue}-team", "priority": priority},
        note=f"assigned to {queue}-team ({priority})",
    )


def build_intake_pipeline() -> Pipeline:
    """The standard four-step intake, wired up. Read it top to bottom."""
    return (
        Pipeline("ticket-intake")
        .step("validate", validate_ticket)
        .step("classify", classify_ticket)
        .step("enrich", enrich_ticket)
        .step("assign", assign_ticket)
    )


# ---------------------------------------------------------------- event-driven

@dataclass
class Event:
    """Something happened. Handlers may care about it."""

    name: str
    payload: dict[str, Any] = field(default_factory=dict)


class EventBus:
    """
    The event-driven shape: publish an event, and whoever subscribed reacts.

    The contrast with a pipeline is the direction of control. A pipeline is a
    line YOU walk down, step by step. An event bus is a room you shout into, and
    anyone listening for that word responds. Neither is better. They answer
    different questions: 'do these steps in order' versus 'when this happens, run
    whatever cares about it'.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable[[Event], None]]] = {}
        self.dispatched: list[str] = []

    def on(self, event_name: str, handler: Callable[[Event], None]) -> None:
        """Subscribe a handler to an event name."""
        self._handlers.setdefault(event_name, []).append(handler)

    def emit(self, event: Event) -> int:
        """
        Publish an event. Every handler subscribed to its name runs.

        Returns how many handlers reacted. A handler that raises does not stop
        the others, because in an event system one broken listener should not
        silence the rest.
        """
        self.dispatched.append(event.name)
        handlers = self._handlers.get(event.name, [])
        ran = 0
        for handler in handlers:
            try:
                handler(event)
                ran += 1
            except Exception:  # noqa: BLE001
                # one bad handler must not take down the others
                continue
        return ran
