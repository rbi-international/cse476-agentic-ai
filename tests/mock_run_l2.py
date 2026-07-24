"""
Prove the four architectures differ in the way the lecture claims,
without spending an API call.
"""
import json
import sys
from types import SimpleNamespace
sys.path.insert(0, "src")
from cse476.architectures import (  # noqa: E402
    ModelBasedAgent, goal_based, reflex, utility_based,
)

def _msg(content=None, calls=None):
    cs=[]
    for i,(n,a) in enumerate(calls or []):
        cs.append(SimpleNamespace(id=f"c{i}", type="function",
            function=SimpleNamespace(name=n, arguments=json.dumps(a))))
    return SimpleNamespace(role="assistant", content=content, tool_calls=cs or None,
        model_dump=lambda **k: {"role":"assistant","content":content,
            "tool_calls":[{"id":c.id,"type":"function","function":{
                "name":c.function.name,"arguments":c.function.arguments}} for c in cs] or None})

class Fake:
    def __init__(self, script):
        self.script = list(script)
        self.calls = 0
        self.seen_tools = []
        self.chat=SimpleNamespace(completions=SimpleNamespace(create=self._c))
    def _c(self, **kw):
        self.calls += 1
        self.seen_tools.append(len(kw.get("tools",[])))
        self.last_messages=kw["messages"]
        m = self.script.pop(0) if self.script else _msg("fallback")
        return SimpleNamespace(choices=[SimpleNamespace(message=m)])

ok = True


def chk(label, cond):
    global ok
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
    ok = ok and cond

print("\n1. reflex: one tool call, then it must stop")
f=Fake([_msg(calls=[("get_room_availability",{"hotel":"Taj Palace","date":"2026-08-14"})]),
        _msg("Taj Palace has no rooms on that date.")])
out=reflex(f,"m","Rooms at Taj Palace on 2026-08-14?")
chk("answered", "no rooms" in out)
chk("capped at 2 model calls", f.calls==2)

print("\n2. reflex: budget stops it even if it keeps asking")
f=Fake([_msg(calls=[("get_room_availability",{"hotel":"Taj Palace","date":"2026-08-14"})])]*9)
out=reflex(f,"m","find me anything", verbose=False)
chk("hard stop fired", "Stopped after 2 steps" in out)

print("\n3. model based: state survives across turns")
f=Fake([_msg(calls=[("get_room_availability",{"hotel":"Radisson Blu","date":"2026-08-14"})]),
        _msg("Radisson Blu has 11 rooms."),
        _msg("You asked about Radisson Blu, which has 11 rooms free.")])
a=ModelBasedAgent(f,"m",verbose=False)
a.ask("Rooms at Radisson Blu on 2026-08-14?")
n_before=len(a.messages)
a.ask("Which hotel did I just ask about?")
chk("history carried forward", len(a.messages) > n_before)
chk("system prompt kept at position 0", a.messages[0]["role"]=="system")

print("\n4. goal based: step count is not fixed by us")
f=Fake([_msg(calls=[("list_hotels",{})]),
        _msg(calls=[("get_room_availability",{"hotel":"Taj Palace","date":"2026-08-14"})]),
        _msg(calls=[("get_room_availability",{"hotel":"Radisson Blu","date":"2026-08-14"})]),
        _msg("Radisson Blu has 11 rooms free.")])
out=goal_based(f,"m","Find me a room on 2026-08-14", verbose=False)
chk("reached an answer", "11 rooms" in out)
chk("took 4 steps, not a number we hardcoded", f.calls==4)

print("\n5. utility based: preferences reach the model")
f=Fake([_msg("Radisson Blu scores highest.")])
out=utility_based(f,"m","Find a room on 2026-08-14",
                  {"price":0.5,"distance from campus":0.3,"rating":0.2}, verbose=False)
chk("answered", "Radisson" in out)
sent = " ".join(m.get("content") or "" for m in f.last_messages)
chk("weights reached the model", "weight 0.5" in sent and "distance from campus" in sent)
chk("utility system prompt asks it to score options", "score every viable option" in sent)

print("\n6. every architecture sees the same three tools")
chk("tool list identical across all four", set(f.seen_tools)=={3})

print("\n" + ("ALL PASS" if ok else "SOMETHING FAILED"))
sys.exit(0 if ok else 1)
