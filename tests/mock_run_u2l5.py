"""
Prove session memory carries context across turns, stays bounded, and that the
invariant approach tests a non-deterministic system correctly. All offline.
"""

import sys

sys.path.insert(0, "src")

from cse476.context import (  # noqa: E402
    CheckResult,
    ContextAgent,
    Session,
    all_passed,
    check_invariants,
    field_in,
    field_present,
    needs_context,
    queue_is_valid,
)

ok = True


def chk(label, cond):
    global ok
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
    ok = ok and cond


print("\n1. a session remembers the transcript")
sess = Session()
sess.add("user", "hello")
sess.add("assistant", "hi")
chk("both turns are stored", len(sess.turns) == 2)
chk("transcript reads back", "user: hello" in sess.transcript())

print("\n2. a session keeps pinned facts separate from the transcript")
sess.remember("queue", "billing")
chk("fact is recalled", sess.recall("queue") == "billing")
chk("a missing fact returns None", sess.recall("nope") is None)

print("\n3. memory is bounded, oldest turns drop first")
sess = Session(max_turns=3)
for i in range(6):
    sess.add("user", f"m{i}")
chk("never exceeds the bound", len(sess.turns) == 3)
chk("kept the most recent", sess.turns[-1].text == "m5")
chk("dropped the oldest", all(t.text != "m0" for t in sess.turns))

print("\n4. pinned facts survive even when the transcript is trimmed")
sess = Session(max_turns=2)
sess.remember("queue", "abuse")
for i in range(5):
    sess.add("user", f"m{i}")
chk("transcript was trimmed", len(sess.turns) == 2)
chk("but the fact survived", sess.recall("queue") == "abuse")

print("\n5. reference detection spots follow-ups")
chk("'make it urgent' needs context", needs_context("make it urgent"))
chk("'the ticket' needs context", needs_context("close the ticket"))
chk("a fresh request does not", not needs_context("route ticket 5 to billing"))

print("\n6. the agent carries context across turns")
agent = ContextAgent()
first = agent.handle("route ticket 12 to billing")
chk("first turn routes", "billing" in first)
second = agent.handle("make it urgent")
chk("second turn understood 'it'", "urgent" in second.lower())
chk("second turn knew which ticket", "billing" in second.lower())

print("\n7. a follow-up with no prior ticket fails honestly")
agent = ContextAgent()
reply = agent.handle("make it urgent")
chk("does not invent a ticket", "do not have" in reply.lower())

print("\n8. the whole conversation is in the session afterwards")
agent = ContextAgent()
agent.handle("route ticket 3 to sales")
agent.handle("make it urgent")
chk("all four turns recorded", len(agent.session.turns) == 4)
chk("queue was pinned", agent.session.recall("queue") == "sales")
chk("priority was pinned", agent.session.recall("priority") == "urgent")

print("\n9. invariants test a result by what must always be true")
good = {"queue": "billing", "priority": "normal", "assigned_to": "billing-team"}
results = check_invariants(good, {
    "queue is valid": queue_is_valid(),
    "priority present": field_present("priority"),
    "priority is allowed": field_in("priority", ["normal", "urgent"]),
})
chk("a good result passes every invariant", all_passed(results))

print("\n10. invariants catch a bad result the model might produce")
bad = {"queue": "not-a-real-queue", "priority": "", "assigned_to": "x"}
results = check_invariants(bad, {
    "queue is valid": queue_is_valid(),
    "priority present": field_present("priority"),
})
chk("invalid queue is caught", not any(r.name == "queue is valid" and r.passed for r in results))
chk("empty priority is caught", not any(r.name == "priority present" and r.passed for r in results))
chk("the whole check fails", not all_passed(results))

print("\n11. a raising predicate is caught, not crashed")
results = check_invariants({}, {"explodes": lambda out: out["missing"] == 1})
chk("did not crash", isinstance(results[0], CheckResult))
chk("recorded as a failure", not results[0].passed)

print("\n" + ("ALL PASS" if ok else "SOMETHING FAILED"))
sys.exit(0 if ok else 1)
