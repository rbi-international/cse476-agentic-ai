"""
Serving the agent: turning a program into a service others can reach.

Unit 5 Lecture 4. Your agent works, it is tested, validated, and observable. But
it still runs in your notebook, on your machine. Nobody else can use it. For an
agent to be a product, it has to become a service: something reachable over the
network that answers requests. The standard way to do that is to wrap it in an
API.

An API is a contract. It says: send me a request shaped like this, and I will
send you a response shaped like that. The agent becomes a function sitting behind
an address (an endpoint), and anyone who can reach that address, a web app, a
mobile app, another service, can use your agent without knowing anything about
how it works inside.

This module builds a real API on FastAPI, and the whole thing is testable offline
with a TestClient, no running server needed. That is the same discipline as the
rest of the unit: real production tooling, exercised deterministically.

    TicketRequest, TriageResponse   the contract: request in, response out
    make_app                        the API that serves the agent
    a health endpoint, so a load balancer knows the service is alive
    testable offline with TestClient, so the API is covered like any code
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel


# ---------------------------------------------------------------- the contract

# WHY define the shapes first: an API is a promise about what goes in and what
# comes out. Writing that promise down as types is what lets the framework check
# every request for you and reject a malformed one automatically, before your
# agent ever sees it. The contract is the interface; the agent is the
# implementation behind it.

class TicketRequest(BaseModel):
    """What a caller must send: a ticket with some text."""

    text: str


class TriageResponse(BaseModel):
    """What the service promises to return: a team and an escalation flag."""

    team: str
    escalate: bool


# ---------------------------------------------------------------- the agent

def triage(text: str) -> dict:
    """
    The agent itself, as a plain function.

    Notice the agent has not changed at all from the rest of the course. It is
    the same kind of plain, testable function you have built all along. Serving it
    does not touch the agent; it wraps it. Keeping the agent separate from the
    serving layer is what lets you test the agent offline and swap the serving
    layer without rewriting the logic.
    """
    low = text.lower()
    if any(w in low for w in ("refund", "charge", "invoice")):
        team = "billing"
    elif any(w in low for w in ("error", "bug", "crash")):
        team = "technical"
    else:
        team = "general"
    escalate = any(w in low for w in ("hack", "breach", "urgent"))
    return {"team": team, "escalate": escalate}


# ---------------------------------------------------------------- the API

def make_app() -> FastAPI:
    """
    Build the API that serves the agent.

    Two endpoints, and each earns its place:
      - GET /health returns a simple ok. A load balancer or orchestrator pings
        this to know the service is alive, and restarts it if it stops
        answering. Every production service needs one.
      - POST /triage is the real work: it takes a TicketRequest, runs the agent,
        and returns a TriageResponse. Because the request and response types are
        declared, FastAPI validates every incoming request and rejects a
        malformed one with a clear error, before the agent runs.

    make_app is a function, not a module-level app, so a test can build a fresh
    instance. That is the same seam habit from Lecture 1: construct, do not reach
    for a global.
    """
    app = FastAPI(title="Triage Service", version="1.0.0")

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.post("/triage", response_model=TriageResponse)
    def triage_endpoint(request: TicketRequest) -> dict:
        return triage(request.text)

    return app


# ---------------------------------------------------------------- the mapping

SERVING_MAP: dict[str, str] = {
    "an API": "a contract: send a request like this, get a response like that",
    "an endpoint": "an address callers reach, for example POST /triage",
    "the request model": "the shape a caller must send; the framework checks it",
    "the response model": "the shape the service promises to return",
    "the health endpoint": "a heartbeat a load balancer pings to know you are alive",
    "the agent is unchanged": "serving wraps the agent; it does not rewrite it",
}


def why_an_api() -> dict[str, str]:
    """
    Why wrap the agent in an API at all, stated for the exam and the job.

    A function in your notebook can only be called by you, in that notebook. An
    API turns it into something any program anywhere can call over the network,
    which is what a service is. The contract, the typed request and response, is
    what makes it safe: callers know exactly what to send, the framework rejects
    anything malformed, and you can change the agent inside without breaking
    callers, as long as the contract holds.
    """
    return {
        "the_problem": "a notebook function is reachable only by you, in that notebook",
        "the_fix": "an API makes it callable by any program over the network",
        "the_contract": "typed request and response, so callers and service agree",
        "the_safety": "malformed requests are rejected before the agent runs",
        "the_freedom": "change the agent inside freely, as long as the contract holds",
    }
