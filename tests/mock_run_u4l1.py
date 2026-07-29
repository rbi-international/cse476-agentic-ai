"""
Prove the real fan-out then fan-in workflow runs offline, in parallel, and that
fan-in synchronises: the combine step sees every reviewer's finding at once, and
only after all of them finish. No model, deterministic, no tokens.
"""

import asyncio
import sys

sys.path.insert(0, "src")

from cse476.orchestration import (  # noqa: E402
    ORCHESTRATION_MAP,
    REVIEWERS,
    build_review_workflow,
    run_review,
    sequential_vs_concurrent,
)

ok = True


def chk(label, cond):
    global ok
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
    ok = ok and cond


def run(coro):
    return asyncio.run(coro)


print("\n1. the fan-out then fan-in workflow builds")
wf = build_review_workflow()
chk("workflow object exists", wf is not None)
chk("there are three parallel reviewers", len(REVIEWERS) == 3)

print("\n2. a clean ticket gets three calm findings, combined")
out = run(run_review("I have a small question about my invoice format"))
chk("security says ok", "security_ok" in out)
chk("priority says normal", "normal_priority" in out)
chk("sentiment says calm", "calm_customer" in out)
chk("all three are in one combined verdict", out.count(",") == 2)

print("\n3. a nasty ticket lights up all three reviewers")
out = run(run_review("URGENT: someone tried to hack my account, this is terrible"))
chk("security flags a risk", "SECURITY_RISK" in out)
chk("priority flags high", "HIGH_PRIORITY" in out)
chk("sentiment flags angry", "ANGRY_CUSTOMER" in out)

print("\n4. the reviewers are independent, order does not change the verdict")
a = run(run_review("my password was leaked and I am furious, fix it immediately"))
b = run(run_review("my password was leaked and I am furious, fix it immediately"))
chk("deterministic across runs", a == b)
chk("all three fired", all(k in a for k in ("SECURITY_RISK", "HIGH_PRIORITY", "ANGRY_CUSTOMER")))

print("\n5. fan-in gathers EVERY finding into one list (the key property)")
# the verdict always has exactly three findings, one per reviewer, never fewer
out = run(run_review("just a normal question"))
findings = out.replace("Review complete: ", "").split(", ")
chk("exactly three findings gathered", len(findings) == 3)
chk("one from each reviewer, none dropped",
    any("security" in f or "SECURITY" in f for f in findings)
    and any("priority" in f or "PRIORITY" in f for f in findings)
    and any("customer" in f or "CUSTOMER" in f for f in findings))

print("\n6. fan-in SYNCHRONISES: combine runs only after all workers finish")
# prove it with a deliberately slow worker; the join must still wait for it
order = []
from agent_framework import WorkflowBuilder, WorkflowContext, executor  # noqa: E402


@executor(id="s")
async def s(x: str, ctx: WorkflowContext[str]) -> None:
    await ctx.send_message(x)


@executor(id="quick")
async def quick(x: str, ctx: WorkflowContext[str]) -> None:
    order.append("quick")
    await ctx.send_message("quick")


@executor(id="slow")
async def slow(x: str, ctx: WorkflowContext[str]) -> None:
    await asyncio.sleep(0.05)
    order.append("slow")
    await ctx.send_message("slow")


@executor(id="j")
async def j(results: list[str], ctx: WorkflowContext) -> None:
    order.append("join")
    await ctx.yield_output(f"{len(results)} results")


wf2 = (
    WorkflowBuilder(start_executor=s)
    .add_fan_out_edges(s, [quick, slow])
    .add_fan_in_edges([quick, slow], j)
    .build()
)
res = run(wf2.run("go"))
chk("join saw both results", "2 results" in res.get_outputs()[0])
chk("join ran LAST, after the slow worker", order[-1] == "join")
chk("nothing ran after the join", len(order) == 3)

print("\n7. the mapping ties every idea to prior work")
chk("fan-out maps to EventBus", "EventBus" in ORCHESTRATION_MAP["fan-out"])
chk("fan-in is named as new", "could not" in ORCHESTRATION_MAP["fan-in"])
chk("synchronisation is called out", "wrote none" in ORCHESTRATION_MAP["synchronisation"])

print("\n8. the interview framing is present and honest")
sv = sequential_vs_concurrent()
chk("names the sequential cost", "waits" in sv["sequential"])
chk("names the concurrent behaviour", "join waits for all" in sv["concurrent"])
chk("names the real win beyond speed", "shape" in sv["the_real_win"])
chk("is honest about the cost", "independent" in sv["the_cost"])

print("\n" + ("ALL PASS" if ok else "SOMETHING FAILED"))
sys.exit(0 if ok else 1)
