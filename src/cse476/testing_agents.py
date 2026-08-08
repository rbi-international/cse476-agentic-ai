"""
Testing an agent: how do you test something that thinks?

Unit 5 Lecture 1. A normal function is easy to test: same input, same output,
assert and done. An agent breaks that. It calls a model, and the model can answer
differently each time, so the naive test "assert the agent said X" fails randomly
even when nothing is wrong. This is the first real problem of putting an agent in
production: how do you test it at all?

The answer is not to give up on testing, it is to split the agent into two parts
and test each the right way.

  1. The SKELETON, your routing, your tools, your state handling, is ordinary
     deterministic code. It tests exactly like any code: fast, offline, exact.
     This is most of your system, and it is why every workflow in this course
     ran offline.
  2. The MODEL-DEPENDENT part, where judgement happens, cannot be pinned to an
     exact answer. You test it with a FAKE model (a test double) to check your
     logic, and with looser checks for the real thing.

This module builds both techniques for real.

    check_refund_eligible   a plain tool: test it exactly, offline
    decide_route            model-dependent logic with a client seam
    FakeClient              a test double so you can test decide_route offline
    the testing pyramid, stated for the exam and the job
"""

from __future__ import annotations

from typing import Protocol


# ---------------------------------------------------------------- 1. plain tools

# WHY start here: most of an agent is not the model. It is tools and logic, and
# those are ordinary deterministic functions. They are the easy, high-value thing
# to test, and testing them well catches most bugs before the model is ever
# involved. Never skip testing the boring parts; they are where real bugs hide.

def check_refund_eligible(days_since_purchase: int, amount: float) -> bool:
    """
    A plain tool the agent can call. Refunds allowed within 30 days, under 5000.

    This is pure logic: same inputs, same output, every time. It tests exactly
    like any function. No model, no flakiness, no lane.
    """
    return days_since_purchase <= 30 and amount <= 5000.0


def summarise_findings(findings: list[str]) -> str:
    """Another plain tool: join findings into a one-line summary. Fully testable."""
    if not findings:
        return "no findings"
    return "; ".join(findings)


# ---------------------------------------------------------------- 2. the client seam

# The trick that makes model-dependent code testable: do not let your logic reach
# out to the model directly. Take the client as an argument (a seam). In
# production you pass the real client; in a test you pass a fake one. Same code,
# two clients. This one habit is what makes an agent testable at all.

class Responder(Protocol):
    """Anything with a respond(prompt) -> str method. The real client and the fake
    one both satisfy this, so decide_route cannot tell them apart."""

    def respond(self, prompt: str) -> str: ...


def decide_route(ticket: str, client: Responder) -> str:
    """
    Model-dependent logic, written against a seam so it can be tested offline.

    It asks the model to classify, then cleans and validates the answer. The
    cleaning and validating is YOUR logic, and it is testable with a fake model.
    Notice what this function guards against: a model that answers with extra
    whitespace, wrong case, or something off the menu. That defensive logic is
    exactly what you want to test, and you can, without spending a token.
    """
    raw = client.respond(f"Classify this ticket as billing, technical, or account:\n{ticket}")
    answer = raw.strip().lower()
    valid = {"billing", "technical", "account"}
    return answer if answer in valid else "general"


# ---------------------------------------------------------------- 3. the test double

class FakeClient:
    """
    A test double: a stand-in for the real model that returns a canned answer.

    It lets you test decide_route offline and deterministically. You control what
    the model "says", so you can check your cleaning and validating logic against
    every awkward answer a real model might give, whitespace, wrong case, garbage,
    without ever calling a real model. It also records what it was asked, so you
    can assert the agent built the right prompt.
    """

    def __init__(self, canned_answer: str) -> None:
        self.canned_answer = canned_answer
        self.prompts_seen: list[str] = []

    def respond(self, prompt: str) -> str:
        self.prompts_seen.append(prompt)
        return self.canned_answer


# ---------------------------------------------------------------- the mapping

TESTING_MAP: dict[str, str] = {
    "the skeleton": "your tools, routing, state; deterministic, test it exactly",
    "the model part": "judgement; cannot pin an exact answer, test with a fake",
    "a seam": "take the client as an argument so a fake can be passed in a test",
    "a test double (fake)": "a stand-in model with a canned answer you control",
    "assert the prompt": "check what the agent SENT, not only what came back",
    "why it runs offline": "with a fake model, no lane and no tokens are needed",
}


