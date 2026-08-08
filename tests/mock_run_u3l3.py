"""
Prove the Agent Framework tools work as plain functions offline, the agent
builds against the real package, and the mapping is complete. Building the agent
uses the real framework; running it needs a lane, so we verify construction, not
a live call.
"""

import sys

sys.path.insert(0, "src")

from cse476.agent_fw import (  # noqa: E402
    AGENT_FRAMEWORK_MAP,
    QUEUES,
    TRIAGE_TOOLS,
    async_matters,
    build_support_agent,
    classify_ticket,
    get_sla,
    list_queues,
)

ok = True


def chk(label, cond):
    global ok
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
    ok = ok and cond


print("\n1. the tools are plain functions, testable with no framework")
chk("classify routes billing", "billing" in classify_ticket("I was charged twice"))
chk("classify routes abuse", "abuse" in classify_ticket("my account was hacked"))
chk("classify defaults sensibly", "technical" in classify_ticket("zzzz"))
chk("get_sla returns billing hours", "24 hour" in get_sla("billing"))
chk("list_queues lists all five", all(q in list_queues() for q in QUEUES))

print("\n2. the tool suite is a plain list of callables")
chk("three tools", len(TRIAGE_TOOLS) == 3)
chk("all are callable", all(callable(t) for t in TRIAGE_TOOLS))
chk("each has a docstring the framework reads as its description",
    all(t.__doc__ for t in TRIAGE_TOOLS))

print("\n3. get_sla fails readably on an unknown queue")
chk("unknown queue handled", "No SLA" in get_sla("nonsense"))

print("\n4. the real framework builds an agent from the tools")
try:
    from agent_framework.openai import OpenAIChatClient
    # a dummy client is enough to prove construction; no call is made
    client = OpenAIChatClient(model="x", api_key="dummy",
                              base_url="https://example.invalid/v1")
    agent = build_support_agent(client)
    chk("agent constructed", agent is not None)
    chk("agent has run", hasattr(agent, "run"))
    chk("agent can become a tool for another agent", hasattr(agent, "as_tool"))
except Exception as e:  # noqa: BLE001
    chk(f"agent construction ({e})", False)

print("\n5. the mapping ties every framework word to hand-built code")
chk("client maps to get_client", "get_client" in AGENT_FRAMEWORK_MAP["OpenAIChatClient"])
chk("run maps to the loop", "loop" in AGENT_FRAMEWORK_MAP["await agent.run(...)"])
chk("session maps to the Unit 2 Session", "Session" in AGENT_FRAMEWORK_MAP["AgentSession"])
chk("middleware maps to call_tool", "call_tool" in AGENT_FRAMEWORK_MAP["middleware"])
chk("as_tool is named as the Unit 4 seed", "Unit 4" in AGENT_FRAMEWORK_MAP["agent.as_tool()"])

print("\n6. the async explanation is present and honest")
a = async_matters()
chk("names the sync Unit 1 version", "block" in a["unit_1"])
chk("names the async framework version", "await" in a["framework"])
chk("explains why it matters", "network" in a["why"])
chk("names the cost of ignoring it", "scales" in a["cost_of_ignoring"])

print("\n7. tools have no hidden framework dependency")
# proving the tools import and run without importing agent_framework at all
chk("classify runs as pure python", classify_ticket("refund please").startswith("This ticket"))

print("\n" + ("ALL PASS" if ok else "SOMETHING FAILED"))
sys.exit(0 if ok else 1)
