"""
Observability: seeing inside a running agent.

Unit 5 Lecture 3. Testing and validation both happen BEFORE you ship: you check
the agent on your machine. But once it is live and real users are hitting it, how
do you see what it is doing? When a user says "it was slow" or "it gave me the
wrong answer", you were not watching. You cannot reproduce what you cannot see.

Observability is building the agent so it tells you what it is doing as it runs.
It rests on three pillars, and this module builds all three, offline:

  1. A TRACE, the ordered steps of one run, each timed, so you can see the path
     the agent took and find the slow step.
  2. METRICS, numbers aggregated across many runs, how often, how slow, how many
     failures, so you can watch the health of the whole system.
  3. Structured LOGS, searchable records of what happened, so you can find the one
     bad run among thousands.

The design keeps timing injectable, so the trace is real but the tests are
deterministic. In production you use the real clock; in a test you feed fixed
durations. That is the same seam idea from L1, applied to time.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------- 1. the trace

@dataclass
class Span:
    """One step in a run: what it was, and how long it took."""

    step: str
    ms: float


@dataclass
class Trace:
    """
    The ordered, timed steps of a single agent run.

    A trace answers "what did this one run actually do, and where did the time
    go?" It is the first thing you reach for when a specific run misbehaved. You
    record a span per step; the trace holds them in order.
    """

    spans: list[Span] = field(default_factory=list)

    def record(self, step: str, ms: float) -> None:
        """Add a completed step to the trace."""
        self.spans.append(Span(step=step, ms=ms))

    def total_ms(self) -> float:
        """How long the whole run took."""
        return round(sum(s.ms for s in self.spans), 2)

    def slowest(self) -> Span | None:
        """
        The step that took longest. This is where performance work should start.

        Optimising anything but the slowest step is wasted effort. A trace turns
        "it feels slow" into "the policy lookup took 80 percent of the time", which
        is the difference between guessing and knowing where to optimise.
        """
        return max(self.spans, key=lambda s: s.ms) if self.spans else None

    def path(self) -> list[str]:
        """The ordered list of step names, the route the agent actually took."""
        return [s.step for s in self.spans]


def trace_run(steps: list[tuple[str, float]]) -> Trace:
    """
    Build a trace from a list of (step_name, duration_ms) pairs.

    In production the durations come from a real clock around each step. Here they
    are passed in, which keeps the trace real but the tests deterministic: same
    inputs, same trace, no flaky timing. This is the L1 seam idea applied to time.
    """
    trace = Trace()
    for step, ms in steps:
        trace.record(step, ms)
    return trace


# ---------------------------------------------------------------- 2. metrics

@dataclass
class Metrics:
    """
    Numbers aggregated across MANY runs.

    A trace is one run; metrics are the whole system. They answer "how is the
    agent doing overall?": how many runs, how many failed, how slow on average.
    This is what you put on a dashboard and watch, and what alerts you when
    something changes. One trace tells you about one user; metrics tell you about
    all of them.
    """

    runs: int = 0
    failures: int = 0
    total_ms: float = 0.0

    def observe(self, trace: Trace, failed: bool = False) -> None:
        """Fold one run's trace into the running totals."""
        self.runs += 1
        self.total_ms += trace.total_ms()
        if failed:
            self.failures += 1

    def average_ms(self) -> float:
        """Average run duration, the headline latency number."""
        return round(self.total_ms / self.runs, 2) if self.runs else 0.0

    def failure_rate(self) -> float:
        """Fraction of runs that failed, the headline reliability number."""
        return round(self.failures / self.runs, 4) if self.runs else 0.0


# ---------------------------------------------------------------- 3. logs

def log_line(run_id: str, trace: Trace, outcome: str) -> dict:
    """
    A structured, searchable record of one run.

    Not a print statement, a dict with named fields you can filter and search:
    find every failed run, every run slower than a second, every run that took a
    given path. Structured logs are what let you find the one bad run among
    thousands, which a wall of unstructured text never could.
    """
    return {
        "run_id": run_id,
        "outcome": outcome,
        "total_ms": trace.total_ms(),
        "slowest_step": trace.slowest().step if trace.slowest() else None,
        "path": trace.path(),
    }


# ---------------------------------------------------------------- the mapping

OBSERVABILITY_MAP: dict[str, str] = {
    "before vs after shipping": "testing and validation check first; observability watches live",
    "a trace": "the ordered, timed steps of one run; find the slow step",
    "metrics": "numbers across many runs; average latency, failure rate",
    "structured logs": "searchable records; find the one bad run among thousands",
    "slowest step": "where performance work starts; optimise that, not a guess",
    "telemetry": "the trace, metrics, and logs an agent emits as it runs",
}


def the_three_pillars() -> dict[str, str]:
    """
    Traces, metrics, and logs, and what each answers, for the exam and the job.

    They are not competing options, they are three views of the same running
    system. A trace answers "what did THIS run do?", metrics answer "how is the
    system doing overall?", and logs answer "find the runs that match this". You
    need all three: metrics tell you something is wrong, logs help you find the
    bad runs, and a trace shows you what one of them actually did.
    """
    return {
        "trace": "one run, step by step and timed; for debugging a specific run",
        "metrics": "many runs, aggregated; for watching overall health",
        "logs": "searchable records; for finding the runs that matter",
        "together": "metrics alert, logs locate, a trace explains",
        "the_point": "you cannot fix what you cannot see; build the agent to tell you",
    }