def the_testing_pyramid() -> dict[str, str]:
    """
    How to spend your testing effort, stated for the exam and the job.

    Most of your tests should be fast, exact, offline tests of the skeleton: the
    tools and the logic. A smaller number use a fake model to test the
    model-dependent logic. Only a few, run rarely, use the real model to check
    that the whole thing behaves, and those are loose checks, not exact ones. Lots
    of cheap certain tests at the bottom, a few expensive uncertain ones at the
    top. That shape is why every workflow in this course was built to run offline.
    """
    return {
        "bottom_many": "exact offline tests of tools and logic; run on every commit",
        "middle_some": "fake-model tests of model-dependent logic; still offline",
        "top_few": "real-model checks of end-to-end behaviour; loose, run rarely",
        "the_rule": "push tests down the pyramid; the lower they are, the more you trust them",
        "why_it_matters": "flaky expensive tests get ignored; cheap certain tests get run",
    }


# ================================================================
# DEBUGGING: finding out WHY an agent got it wrong
# ================================================================
# Testing tells you THAT something is wrong. Debugging is finding WHERE. An agent
# has three layers where a bug can hide, and the whole skill is isolating which
# one broke: the prompt you SENT, the answer the model GAVE, or the logic that
# HANDLED it. The tools below make each layer visible and reproducible.


class ReplayClient:
    """
    Plays back a saved list of answers, in order. This turns a flaky bug into a
    reproducible one.

    A real model is non-deterministic, so a bug that shows up once may vanish on
    the next run, which is a nightmare to fix. The moment you capture what the
    model actually said and wrap it in a ReplayClient, the bug becomes
    deterministic: it happens every single time, offline, with no model. You can
    now fix it and prove it is fixed. Capture once, replay forever.
    """

    def __init__(self, answers: list[str]) -> None:
        self.answers = list(answers)
        self.index = 0
        self.prompts_seen: list[str] = []

    def respond(self, prompt: str) -> str:
        self.prompts_seen.append(prompt)
        answer = self.answers[self.index]
        self.index += 1
        return answer


def diagnose_route(ticket: str, client: Responder) -> dict[str, str]:
    """
    Route a ticket, but return all three layers so you can SEE where it went wrong.

    When a route is wrong, this tells you which layer to blame:
      - if 'sent' is wrong, your prompt is the bug (fix the prompt)
      - if 'model_said' is surprising, the model is the problem (fix the prompt
        or add validation)
      - if 'we_decided' mishandles a fine 'model_said', your logic is the bug
    Isolating the layer is the whole debugging skill. Guessing is not debugging.
    """
    prompt = f"Classify this ticket as billing, technical, or account:\n{ticket}"
    raw = client.respond(prompt)
    cleaned = raw.strip().lower()
    valid = {"billing", "technical", "account"}
    decided = cleaned if cleaned in valid else "general"
    return {"sent": prompt, "model_said": raw, "we_decided": decided}


def safe_call(tool, *args) -> dict:
    """
    Call a tool, but never let its failure crash the whole agent.

    A tool can raise: a lookup misses, a service is down, an input is bad. In a
    production agent, one tool blowing up must not take down the run. This wraps a
    call so a failure becomes data the agent can handle, not an exception that
    ends everything. This is the Unit 2 reliability lesson, now as something you
    can test: you can prove your agent degrades gracefully.
    """
    try:
        return {"ok": True, "value": tool(*args)}
    except Exception as exc:  # noqa: BLE001  (intentional: turn any failure into data)
        return {"ok": False, "error": str(exc)}


DEBUGGING_MAP: dict[str, str] = {
    "the three layers": "the prompt you sent, the model's answer, your handling",
    "isolate the layer": "find which of the three broke; do not guess",
    "reproduce first": "capture the model's answer and replay it, so the bug is not flaky",
    "ReplayClient": "plays saved answers back, turning a flaky bug reproducible",
    "diagnose shows all three": "sent, model_said, we_decided, side by side",
    "safe_call": "a tool failure becomes data, not a crash; now testable",
}


def the_debugging_recipe() -> dict[str, str]:
    """
    The order to debug an agent in, stated for the exam and the job.

    Beginners debug by changing things at random and re-running, which with a
    non-deterministic model is hopeless. The disciplined order is: reproduce the
    bug deterministically first, then isolate which of the three layers is at
    fault, then fix only that layer, then keep the reproduction as a test so it
    never comes back. Reproduce, isolate, fix, lock in.
    """
    return {
        "1_reproduce": "capture the model's answer and replay it, so the bug is not flaky",
        "2_isolate": "use diagnose to see which layer broke: sent, said, or decided",
        "3_fix": "change only the layer at fault, not everything at once",
        "4_lock_in": "keep the replayed case as a test so the bug cannot return",
        "the_trap": "changing things at random against a non-deterministic model never converges",
    }
