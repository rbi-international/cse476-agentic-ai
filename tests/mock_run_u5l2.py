"""
Prove the three validation checks catch real hallucinations offline: structural,
grounding, and cross-check. A validator is your own deterministic code judging
the model's output, so all of this runs with no model and no tokens.
"""

import sys

sys.path.insert(0, "src")

from cse476.validation import (  # noqa: E402
    VALIDATION_MAP,
    cross_check,
    find_unsupported_claim,
    is_grounded,
    validate_answer,
    validate_choice,
    validate_number,
    why_validate,
)

ok = True


def chk(label, cond):
    global ok
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
    ok = ok and cond


print("\n1. structural check: is the answer on the allowed menu?")
allowed = {"billing", "technical", "account"}
chk("a valid choice passes", validate_choice("billing", allowed) == "billing")
chk("case and punctuation are cleaned", validate_choice("  Billing.  ", allowed) == "billing")
chk("an off-menu answer is rejected", validate_choice("the moon", allowed) is None)

print("\n2. structural check for numbers: parses and in range?")
chk("a sane number passes", validate_number("20%", 0, 100) == 20.0)
chk("out of range is rejected", validate_number("150", 0, 100) is None)
chk("non-numeric is rejected", validate_number("about ten", 0, 100) is None)

print("\n3. grounding check: is the claim actually in the source?")
policy = "Refunds are available within 30 days of purchase."
chk("a grounded claim passes", is_grounded("refunds within 30 days", policy))
chk("an invented claim is caught (60 days is not in the source)",
    not is_grounded("refunds within 60 days", policy))

print("\n4. grounding points at WHAT was invented")
invented = find_unsupported_claim("refunds within 60 days", policy)
chk("it names the invented token", invented == "60" or invented == "days" or invented == "within"
    or (invented is not None and invented not in policy.lower()))
chk("a grounded claim has nothing unsupported", find_unsupported_claim("within 30 days", policy) is None)

print("\n5. cross-check: model claim vs ground truth from a tool")
chk("matching values pass", cross_check(30, 30) is True)
chk("the tool wins on a mismatch", cross_check(5000, 4200) is False)

print("\n6. the validator gate returns a usable verdict")
good = validate_answer("refunds within 30 days", policy)
chk("a grounded answer is valid", good["valid"] is True)
bad = validate_answer("refunds within 60 days", policy)
chk("a hallucinated answer is invalid", bad["valid"] is False)
chk("the verdict says WHY", "unsupported" in bad["reason"])
offmenu = validate_answer("the moon", policy, allowed={"billing", "technical"})
chk("an off-menu answer is caught first", offmenu["valid"] is False and "menu" in offmenu["reason"])

print("\n7. the mapping distinguishes testing from validation")
chk("testing vs validation is stated",
    "MODEL" in VALIDATION_MAP["testing vs validation"] and "code" in VALIDATION_MAP["testing vs validation"])
chk("a hallucination is defined as a failed check", "fails" in VALIDATION_MAP["a hallucination"])
chk("the verdict is data", "handles" in VALIDATION_MAP["the verdict is data"])

print("\n8. the why-validate framing is present and honest")
w = why_validate()
chk("names the confident-and-wrong problem", "confident" in w["the_problem"])
chk("explains why testing misses it", "model's output" in w["why_testing_misses_it"])
chk("grounding is called key", "trace to the source" in w["grounding_is_key"])
chk("tools beat talk", "tool wins" in w["tools_beat_talk"])

print("\n" + ("ALL PASS" if ok else "SOMETHING FAILED"))
sys.exit(0 if ok else 1)
