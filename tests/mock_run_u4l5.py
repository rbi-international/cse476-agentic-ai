"""
Prove the full composed system works end to end: route to a team, fan out the
parallel checks onto a shared blackboard, fan in, and decide. Every Unit 4
primitive in one workflow, offline, deterministic, no tokens.
"""

import asyncio
import sys

sys.path.insert(0, "src")

from cse476.triage_system import (  # noqa: E402
    SYSTEM_MAP,
    build_triage_system,
    run_triage_system,
    what_you_can_build_now,
)

ok = True


def chk(label, cond):
    global ok
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
    ok = ok and cond


def run(coro):
    return asyncio.run(coro)


print("\n1. the full system builds")
wf = build_triage_system()
chk("workflow exists", wf is not None)
chk("it has a run method", hasattr(wf, "run"))

print("\n2. routing works: a billing ticket reaches the billing team")
out = run(run_triage_system("I was charged twice, need a refund"))
chk("routed to billing", "team: billing" in out)
chk("not to technical", "team: technical" not in out)

print("\n3. routing works: a technical ticket reaches the technical team")
out = run(run_triage_system("the app crashes with an error"))
chk("routed to technical", "team: technical" in out)

print("\n4. the default team catches unmatched tickets")
out = run(run_triage_system("just saying hello"))
chk("routed to general", "team: general" in out)

print("\n5. the parallel checks both ran and posted to the board")
out = run(run_triage_system("small question about my invoice"))
chk("security check posted", "security:" in out)
chk("priority check posted", "priority:" in out)

print("\n6. the blackboard accumulated ALL findings (team + both checks)")
out = run(run_triage_system("I was charged and it is urgent"))
chk("team finding on the board", "team: billing" in out)
chk("security finding on the board", "security:" in out)
chk("priority finding on the board", "priority:" in out)
chk("three findings, none lost to overwrite", out.count(":") >= 4)  # Ticket:, team:, security:, priority:, Decision:

print("\n7. the decision reads the whole board")
# a hacked, urgent ticket must ESCALATE
out = run(run_triage_system("someone hacked my account, this is urgent"))
chk("security flagged a risk", "security: RISK" in out)
chk("priority flagged high", "priority: HIGH" in out)
chk("the decision escalates", "ESCALATE" in out)

print("\n8. a calm ticket queues normally")
out = run(run_triage_system("a small question about my plan"))
chk("no risk", "security: ok" in out)
chk("normal priority", "priority: normal" in out)
chk("queues normally, does not escalate", "queue normally" in out and "ESCALATE" not in out)

print("\n9. the whole system is deterministic")
a = run(run_triage_system("refund, urgent, hacked"))
b = run(run_triage_system("refund, urgent, hacked"))
chk("same ticket, same disposition, every time", a == b)

print("\n10. the mapping shows every primitive is present")
chk("routing is L2", "L2" in list(SYSTEM_MAP)[0])
chk("fan-out is L1", "L1" in list(SYSTEM_MAP)[1])
chk("blackboard is L4", "L4" in list(SYSTEM_MAP)[2])
chk("the decision is the manager idea from L3",
    any("L3" in k for k in SYSTEM_MAP))

print("\n11. the closing capability summary is present")
cap = what_you_can_build_now()
chk("decompose", "specialists" in cap["decompose"])
chk("route", "owns it" in cap["route"])
chk("parallelise", "wait for all" in cap["parallelise"])
chk("share", "board" in cap["share"])
chk("decide", "assembled evidence" in cap["decide"])

print("\n" + ("ALL PASS" if ok else "SOMETHING FAILED"))
sys.exit(0 if ok else 1)
