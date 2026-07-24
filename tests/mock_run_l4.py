"""
Prove the planning strategies and the no progress detector, offline.
"""

import json
import sys
from types import SimpleNamespace

sys.path.insert(0, "src")

from cse476.planning import (  # noqa: E402
    NoProgress,
    act_only,
    compare,
    plan_then_execute,
    react,
    reflect,
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
                {
                    "id": c.id,
                    "type": "function",
                    "function": {"name": c.function.name, "arguments": c.function.arguments},
                }
                for c in cs
            ]
            or None,
        },
    )


class Fake:
    def __init__(self, script):
        self.script = list(script)
        self.calls = 0
        self.systems = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._c))

    def _c(self, **kw):
        self.calls += 1
        self.systems.append(kw["messages"][0]["content"])
        m = self.script.pop(0) if self.script else _msg("fallback")
        return SimpleNamespace(choices=[SimpleNamespace(message=m)])


FULL = ("get_room_availability", {"hotel": "Taj Palace", "date": "2026-08-14"})

print("\n1. act only thrashes on the same call")
f = Fake([_msg(calls=[FULL]) for _ in range(9)])
r = act_only(f, "m", "Book the Taj Palace", max_steps=6, verbose=False)
chk("ran to the budget", r["stopped_because"] == "budget")
chk("used all six steps", r["steps"] == 6)
chk("produced no reasoning", r["thoughts"] == [])

print("\n2. the detector catches the repeat")
det = NoProgress(repeat_limit=3)
f = Fake([_msg(calls=[FULL]) for _ in range(9)])
r = react(f, "m", "Book the Taj Palace", max_steps=6, detector=det, verbose=False)
chk("stopped for no progress, not budget", r["stopped_because"] == "no progress")
chk("stopped before the budget", r["steps"] < 6)
chk("explained itself", "Repeated the same call" in r["answer"])

print("\n3. the detector also catches identical observations from different calls")
det = NoProgress(repeat_limit=99, stuck_limit=3)
det.record("a", {"x": 1}, "No record found.")
det.record("b", {"x": 2}, "No record found.")
chk("two is not enough to fire", det.verdict() is None)
det.record("c", {"x": 3}, "No record found.")
chk("three identical observations fires", det.verdict() is not None)
chk("names the right reason", "identical" in (det.verdict() or ""))

print("\n4. the detector does not fire on healthy progress")
det = NoProgress()
det.record("get_room_availability", {"hotel": "Taj Palace"}, "0 rooms available.")
det.record("get_room_availability", {"hotel": "Radisson Blu"}, "11 rooms available.")
det.record("get_hotel_details", {"hotel": "Radisson Blu"}, "Rs 6200 per night.")
chk("stays quiet while things change", det.verdict() is None)

print("\n5. react captures reasoning in the transcript")
f = Fake([
    _msg("The Taj is the obvious first choice, so check it.", [FULL]),
    _msg("Full. Try the Radisson instead.",
         [("get_room_availability", {"hotel": "Radisson Blu", "date": "2026-08-14"})]),
    _msg("Radisson Blu has 11 rooms free on that date."),
])
r = react(f, "m", "Find a room on 2026-08-14", verbose=False)
chk("reached an answer", r["stopped_because"] == "goal met")
chk("kept two thoughts", len(r["thoughts"]) >= 2)
chk("recovered without a rule telling it to", "Radisson" in r["answer"])

print("\n6. plan then execute makes a plan first, with no tools")
f = Fake([
    _msg("1. list_hotels\n2. get_room_availability for each\n3. answer"),
    _msg(calls=[("list_hotels", {})]),
    _msg("Hotel Meera has rooms."),
])
r = plan_then_execute(f, "m", "Find a room on 2026-08-14", verbose=False)
chk("a plan was produced", "1." in r["plan"])
chk("planner ran before the executor", "planner" in f.systems[0].lower())
chk("executor was a different prompt", f.systems[0] != f.systems[1])
chk("reached an answer", "Meera" in r["answer"])

print("\n7. reflection revises a weak draft")
f = Fake([
    _msg("The draft gives no price and no date."),
    _msg("Radisson Blu, 11 rooms free on 2026-08-14, Rs 6200 per night."),
])
r = reflect(f, "m", "Find a room", "There is a room somewhere.")
chk("it was revised", r["revised"] is True)
chk("the improved answer came back", "6200" in r["final"])

print("\n8. reflection leaves a good draft alone")
f = Fake([_msg("APPROVED")])
good = "Radisson Blu, 11 rooms on 2026-08-14, Rs 6200 per night."
r = reflect(f, "m", "Find a room", good)
chk("not revised", r["revised"] is False)
chk("draft returned untouched", r["final"] == good)
chk("only one model call spent", f.calls == 1)

print("\n9. compare renders a table")
table = compare({
    "act only": {"steps": 6, "stopped_because": "budget", "answer": "none"},
    "react": {"steps": 3, "stopped_because": "goal met", "answer": "Radisson Blu"},
})
chk("both rows present", "act only" in table and "react" in table)

print("\n" + ("ALL PASS" if ok else "SOMETHING FAILED"))
sys.exit(0 if ok else 1)
