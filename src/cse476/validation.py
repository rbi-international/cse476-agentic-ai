"""
Validation: the model can be confidently wrong. Check before you trust.

Unit 5 Lecture 2. Last lecture tested that YOUR code is correct. But your code can
be perfect and the agent can still fail, because the model can be confidently
wrong. It can invent a refund policy, cite a rule that does not exist, or return a
number it made up. It will say it with total confidence. Testing your own code
never catches this, because the bug is not in your code, it is in the model's
output.

The answer is validation: a gate between what the model says and what you act on.
You never trust the model's output directly. You check it against something you
control, and only then use it. This module builds three checks, from cheapest to
deepest.

  1. STRUCTURAL, is it even the right shape and one of the allowed answers?
  2. GROUNDING, did the claim come from the source, or was it invented?
  3. CROSS-CHECK, does a claimed fact match ground truth from a tool?

A hallucination is just an output that fails one of these checks. Every check
runs offline, because a validator is your own deterministic code judging the
model's output.
"""

from __future__ import annotations


# ---------------------------------------------------------------- 1. structural

def validate_choice(answer: str, allowed: set[str]) -> str | None:
    """
    Structural check: is the answer one of the allowed options at all?

    The cheapest, first line of defence. If you asked the model to pick a queue
    and it returns "the moon", that is not a valid choice, it is off the menu.
    Returns the cleaned answer if valid, or None if it should be rejected. You saw
    a version of this in Unit 4 routing; now we name it as validation.
    """
    cleaned = answer.strip().lower().rstrip(".!?")
    return cleaned if cleaned in allowed else None


def validate_number(answer: str, low: float, high: float) -> float | None:
    """
    Structural check for numbers: does it parse, and is it in a sane range?

    A model asked for a discount percent might return "150" or "free" or "about
    ten". A validator insists on a real number inside a plausible range, and
    rejects anything else rather than passing nonsense downstream.
    """
    try:
        value = float(answer.strip().rstrip("%"))
    except ValueError:
        return None
    return value if low <= value <= high else None


# ---------------------------------------------------------------- 2. grounding

def is_grounded(claim: str, source: str) -> bool:
    """
    Grounding check: are the claim's key facts actually in the source?

    This is the heart of hallucination detection. If the agent answers from a
    document, the answer must be supported by that document. We take the
    substantial words of the claim and require them to appear in the source. If
    the model asserts "60 days" but the source only says "30 days", the phrase is
    not in the source, so the claim is ungrounded, a hallucination.

    This is a deliberately simple, honest version of grounding. Real systems use
    embeddings and entailment models, but the principle is exactly this: a claim
    you cannot trace back to the source is a claim you should not trust.
    """
    key_words = [
        w.strip(".,!?").lower()
        for w in claim.split()
        if len(w) > 4 or any(ch.isdigit() for ch in w)  # keep numbers even if short
    ]
    if not key_words:
        return False
    low_source = source.lower()
    return all(word in low_source for word in key_words)


def find_unsupported_claim(claim: str, source: str) -> str | None:
    """
    Point at WHAT was invented, not just that something was.

    Returns the first key word of the claim that does not appear in the source,
    which is usually the invented fact. Naming the specific unsupported token
    turns "this is a hallucination" into "this is the part it made up", which is
    what you need to debug or to show a reviewer.
    """
    low_source = source.lower()
    for word in claim.split():
        w = word.strip(".,!?").lower()
        important = len(w) > 4 or any(ch.isdigit() for ch in w)
        if important and w not in low_source:
            return word.strip(".,!?")
    return None


# ---------------------------------------------------------------- 3. cross-check

def cross_check(claimed: object, actual: object) -> bool:
    """
    Cross-check: does the model's claimed fact match ground truth from a tool?

    The strongest check when you have a source of truth. If the model says the
    account balance is 5000 but the balance tool returns 4200, you do not argue,
    you reject the model and use the tool. The tool is the truth; the model is a
    suggestion. Never let a confident sentence override a real lookup.
    """
    return claimed == actual


# ---------------------------------------------------------------- the validator

def validate_answer(answer: str, source: str, allowed: set[str] | None = None) -> dict:
    """
    Run the checks and return a verdict, the gate an agent puts before acting.

    It reports whether the answer is safe to use and why not if it is not. An
    agent uses this to decide: if valid, act on the answer; if not, refuse, ask
    again, or fall back to a safe default. The verdict is data, so the agent can
    handle a bad answer instead of blindly trusting it.
    """
    if allowed is not None and validate_choice(answer, allowed) is None:
        return {"valid": False, "reason": "off the allowed menu", "answer": answer}
    invented = find_unsupported_claim(answer, source)
    if invented is not None:
        return {"valid": False, "reason": f"unsupported claim: {invented!r}", "answer": answer}
    return {"valid": True, "reason": "grounded in source", "answer": answer}


# ---------------------------------------------------------------- the mapping

VALIDATION_MAP: dict[str, str] = {
    "testing vs validation": "testing checks YOUR code; validation checks the MODEL's output",
    "structural check": "is the answer the right shape and on the allowed menu",
    "grounding check": "are the claim's facts actually in the source it used",
    "cross-check": "does a claimed fact match ground truth from a tool",
    "a hallucination": "an output that fails one of these checks",
    "the verdict is data": "the agent handles a bad answer, it does not blindly trust",
}


def why_validate() -> dict[str, str]:
    """
    Why a confident model still needs a gate, stated for the exam and the job.

    A model does not know when it is wrong, and it never sounds unsure. That
    combination, confident and sometimes wrong, is the whole danger: a plausible
    invented fact sails past a human who is not checking. Validation is the check
    the model cannot do for itself, applied by code that can. It is not distrust
    of the model, it is the seatbelt you wear even when you expect not to crash.
    """
    return {
        "the_problem": "the model can be wrong and always sounds confident",
        "why_testing_misses_it": "your code is correct; the bug is in the model's output",
        "the_fix": "gate the output: check it against something you control, then act",
        "grounding_is_key": "an answer you cannot trace to the source is one you should not trust",
        "tools_beat_talk": "when a tool and the model disagree, the tool wins",
    }
