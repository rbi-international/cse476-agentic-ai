"""
Prove the loop works without spending a single API call.

The network in this sandbox cannot reach models.github.ai, and CI has no key
either, so we stand in a fake client that replays a scripted sequence of model
responses. That is enough to verify the part that is actually ours: the control
flow, the message shapes, the whitelist, and the budget guard.
"""

import json
import sys
from types import SimpleNamespace

sys.path.insert(0, "src")

from cse476.tiny_agent import REGISTRY, run_agent  # noqa: E402


def _msg(content=None, tool_calls=None):
    """Build an object shaped like an SDK ChatCompletionMessage."""
    calls = []
    for i, (name, args) in enumerate(tool_calls or []):
        calls.append(
            SimpleNamespace(
                id=f"call_{i}",
                type="function",
                function=SimpleNamespace(name=name, arguments=json.dumps(args)),
            )
        )
    m = SimpleNamespace(
        role="assistant",
        content=content,
        tool_calls=calls or None,
        model_dump=lambda **kw: {
            "role": "assistant",
            "content": content,
            "tool_calls": [
                {
                    "id": c.id,
                    "type": "function",
                    "function": {
                        "name": c.function.name,
                        "arguments": c.function.arguments,
                    },
                }
                for c in calls
            ]
            or None,
        },
    )
    return m


class FakeClient:
    def __init__(self, script):
        self.script = list(script)
        self.calls = 0
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.calls += 1
        assert "tools" in kwargs, "tool schema was not sent to the model"
        assert kwargs["messages"][0]["role"] == "system"
        m = self.script.pop(0) if self.script else _msg("fallback")
        return SimpleNamespace(choices=[SimpleNamespace(message=m)])


def check(label, cond):
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
    return cond


ok = True

print("\nscenario 1: two tools, then a final answer")
client = FakeClient(
    [
        _msg(tool_calls=[("get_room_availability", {"hotel": "Taj Palace", "date": "2026-08-14"})]),
        _msg(tool_calls=[("get_nightly_rate", {"hotel": "Taj Palace"})]),
        _msg(content="Taj Palace has 3 rooms on 14 Aug at Rs 14500 per night."),
    ]
)
out = run_agent(client, "fake-model", "Rooms and price at Taj Palace on 2026-08-14?")
ok &= check("returns the final answer", "3 rooms" in out)
ok &= check("made exactly 3 model calls", client.calls == 3)

print("\nscenario 2: model invents a tool that does not exist")
client = FakeClient(
    [
        _msg(tool_calls=[("send_email", {"to": "manager@lpu.in"})]),
        _msg(content="I do not have an email tool, so I cannot send that."),
    ]
)
out = run_agent(client, "fake-model", "Email the manager.", verbose=False)
ok &= check("whitelist blocked it, loop survived", "cannot send" in out)
ok &= check("send_email never entered the registry", "send_email" not in REGISTRY)

print("\nscenario 3: model never stops asking for tools")
client = FakeClient(
    [_msg(tool_calls=[("get_nightly_rate", {"hotel": "Taj Palace"})]) for _ in range(50)]
)
out = run_agent(client, "fake-model", "Loop forever please.", max_steps=4, verbose=False)
ok &= check("budget guard fired", "Stopped after 4 steps" in out)
ok &= check("stopped at exactly 4 model calls", client.calls == 4)

print("\nscenario 4: bad arguments do not crash the process")
client = FakeClient(
    [
        _msg(tool_calls=[("get_room_availability", {"hotel": "Nowhere", "date": "2026-08-14"})]),
        _msg(content="I could not find that hotel."),
    ]
)
out = run_agent(client, "fake-model", "Rooms at Nowhere?", verbose=False)
ok &= check("unknown hotel handled by the tool itself", "could not find" in out)

print()
print("ALL PASS" if ok else "SOMETHING FAILED")
sys.exit(0 if ok else 1)
