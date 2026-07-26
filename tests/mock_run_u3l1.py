"""
Prove the landscape facts, the concept mapping, and that the real framework
imports resolve. The live-call agents need a lane, so they are checked for
importability here, not executed. The notebook runs them for real.
"""

import sys

sys.path.insert(0, "src")

from cse476.frameworks import (  # noqa: E402
    CONCEPT_MAP,
    Framework,
    ImportTrap,
    describe_landscape,
    framework_by_status,
    hand_rolled_agent_shape,
)

ok = True


def chk(label, cond):
    global ok
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
    ok = ok and cond


print("\n1. the landscape names the successor and the lineage")
land = describe_landscape()
names = [f.name for f in land]
chk("Microsoft Agent Framework is on the map", "Microsoft Agent Framework" in names)
chk("Semantic Kernel is on the map", "Semantic Kernel" in names)
chk("AutoGen is on the map", "AutoGen" in names)
chk("the competitors are named", "LangGraph" in names and "CrewAI" in names)
chk("the community fork is named", "AG2" in names)

print("\n2. the statuses are honest")
chk("Agent Framework is current", "Microsoft Agent Framework" in framework_by_status("current"))
chk("SK and AutoGen are maintenance", set(framework_by_status("maintenance")) == {"Semantic Kernel", "AutoGen"})
chk("every entry has a lineage and a use", all(f.lineage and f.when_to_use for f in land))

print("\n3. the merger is stated where it matters")
af = next(f for f in land if f.name == "Microsoft Agent Framework")
chk("Agent Framework lineage names the merger", "merger" in af.lineage.lower())
sk = next(f for f in land if f.name == "Semantic Kernel")
chk("SK is described as the foundation layer", "foundation" in sk.lineage.lower())

print("\n4. every framework word maps to something already built")
chk("the concept map is non-empty", len(CONCEPT_MAP) >= 6)
chk("Agent maps to tiny_agent", "tiny_agent" in CONCEPT_MAP["Agent / ChatAgent"])
chk("instructions maps to the system prompt", "system prompt" in CONCEPT_MAP["instructions"])
chk("WorkflowBuilder maps to the pipeline", "Pipeline" in CONCEPT_MAP["WorkflowBuilder"])
chk("session maps to the Unit 2 Session", "Session" in CONCEPT_MAP["AgentThread / session"])

print("\n5. the hand-rolled shape is described for comparison")
shape = hand_rolled_agent_shape()
chk("names the client", "get_client" in shape["client"])
chk("names the tools", "REGISTRY" in shape["tools"])
chk("makes the point that it is small and yours", "yours" in shape["lines_of_code"])

print("\n6. the import trap is captured")
trap = ImportTrap()
chk("first check is pip show", "pip show" in trap.first_check)
chk("names the current package", any("agent-framework" in c for c in trap.the_confusion))
chk("names the old package", any("autogen" in c.lower() for c in trap.the_confusion))
chk("names the community fork", any("ag2" in c.lower() for c in trap.the_confusion))

print("\n7. the real frameworks are installed and import")
try:
    from agent_framework.openai import OpenAIChatClient  # noqa: F401
    chk("agent-framework imports", True)
except Exception as e:  # noqa: BLE001
    chk(f"agent-framework imports ({e})", False)
try:
    from semantic_kernel.agents import ChatCompletionAgent  # noqa: F401
    chk("semantic-kernel imports", True)
except Exception as e:  # noqa: BLE001
    chk(f"semantic-kernel imports ({e})", False)

print("\n8. the live-call functions exist and are async")
import inspect  # noqa: E402
from cse476 import frameworks  # noqa: E402
chk("framework_agent is a coroutine function", inspect.iscoroutinefunction(frameworks.framework_agent))
chk("kernel_agent is a coroutine function", inspect.iscoroutinefunction(frameworks.kernel_agent))

print("\n9. Framework is a clean frozen record")
f = Framework(name="x", status="current", lineage="y", when_to_use="z")
chk("fields are set", f.name == "x" and f.status == "current")
try:
    f.name = "changed"
    chk("should be frozen", False)
except Exception:  # noqa: BLE001
    chk("frozen, cannot be mutated", True)

print("\n" + ("ALL PASS" if ok else "SOMETHING FAILED"))
sys.exit(0 if ok else 1)
