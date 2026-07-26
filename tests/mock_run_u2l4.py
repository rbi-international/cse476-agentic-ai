"""
Prove the pipeline chains steps, stops cleanly on failure, and that the event
bus reacts to events. All offline, no model.
"""

import sys

sys.path.insert(0, "src")

from cse476.pipeline import (  # noqa: E402
    Event,
    EventBus,
    Pipeline,
    StepResult,
    assign_ticket,
    build_intake_pipeline,
    classify_ticket,
    validate_ticket,
)

ok = True


def chk(label, cond):
    global ok
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
    ok = ok and cond


print("\n1. a full pipeline runs every step and threads state through")
pipe = build_intake_pipeline()
state, log = pipe.run({"text": "I was charged twice and want a refund."})
chk("completed", log.completed)
chk("classified as billing", state["queue"] == "billing")
chk("enriched with the billing SLA", state["sla_hours"] == 24)
chk("assigned to the billing team", state["assigned_to"] == "billing-team")
chk("ran all four steps", len(log.steps) == 4)

print("\n2. state genuinely flows from one step to the next")
# enrich could not have worked unless classify put 'queue' in the state
chk("enrich depended on classify's output", "sla_hours" in state)

print("\n3. abuse tickets come out urgent")
state, log = pipe.run({"text": "someone hacked my account"})
chk("classified as abuse", state["queue"] == "abuse")
chk("priority is urgent", state["priority"] == "urgent")
chk("SLA is the strict one", state["sla_hours"] == 1)

print("\n4. a bad ticket stops the pipeline at step one")
state, log = pipe.run({"text": ""})
chk("did not complete", not log.completed)
chk("stopped at validate", log.stopped_at == "validate")
chk("only the first step ran", len(log.steps) == 1)
chk("never reached classify", "queue" not in state)

print("\n5. stopping keeps the work that did succeed")
# a pipeline where step 3 fails: steps 1 and 2 results survive in state
def failing_enrich(state):
    return StepResult(ok=False, note="deliberate failure")

pipe2 = (
    Pipeline("partial")
    .step("validate", validate_ticket)
    .step("classify", classify_ticket)
    .step("enrich", failing_enrich)
    .step("assign", assign_ticket)
)
state, log = pipe2.run({"text": "login broken"})
chk("stopped at enrich", log.stopped_at == "enrich")
chk("classify's work survived the stop", state.get("queue") == "account")
chk("assign never ran", "assigned_to" not in state)

print("\n6. a step that raises is caught, not crashed")
def exploding(state):
    raise ValueError("boom")

pipe3 = Pipeline("risky").step("boom", exploding)
state, log = pipe3.run({"text": "x"})
chk("did not crash the process", not log.completed)
chk("recorded the error", "boom" in log.stopped_at)

print("\n7. the run log reads as a clean record")
_, log = build_intake_pipeline().run({"text": "refund please"})
text = str(log)
chk("shows step names", "validate" in text and "assign" in text)
chk("shows the outcome", "completed" in text)

# ---- event-driven ----

print("\n8. an event bus runs every subscribed handler")
bus = EventBus()
hits = []
bus.on("ticket.created", lambda e: hits.append(("logger", e.payload["id"])))
bus.on("ticket.created", lambda e: hits.append(("notifier", e.payload["id"])))
ran = bus.emit(Event("ticket.created", {"id": 7}))
chk("both handlers reacted", ran == 2)
chk("both saw the same event", hits == [("logger", 7), ("notifier", 7)])

print("\n9. an event with no listeners is harmless")
ran = bus.emit(Event("nobody.listening"))
chk("zero handlers ran", ran == 0)
chk("but the event was still dispatched", "nobody.listening" in bus.dispatched)

print("\n10. one broken handler does not silence the others")
bus2 = EventBus()
survived = []
bus2.on("x", lambda e: (_ for _ in ()).throw(RuntimeError("bad handler")))
bus2.on("x", lambda e: survived.append("ok"))
ran = bus2.emit(Event("x"))
chk("the good handler still ran", survived == ["ok"])
chk("only the working handler counted", ran == 1)

print("\n" + ("ALL PASS" if ok else "SOMETHING FAILED"))
sys.exit(0 if ok else 1)
