"""
Prove the defended tool executor survives every failure mode, offline.
Most of this needs no model at all: call_tool is pure Python.
"""

import json
import sys
from types import SimpleNamespace

sys.path.insert(0, "src")

from cse476.tools import (  # noqa: E402
    ToolError,
    call_tool,
    get_weather,
    get_weather_that_returns_junk,
    get_weather_that_throws,
    run_with_tools,
)

ok = True


def chk(label, cond):
    global ok
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
    ok = ok and cond


print("\n1. the happy path still works")
r = call_tool("get_weather", {"city": "Mumbai"})
chk("succeeded", r.ok)
chk("returned the real data", "Mumbai" in r.observation)
chk("one attempt", r.attempts == 1)

print("\n2. an unknown tool is blocked by the whitelist")
r = call_tool("delete_everything", {})
chk("did not run", not r.ok)
chk("observation names the real tools", "get_weather" in r.observation)
chk("observation is still a readable string", isinstance(r.observation, str))

print("\n3. a throwing tool is caught, not crashed")
reg = {"get_weather": get_weather_that_throws}
r = call_tool("get_weather", {"city": "Delhi"}, registry=reg, retries=2, backoff=0.0)
chk("reported as failed", not r.ok)
chk("retried the full number of times", r.attempts == 3)
chk("the last error is in the observation", "Connection reset" in r.observation)
chk("process did not die", True)

print("\n4. junk output is treated as failure even though nothing threw")
reg = {"get_weather": get_weather_that_returns_junk}
r = call_tool("get_weather", {"city": "Delhi"}, registry=reg)
chk("flagged unusable", not r.ok)
chk("did not pass null bytes to the model", "\x00" not in r.observation)
chk("told the model to treat it as no data", "no data" in r.observation.lower())

print("\n5. bad arguments are a permanent fault, not retried")
def needs_city(city: str) -> str:
    return get_weather(city)
r = call_tool("get_weather", {"wrong_arg": "x"}, registry={"get_weather": needs_city},
              retries=2, backoff=0.0)
chk("reported as failed", not r.ok)
chk("did NOT retry a permanent error", r.attempts == 1)
chk("observation mentions arguments", "argument" in r.observation.lower())

print("\n6. a transient failure that recovers on retry")
calls = {"n": 0}
def flaky(city: str) -> str:
    calls["n"] += 1
    if calls["n"] < 2:
        raise ToolError("temporary blip")
    return get_weather(city)
r = call_tool("get_weather", {"city": "Jammu"}, registry={"get_weather": flaky},
              retries=2, backoff=0.0)
chk("eventually succeeded", r.ok)
chk("took two attempts", r.attempts == 2)
chk("returned the real data after recovering", "Jammu" in r.observation)

print("\n7. every outcome is always a readable string")
for reg in (
    {"get_weather": get_weather_that_throws},
    {"get_weather": get_weather_that_returns_junk},
):
    r = call_tool("get_weather", {"city": "Delhi"}, registry=reg, retries=1, backoff=0.0)
    chk("observation is a non-empty string", isinstance(r.observation, str) and r.observation.strip())

# ---- the loop, with a scripted fake client ----

def _msg(content=None, calls=None):
    cs = []
    for i, (n, a) in enumerate(calls or []):
        cs.append(SimpleNamespace(id=f"c{i}", type="function",
            function=SimpleNamespace(name=n, arguments=json.dumps(a))))
    return SimpleNamespace(role="assistant", content=content, tool_calls=cs or None,
        model_dump=lambda **k: {"role": "assistant", "content": content,
            "tool_calls": [{"id": c.id, "type": "function",
                "function": {"name": c.function.name, "arguments": c.function.arguments}}
                for c in cs] or None})

class Fake:
    def __init__(self, script):
        self.script = list(script)
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._c))
    def _c(self, **kw):
        m = self.script.pop(0) if self.script else _msg("fallback")
        return SimpleNamespace(choices=[SimpleNamespace(message=m)])

print("\n8. the loop survives a broken tool and lets the model recover")
f = Fake([
    _msg(calls=[("get_weather", {"city": "Delhi"})]),   # this one will fail
    _msg("I could not reach the weather service for Delhi, sorry."),
])
r = run_with_tools(f, "m", "Weather in Delhi?",
                   registry={"get_weather": get_weather_that_throws}, verbose=False)
chk("reached a final answer despite the failure", r.stopped_because == "goal met")
chk("the failed call was recorded", any(not c.ok for c in r.tool_calls))
chk("the model saw the failure and was honest", "could not" in r.answer.lower())

print("\n9. the loop still handles the happy path")
f = Fake([
    _msg(calls=[("get_weather", {"city": "Mumbai"})]),
    _msg("It is 31C and humid in Mumbai with light rain."),
])
r = run_with_tools(f, "m", "Weather in Mumbai?", verbose=False)
chk("succeeded", r.stopped_because == "goal met")
chk("the successful call was recorded", any(c.ok for c in r.tool_calls))

print("\n" + ("ALL PASS" if ok else "SOMETHING FAILED"))
sys.exit(0 if ok else 1)
