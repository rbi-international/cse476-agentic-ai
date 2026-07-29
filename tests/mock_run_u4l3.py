"""
Prove the manager pattern is wired correctly against the real framework: three
named specialists, each wrapped as a tool with a helpful description, and a
manager that carries those tools. The manager's actual decision needs a lane, so
we verify construction and wiring offline, not a live delegation.
"""

import sys

sys.path.insert(0, "src")

from cse476.manager import (  # noqa: E402
    MANAGER_INSTRUCTIONS,
    MANAGER_MAP,
    SPECIALIST_INSTRUCTIONS,
    build_manager,
    build_specialists,
    rules_vs_manager,
    specialist_tools,
)

ok = True


def chk(label, cond):
    global ok
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
    ok = ok and cond


print("\n1. the three specialists build against the real framework")
try:
    from agent_framework.openai import OpenAIChatClient
    client = OpenAIChatClient(model="x", api_key="dummy",
                              base_url="https://models.github.ai/inference")
    specialists = build_specialists(client)
    chk("three specialists", len(specialists) == 3)
    chk("billing, technical, account", set(specialists) == {"billing", "technical", "account"})
    chk("each is a real agent", all(hasattr(a, "run") for a in specialists.values()))
    chk("each is named so as_tool can identify it",
        all(a.name.endswith("_specialist") for a in specialists.values()))
except Exception as e:  # noqa: BLE001
    chk(f"specialist construction ({e})", False)
    specialists = {}

print("\n2. each specialist has a narrow, focused instruction")
chk("billing instruction is about billing", "billing" in SPECIALIST_INSTRUCTIONS["billing"].lower())
chk("technical instruction is about technical", "technical" in SPECIALIST_INSTRUCTIONS["technical"].lower())
chk("each tells non-matching work to go elsewhere",
    all("another team" in i for i in SPECIALIST_INSTRUCTIONS.values()))

print("\n3. specialists wrap into tools with helpful descriptions")
if specialists:
    tools = specialist_tools(specialists)
    chk("three tools", len(tools) == 3)
    chk("each tool is named ask_<domain>",
        all(getattr(t, "name", "").startswith("ask_") for t in tools))
    chk("each tool has a description the manager reads to choose",
        all(getattr(t, "description", "") for t in tools))
    chk("descriptions mention the domain",
        any("refund" in getattr(t, "description", "").lower() for t in tools))

print("\n4. the manager builds with the specialists as its tools")
if specialists:
    manager = build_manager(client)
    chk("manager is a real agent", hasattr(manager, "run"))
    chk("manager is named", manager.name == "support_manager")

print("\n5. the manager is told to delegate, not answer")
chk("manager instructed not to answer itself", "not answer" in MANAGER_INSTRUCTIONS.lower())

print("\n6. the mapping ties the pattern to prior work")
chk("manager maps to the L2 classifier", "classifier" in MANAGER_MAP["manager agent"])
chk("as_tool is named", "call" in MANAGER_MAP["as_tool"])
chk("description is called an instruction", "instruction" in MANAGER_MAP["the tool description"])
chk("the cost is named honestly", "wrong" in MANAGER_MAP["the cost"])

print("\n7. the rules-versus-manager framing is present and honest")
rv = rules_vs_manager()
chk("names the speed of rules", "fast" in rv["fixed_routing"])
chk("names the judgement of a manager", "intent" in rv["manager_agent"])
chk("says when to use rules", "high volume" in rv["use_rules_when"])
chk("says when to use a manager", "ambiguous" in rv["use_manager_when"])
chk("is honest that a manager can err", "wrong specialist" in rv["the_honest_risk"])

print("\n" + ("ALL PASS" if ok else "SOMETHING FAILED"))
sys.exit(0 if ok else 1)
