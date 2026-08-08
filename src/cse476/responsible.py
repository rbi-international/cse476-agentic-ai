"""
Responsible AI: turning principles into checks your agent actually runs.

Unit 6 Lecture 1. The whole course so far made an agent that works, is reliable,
uses real frameworks, cooperates with other agents, and ships. This unit asks a
different question: should it do what it does, and can you stand behind it? That
is responsible AI, and the danger is treating it as a poster on the wall,
fairness, transparency, accountability, three nice words and no code.

This module refuses that. It turns each principle into something you can build
and test, because a principle you cannot check is a principle you cannot keep.

Think of a good loan officer. A responsible one (1) treats similar people the
same regardless of who they are (fairness), (2) can explain every decision in
plain words (transparency), and (3) leaves a record so a decision can be reviewed
and someone held responsible (accountability). A responsible agent is the same,
and each of those becomes a function here.

    decide            a decision that must not depend on who the applicant is
    is_fair           flip only the protected attribute; the decision must not move
    decide_with_reason  every decision carries a human-readable reason
    decision_record   an auditable record: what was decided, on what, and why
    RESPONSIBLE_MAP   the three principles, named
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ---------------------------------------------------------------- the decision

# WHY a plain decision first: responsible AI is not a wrapper you bolt on, it is a
# property of the decision itself. So we start with an honest decision function
# and then check that it has the three properties. A decision that only becomes
# fair once you add a checker was never fair; the checker just reveals it.

def decide(income: float, credit_score: int, applicant_group: str | None = None) -> str:
    """
    Decide a simple loan case. Approve on income and credit only.

    The applicant_group argument is accepted but MUST NOT be used. It is here on
    purpose, so the fairness test can pass different groups and prove the decision
    ignores them. A responsible decision depends on what is relevant (income,
    credit) and never on who the person is (their group).
    """
    return "approve" if (income >= 30000 and credit_score >= 650) else "decline"


# ---------------------------------------------------------------- 1. fairness

def is_fair(decision_fn, income: float, credit_score: int, groups: list[str]) -> bool:
    """
    Fairness as a test: flip only the protected attribute, the decision must not move.

    We call the decision with the same income and credit for every group. If the
    outcome is identical across all of them, the decision did not depend on the
    group, which is exactly what fairness means here. If the outcome changes when
    only the group changes, that is the definition of an unfair decision, and this
    test catches it.
    """
    outcomes = {decision_fn(income, credit_score, applicant_group=g) for g in groups}
    return len(outcomes) == 1


def find_unfairness(decision_fn, income: float, credit_score: int, groups: list[str]) -> dict | None:
    """
    Point at the unfairness, not just report that it exists.

    Returns the differing outcomes per group when the decision is not fair, so you
    can see who got treated differently. Naming the disparate outcome is what you
    need to fix the rule or show a reviewer, exactly as in the debugging lecture.
    """
    outcomes = {g: decision_fn(income, credit_score, applicant_group=g) for g in groups}
    if len(set(outcomes.values())) == 1:
        return None
    return outcomes


# ---------------------------------------------------------------- 2. transparency

def decide_with_reason(income: float, credit_score: int) -> dict:
    """
    Transparency: every decision comes with a reason a human can read.

    A decision with no reason is a black box, and a black box cannot be trusted,
    appealed, or corrected. This returns the outcome together with the specific
    facts that produced it, in plain language. Notice the reason is built from the
    same thresholds the decision uses, so it cannot drift from the real logic; it
    is the logic, explained.
    """
    reasons = [
        f"income {income:.0f} is {'at or above' if income >= 30000 else 'below'} the 30000 threshold",
        f"credit score {credit_score} is {'at or above' if credit_score >= 650 else 'below'} the 650 threshold",
    ]
    decision = "approve" if (income >= 30000 and credit_score >= 650) else "decline"
    return {"decision": decision, "because": reasons}


# ---------------------------------------------------------------- 3. accountability

@dataclass
class DecisionRecord:
    """
    Accountability: a reviewable record of a decision.

    Fairness and transparency are about the decision now; accountability is about
    the decision later. When someone asks months from now why an applicant was
    declined, there must be a record: which agent decided, on what inputs, what it
    decided, and why. Without that record, no one can be held responsible, because
    no one can even reconstruct what happened.
    """

    agent: str
    inputs: dict
    outcome: str
    reason: list[str]
    tags: list[str] = field(default_factory=list)

    def is_reviewable(self) -> bool:
        """A record is reviewable only if it has the who, the what, and the why."""
        return bool(self.agent) and bool(self.inputs) and bool(self.reason)


def decision_record(agent: str, income: float, credit_score: int) -> DecisionRecord:
    """Make an accountable record by deciding and capturing the reason together."""
    verdict = decide_with_reason(income, credit_score)
    return DecisionRecord(
        agent=agent,
        inputs={"income": income, "credit_score": credit_score},
        outcome=verdict["decision"],
        reason=verdict["because"],
    )


# ---------------------------------------------------------------- the mapping

RESPONSIBLE_MAP: dict[str, str] = {
    "responsible AI": "not whether the agent works, but whether it should do what it does",
    "fairness": "the decision does not depend on who the person is, only on what is relevant",
    "transparency": "every decision carries a reason a human can read and question",
    "accountability": "a reviewable record exists, so a decision can be traced and owned",
    "a principle you cannot check": "is a principle you cannot keep; make each one a test",
    "the harm": "an agent acts at scale, so an unfair or opaque rule harms many, fast",
}


def why_responsible() -> dict[str, str]:
    """
    Why this matters more for an agent than for a one-off model, for the exam.

    A model gives an answer; an agent takes actions, many of them, automatically,
    for lots of people. That scale is the point: a single biased rule in a chatbot
    annoys one user, but the same rule in an agent that processes ten thousand
    applications a day harms ten thousand people before anyone notices. Responsible
    AI is not slower or softer engineering; it is the checks that keep an
    autonomous system from doing harm at the speed and scale it operates.
    """
    return {
        "scale": "an agent acts automatically and often, so a bad rule harms many, fast",
        "autonomy": "no human reviews each action, so the checks must be built in",
        "fairness_check": "flip the protected attribute; the decision must not move",
        "transparency_check": "no decision without a readable reason attached",
        "accountability_check": "no action without a record that can be reviewed later",
    }
