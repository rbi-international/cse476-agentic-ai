"""
Everything the crew does becomes an event: who acted, what kind of step, how long.

The same events feed three places: the live web page (streamed), the job log in
GitHub Actions, and the cloud's log service (one JSON line each on stdout, which
CloudWatch and Cloud Logging pick up without any extra code).
"""

from __future__ import annotations

import json
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Callable


@dataclass
class Event:
    run: str
    t: float           # seconds since the run started
    agent: str         # lead, tests, security, quality, docs, judge, fixer, crew
    kind: str          # start, plan, tool, llm, finding, fix, verdict, done, error
    text: str
    ms: float = 0.0
    tokens: int = 0
    data: dict = field(default_factory=dict)


class Trace:
    def __init__(self, on_event: Callable[[Event], None] | None = None, quiet: bool = False):
        self.run = uuid.uuid4().hex[:8]
        self.start = time.perf_counter()
        self.events: list[Event] = []
        self.on_event = on_event
        self.quiet = quiet
        self._lock = threading.Lock()

    def emit(self, agent: str, kind: str, text: str, ms: float = 0.0, tokens: int = 0, **data) -> Event:
        ev = Event(self.run, round(time.perf_counter() - self.start, 3), agent, kind, text, ms, tokens, data)
        with self._lock:
            self.events.append(ev)
        if not self.quiet:
            print(json.dumps(asdict(ev)), flush=True)  # one structured log line per step
        if self.on_event:
            self.on_event(ev)
        return ev

    def totals(self) -> dict:
        llm = [e for e in self.events if e.kind == "llm"]
        return {
            "seconds": round(time.perf_counter() - self.start, 2),
            "llm_calls": len(llm),
            "tokens": sum(e.tokens for e in llm),
        }
