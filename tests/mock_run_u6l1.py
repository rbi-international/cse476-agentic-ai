"""
Prove responsible AI as testable checks: fairness (decision invariant to group),
transparency (a readable reason), accountability (a reviewable record). All
offline and deterministic, because a principle you cannot check you cannot keep.
"""

import sys

sys.path.insert(0, "src")

from cse476.responsible import (
    RESPONSIBLE_MAP,
    DecisionRecord,
    decide,
    decide_with_reason,
    decision_record,
    find_unfairness,
    is_fair,
    why_responsible,
)

ok = True


def chk(label, cond):
    global ok
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
    ok = ok and cond


print("\n1. the decision is sound on the relevant facts")
chk("good income and credit approves", decide(40000, 700) == "approve")
chk("low income declines", decide(20000, 700) == "decline")
chk("low credit declines", decide(40000, 600) == "decline")

print("\n2. FAIRNESS: flipping only the group does not change the decision")
chk("approved case is fair across groups", is_fair(decide, 40000, 700, ["A", "B", "C"]))
chk("declined case is fair across groups", is_fair(decide, 20000, 700, ["A", "B", "C"]))
chk("a fair decision has nothing to flag", find_unfairness(decide, 40000, 700, ["A", "B"]) is None)

print("\n3. the fairness test would CATCH a biased decision")
def biased(income, credit_score, applicant_group=None):
    # deliberately unfair: group B is held to a higher bar
    bar = 750 if applicant_group == "B" else 650
    return "approve" if (income >= 30000 and credit_score >= bar) else "decline"
chk("bias is detected (not fair)", not is_fair(biased, 40000, 700, ["A", "B"]))
flagged = find_unfairness(biased, 40000, 700, ["A", "B"])
chk("it names who was treated differently", flagged == {"A": "approve", "B": "decline"})

print("\n4. TRANSPARENCY: every decision carries a readable reason")
v = decide_with_reason(25000, 700)
chk("it returns the decision", v["decision"] == "decline")
chk("it returns reasons", len(v["because"]) == 2)
chk("the reason names the income fact", any("income" in r for r in v["because"]))
chk("the reason names the credit fact", any("credit" in r for r in v["because"]))
chk("the reason matches the decision (income below)", any("below" in r for r in v["because"]))

print("\n5. ACCOUNTABILITY: a reviewable record exists")
rec = decision_record("loan-agent-v1", 25000, 700)
chk("it is a DecisionRecord", isinstance(rec, DecisionRecord))
chk("it names the agent", rec.agent == "loan-agent-v1")
chk("it captures the inputs", rec.inputs["income"] == 25000)
chk("it captures the outcome", rec.outcome == "decline")
chk("it captures the reason", len(rec.reason) == 2)
chk("it is reviewable", rec.is_reviewable() is True)

print("\n6. an incomplete record is not reviewable")
empty = DecisionRecord(agent="", inputs={}, outcome="decline", reason=[])
chk("a record with no who/what/why is not reviewable", empty.is_reviewable() is False)

print("\n7. the mapping and framing are present and honest")
chk("responsible AI is about should, not works", "should do" in RESPONSIBLE_MAP["responsible AI"])
chk("fairness is invariance to who", "who the person is" in RESPONSIBLE_MAP["fairness"])
chk("a principle you cannot check", "cannot keep" in RESPONSIBLE_MAP["a principle you cannot check"])
w = why_responsible()
chk("scale is named as the danger", "harms many" in w["scale"])
chk("autonomy means built-in checks", "built in" in w["autonomy"])
chk("fairness check is the flip test", "must not move" in w["fairness_check"])

print("\n" + ("ALL PASS" if ok else "SOMETHING FAILED"))
sys.exit(0 if ok else 1)
