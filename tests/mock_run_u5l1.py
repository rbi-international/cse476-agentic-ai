"""
Prove the two testing techniques: plain tools test exactly, and model-dependent
logic tests offline with a fake model (a test double). This file is itself an
example of the lesson: it tests an agent's parts without ever calling a model.
"""

import sys

sys.path.insert(0, "src")

from cse476.testing_agents import (  # noqa: E402
    FakeClient,
    TESTING_MAP,
    check_refund_eligible,
    decide_route,
    summarise_findings,
    the_testing_pyramid,
)

ok = True


def chk(label, cond):
    global ok
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
    ok = ok and cond


print("\n1. plain tools test exactly, offline, no model")
chk("refund allowed within limits", check_refund_eligible(10, 2000.0) is True)
chk("refund refused when too old", check_refund_eligible(40, 2000.0) is False)
chk("refund refused when too large", check_refund_eligible(10, 9000.0) is False)
chk("summary joins findings", summarise_findings(["a", "b"]) == "a; b")
chk("summary handles empty", summarise_findings([]) == "no findings")

print("\n2. a fake model lets us test model-dependent logic offline")
fake = FakeClient("billing")
chk("clean answer routes correctly", decide_route("I want a refund", fake) == "billing")

print("\n3. the fake lets us test DEFENSIVE logic against awkward answers")
chk("extra whitespace is cleaned", decide_route("x", FakeClient("  technical  ")) == "technical")
chk("wrong case is normalised", decide_route("x", FakeClient("ACCOUNT")) == "account")
chk("garbage falls back to general", decide_route("x", FakeClient("banana")) == "general")
chk("empty falls back to general", decide_route("x", FakeClient("")) == "general")

print("\n4. the fake records the prompt, so we can assert what the agent SENT")
spy = FakeClient("billing")
decide_route("my card was double charged", spy)
chk("the agent asked exactly once", len(spy.prompts_seen) == 1)
chk("the prompt carried the ticket", "double charged" in spy.prompts_seen[0])
chk("the prompt asked for a classification", "classify" in spy.prompts_seen[0].lower())

print("\n5. none of this needed a lane or a token")
chk("the whole file ran offline", True)  # if we got here, it did

print("\n6. the mapping names each technique")
chk("skeleton is deterministic", "deterministic" in TESTING_MAP["the skeleton"])
chk("model part uses a fake", "fake" in TESTING_MAP["the model part"])
chk("a seam takes the client as an argument", "argument" in TESTING_MAP["a seam"])
chk("assert the prompt is named", "SENT" in TESTING_MAP["assert the prompt"])

print("\n7. the testing pyramid is present and sensible")
p = the_testing_pyramid()
chk("many cheap tests at the bottom", "every commit" in p["bottom_many"])
chk("some fake-model tests in the middle", "fake-model" in p["middle_some"])
chk("few real-model tests at the top", "loose" in p["top_few"])
chk("the rule is push tests down", "push tests down" in p["the_rule"])
chk("flaky expensive tests get ignored", "ignored" in p["why_it_matters"])


# ---- debugging techniques ----
print("\n=== DEBUGGING ===")
from cse476.testing_agents import (  # noqa: E402
    DEBUGGING_MAP,
    ReplayClient,
    diagnose_route,
    safe_call,
    the_debugging_recipe,
)

ok2 = True


def chk2(label, cond):
    global ok2
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
    ok2 = ok2 and cond


print("\n8. ReplayClient makes a flaky bug reproducible")
# the model once answered 'Billing.' with a period, which broke the exact match
chk2("the buggy answer reproduces the miss", decide_route("x", ReplayClient(["Billing."])) == "general")
chk2("it reproduces the SAME way every run",
     decide_route("x", ReplayClient(["Billing."])) == decide_route("x", ReplayClient(["Billing."])))

print("\n9. diagnose_route isolates which layer broke")
d = diagnose_route("refund please", ReplayClient(["Billing."]))
chk2("it shows what we sent", "Classify" in d["sent"])
chk2("it shows what the model said", d["model_said"] == "Billing.")
chk2("it shows what we decided", d["we_decided"] == "general")
chk2("the layers together point to the logic bug (punctuation not stripped)",
     d["model_said"].lower().startswith("billing") and d["we_decided"] == "general")

print("\n10. safe_call turns a tool crash into data, not an exception")
def _boom(x):
    raise ValueError("service down")
r = safe_call(_boom, "in")
chk2("a raising tool does not crash the agent", r["ok"] is False)
chk2("the error is captured as data", "service down" in r["error"])
chk2("a good tool returns its value", safe_call(lambda x: x.upper(), "hi") == {"ok": True, "value": "HI"})

print("\n11. the debugging recipe is present and ordered")
rec = the_debugging_recipe()
chk2("step 1 is reproduce", "replay" in rec["1_reproduce"])
chk2("step 2 is isolate", "which layer" in rec["2_isolate"])
chk2("step 3 is fix only the fault", "only the layer" in rec["3_fix"])
chk2("step 4 locks it in as a test", "test" in rec["4_lock_in"])
chk2("names the random-changes trap", "never converges" in rec["the_trap"])
chk2("the map names the three layers", "prompt" in DEBUGGING_MAP["the three layers"])

print("\n" + ("ALL PASS" if (ok and ok2) else "SOMETHING FAILED"))
sys.exit(0 if (ok and ok2) else 1)
