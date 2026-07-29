"""
Prove the blackboard works: agents write to and read from shared state, each
building on the findings before it, and the final agent reads the whole board.
Real ctx.set_state / ctx.get_state, offline, deterministic, no tokens.
"""

import asyncio
import sys

sys.path.insert(0, "src")

from cse476.blackboard import (  # noqa: E402
    BLACKBOARD_MAP,
    build_blackboard,
    message_vs_blackboard,
    run_blackboard,
)

ok = True


def chk(label, cond):
    global ok
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
    ok = ok and cond


def run(coro):
    return asyncio.run(coro)


print("\n1. the blackboard workflow builds")
wf = build_blackboard()
chk("workflow exists", wf is not None)
chk("it has a run method", hasattr(wf, "run"))

print("\n2. findings accumulate on the shared board")
out = run(run_blackboard("someone tried to hack my account, this is urgent"))
chk("the ticket is on the board", "hack my account" in out)
chk("the security finding is there", "security: RISK" in out)
chk("the priority finding is there too", "priority: HIGH" in out)
chk("both findings survived (append, not overwrite)",
    "security" in out and "priority" in out)

print("\n3. a clean ticket accumulates clean findings")
out = run(run_blackboard("just a small question about my invoice"))
chk("security says ok", "security: ok" in out)
chk("priority says normal", "priority: normal" in out)
chk("still two findings on the board", out.count(":") >= 3)  # Ticket:, security:, priority:

print("\n4. the final agent reads the WHOLE board, not just its message")
# summarise reads TICKET and FINDINGS from state, nothing from its incoming message
out = run(run_blackboard("password breach, system is down"))
chk("it read the original ticket from state", "password breach" in out)
chk("it read the security finding from state", "security: RISK" in out)
chk("it read the priority finding from state", "priority: HIGH" in out)

print("\n5. each agent builds on the ones before it")
# priority runs after security; the board it reads already has security's finding
# we can prove ordering by the fact both appear and the board is cumulative
out = run(run_blackboard("hacked and urgent"))
board = out.split("Board:")[1]
chk("security appears before priority on the board",
    board.index("security") < board.index("priority"))

print("\n6. the blackboard is deterministic")
a = run(run_blackboard("breach, urgent"))
b = run(run_blackboard("breach, urgent"))
chk("same ticket, same board, every time", a == b)

print("\n7. the mapping ties the pattern to the real API")
chk("set_state is posting to the board", "post" in BLACKBOARD_MAP["ctx.set_state(key, value)"])
chk("get_state is reading the board", "read" in BLACKBOARD_MAP["ctx.get_state(key)"])
chk("read-modify-write is named", "add your finding" in BLACKBOARD_MAP["read, modify, write"])
chk("agreed keys are called the contract", "contract" in BLACKBOARD_MAP["agreed key names"])
chk("append not overwrite is stressed", "survive" in BLACKBOARD_MAP["append not overwrite"])

print("\n8. the message-vs-blackboard framing is present and honest")
mb = message_vs_blackboard()
chk("names the message shape", "point to point" in mb["message"])
chk("names the blackboard shape", "shared" in mb["blackboard"])
chk("says when to use a message", "one result to the next" in mb["use_a_message"])
chk("says when to use a board", "growing picture" in mb["use_a_board"])
chk("is honest about the cost", "discipline" in mb["the_cost"] or "tangle" in mb["the_cost"])

print("\n" + ("ALL PASS" if ok else "SOMETHING FAILED"))
sys.exit(0 if ok else 1)
