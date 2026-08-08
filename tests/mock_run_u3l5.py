"""
Prove the real Agent Framework graph runs offline and routes correctly, and that
the multi-agent mappings are complete. The manager needs a lane; the graph of
function nodes does not, so the graph is fully tested here with no model.
"""

import asyncio
import sys

sys.path.insert(0, "src")

from cse476.multi_agent import (  # noqa: E402
    GRAPH_MAP,
    build_manager,
    build_triage_graph,
    conversation_vs_graph,
    run_triage_graph,
)

ok = True


def chk(label, cond):
    global ok
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
    ok = ok and cond


def run(coro):
    return asyncio.run(coro)


print("\n1. a real Agent Framework graph builds")
graph = build_triage_graph()
chk("graph object exists", graph is not None)
chk("it has a run method", hasattr(graph, "run"))

print("\n2. the graph routes a billing ticket end to end, no model")
out = run(run_triage_graph("I was charged twice and want a refund"))
chk("reached the billing team", "billing-team" in out)
chk("attached the billing SLA", "24h" in out)
chk("priority is normal", "normal" in out)

print("\n3. the graph routes an abuse ticket and escalates")
out = run(run_triage_graph("someone hacked my account and is sending spam"))
chk("reached the abuse team", "abuse-team" in out)
chk("attached the strict SLA", "1h" in out)
chk("priority is urgent", "urgent" in out)

print("\n4. the graph handles a technical ticket")
out = run(run_triage_graph("the app crashes with an error on login"))
chk("routed somewhere valid", any(q in out for q in ("technical-team", "account-team")))

print("\n5. the graph defaults unmatched tickets safely")
out = run(run_triage_graph("hello there"))
chk("defaulted to technical", "technical-team" in out)
chk("still produced a full assignment", "SLA" in out)

print("\n6. every graph concept maps to hand-built work")
chk("node maps to a pipeline step", "step" in GRAPH_MAP["Executor / node"].lower())
chk("edge maps to pipeline order", "next" in GRAPH_MAP["Edge"].lower() or "order" in GRAPH_MAP["Edge"].lower())
chk("builder maps to the pipeline", "Pipeline" in GRAPH_MAP["WorkflowBuilder"])
chk("send_message maps to state passing", "state" in GRAPH_MAP["ctx.send_message"].lower())
chk("fan-out is named as new", "new" in GRAPH_MAP["fan-out / fan-in"].lower())

print("\n7. the conversation-to-graph shift is stated for interviews")
shift = conversation_vs_graph()
chk("names the old conversation model", "conversation" in shift["autogen_old"].lower())
chk("names the new graph model", "graph" in shift["agent_framework_new"].lower())
chk("explains why it changed", "testable" in shift["why_it_changed"].lower())
chk("is honest about the cost", "more to set up" in shift["the_cost"].lower())

print("\n8. the manager builds against the real framework")
try:
    from agent_framework.openai import OpenAIChatClient
    client = OpenAIChatClient(model="x", api_key="dummy",
                              base_url="https://example.invalid/v1")
    manager = build_manager(client)
    chk("manager constructed", manager is not None)
    chk("manager has run", hasattr(manager, "run"))
except Exception as e:  # noqa: BLE001
    chk(f"manager construction ({e})", False)

print("\n9. the same ticket gives the same route every run (deterministic graph)")
a = run(run_triage_graph("refund my invoice"))
b = run(run_triage_graph("refund my invoice"))
chk("graph is deterministic", a == b)
chk("and it is the billing route", "billing-team" in a)

print("\n" + ("ALL PASS" if ok else "SOMETHING FAILED"))
sys.exit(0 if ok else 1)
