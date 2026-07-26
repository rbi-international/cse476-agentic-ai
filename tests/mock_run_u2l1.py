"""
Prove the three triage shapes differ exactly as the lecture claims, offline.
"""

import json
import sys
from types import SimpleNamespace

sys.path.insert(0, "src")

from cse476.triage import (  # noqa: E402
    QUEUES,
    compare,
    triage_agent,
    triage_router,
    triage_workflow,
)

ok = True


def chk(label, cond):
    global ok
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
    ok = ok and cond


def _msg(content=None, calls=None):
    cs = []
    for i, (n, a) in enumerate(calls or []):
        cs.append(
            SimpleNamespace(
                id=f"c{i}",
                type="function",
                function=SimpleNamespace(name=n, arguments=json.dumps(a)),
            )
        )
    return SimpleNamespace(
        role="assistant",
        content=content,
        tool_calls=cs or None,
        model_dump=lambda **k: {
            "role": "assistant",
            "content": content,
            "tool_calls": [
                {"id": c.id, "type": "function",
                 "function": {"name": c.function.name, "arguments": c.function.arguments}}
                for c in cs
            ] or None,
        },
    )


class Fake:
    def __init__(self, script):
        self.script = list(script)
        self.calls = 0
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._c))

    def _c(self, **kw):
        self.calls += 1
        m = self.script.pop(0) if self.script else _msg("fallback")
        return SimpleNamespace(choices=[SimpleNamespace(message=m)])


print("\n1. workflow uses no model at all")
t = triage_workflow("I was charged twice for my subscription.")
chk("routed by keyword to billing", t.queue == "billing")
chk("zero model calls", t.model_calls == 0)
chk("labelled as a workflow", t.shape == "workflow")

print("\n2. workflow catches abuse and flags escalation")
t = triage_workflow("Someone hacked my account and is sending spam.")
chk("routed to abuse", t.queue == "abuse")
chk("escalate flag set", t.escalate is True)

print("\n3. workflow defaults safely when no rule matches")
t = triage_workflow("zxcvbnm qwerty")
chk("defaulted to technical", t.queue == "technical")
chk("still zero cost", t.model_calls == 0)

print("\n4. router makes exactly one model call")
f = Fake([_msg("billing")])
t = triage_router(f, "m", "I want a refund.")
chk("routed to billing", t.queue == "billing")
chk("exactly one model call", t.model_calls == 1)
chk("Fake also saw exactly one call", f.calls == 1)
chk("labelled as a router", t.shape == "router")

print("\n5. router defends against an off-menu answer")
f = Fake([_msg("i think probably the billing department maybe")])
t = triage_router(f, "m", "refund please")
chk("invalid choice defaulted to technical", t.queue == "technical")
chk("reason explains the fallback", "not a valid queue" in t.reason)

print("\n6. agent can decide in a single step")
f = Fake([_msg("QUEUE: billing\nThe customer was double charged.")])
t = triage_agent(f, "m", "I was charged twice.")
chk("parsed the queue from the answer", t.queue == "billing")
chk("one model call when it decides immediately", t.model_calls == 1)
chk("labelled as an agent", t.shape == "agent")

print("\n7. agent can use tools first, costing more calls")
f = Fake([
    _msg(calls=[("list_queues", {})]),
    _msg(calls=[("lookup_queue_policy", {"queue": "abuse"})]),
    _msg("QUEUE: abuse\nAccount takeover, needs immediate escalation."),
])
t = triage_agent(f, "m", "Someone is in my account sending spam.")
chk("reached the abuse queue", t.queue == "abuse")
chk("took three model calls", t.model_calls == 3)
chk("escalation flagged", t.escalate is True)

print("\n8. the punchline: same ticket, wildly different cost")
# workflow: 0 calls, router: 1 call, agent: 3 calls, identical outcome
wf = triage_workflow("I was charged twice.")
f = Fake([_msg("billing")])
rt = triage_router(f, "m", "I was charged twice.")
f = Fake([
    _msg(calls=[("list_queues", {})]),
    _msg(calls=[("lookup_queue_policy", {"queue": "billing"})]),
    _msg("QUEUE: billing\nDouble charge."),
])
ag = triage_agent(f, "m", "I was charged twice.")
chk("all three reached billing", wf.queue == rt.queue == ag.queue == "billing")
chk("but cost 0, 1 and 3 calls respectively",
    (wf.model_calls, rt.model_calls, ag.model_calls) == (0, 1, 3))

print("\n9. compare renders all three")
table = compare({"workflow": wf, "router": rt, "agent": ag})
chk("all three shapes present", all(s in table for s in ("workflow", "router", "agent")))

print("\n10. every queue name is known")
chk("five queues on file", len(QUEUES) == 5)

print("\n" + ("ALL PASS" if ok else "SOMETHING FAILED"))
sys.exit(0 if ok else 1)
