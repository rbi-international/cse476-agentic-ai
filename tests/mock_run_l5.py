"""
Prove the design linter, offline. No model calls at all.

Scenario 7 is the one that matters: the linter must stay quiet on the code we
actually teach. A linter that complains about correct work gets switched off.
"""

import sys

sys.path.insert(0, "src")

from cse476.architectures import REGISTRY, TOOL_SCHEMA  # noqa: E402
from cse476.tiny_agent import REGISTRY as TINY_REGISTRY  # noqa: E402
from cse476.tiny_agent import TOOL_SCHEMA as TINY_SCHEMA  # noqa: E402
from cse476.design import (  # noqa: E402
    AgentSpec,
    audit_guards,
    audit_tools,
    report,
)

ok = True


def chk(label, cond):
    global ok
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
    ok = ok and cond


def msgs(findings, severity=None):
    # WHY message and fix together: a finding is both halves. Asserting on only
    # one of them is how you write a test that passes for the wrong reason.
    return " ".join(
        f"{f.message} {f.fix}"
        for f in findings
        if severity is None or f.severity == severity
    )


print("\n1. schema and registry drifting apart")
bad_schema = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a city, in degrees celsius.",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string", "description": "City name."}},
            "required": ["city"],
        },
    },
}]
found = audit_tools(bad_schema, {})
chk("schema entry with no function is an error",
    any(f.severity == "error" and "not in the registry" in f.message for f in found))

found = audit_tools([], {"orphan": lambda: "x"})
chk("registry entry with no schema is a warning",
    any(f.severity == "warning" and "not in the schema" in f.message for f in found))


print("\n2. thin descriptions")
thin = [{
    "type": "function",
    "function": {
        "name": "lookup",
        "description": "Looks things up.",
        "parameters": {"type": "object",
                       "properties": {"q": {"type": "string", "description": "query"}},
                       "required": ["q"]},
    },
}]
found = audit_tools(thin, {"lookup": lambda q: "x"})
chk("short tool description is flagged", "only" in msgs(found, "warning"))

nodesc = [{"type": "function", "function": {"name": "lookup", "parameters": {}}}]
found = audit_tools(nodesc, {"lookup": lambda: "x"})
chk("missing description is an error", "No description at all." in msgs(found, "error"))


print("\n3. one tool, one job")
god = [{
    "type": "function",
    "function": {
        "name": "check_and_book_room",
        "description": "Checks availability and books the room and sends confirmation.",
        "parameters": {"type": "object",
                       "properties": {"hotel": {"type": "string", "description": "Hotel name."}},
                       "required": ["hotel"]},
    },
}]
found = audit_tools(god, {"check_and_book_room": lambda hotel: "x"})
chk("conjunction in the name is flagged", "more than one job" in msgs(found, "warning"))


print("\n4. signature disagreement is caught before runtime")
mismatch = [{
    "type": "function",
    "function": {
        "name": "get_rate",
        "description": "Get the nightly rate in rupees for a named hotel on a date.",
        "parameters": {
            "type": "object",
            "properties": {
                "hotel": {"type": "string", "description": "Exact hotel name."},
                "currency": {"type": "string", "description": "Currency code."},
            },
            "required": ["hotel"],
        },
    },
}]


def get_rate(hotel: str, date: str) -> str:
    return "x"


found = audit_tools(mismatch, {"get_rate": get_rate})
chk("schema declares a parameter the function lacks",
    "does not accept it" in msgs(found, "error"))
chk("function requires a parameter the schema hides",
    "never mentions it" in msgs(found, "error"))


print("\n5. missing guards")
found = audit_guards()
chk("no step budget is an error", "No step budget." in msgs(found, "error"))
chk("no whitelist is an error", "No registry check" in msgs(found, "error"))
chk("no progress check is a warning", "no progress detection" in msgs(found, "warning"))
chk("unbounded transcript is a warning", "bounds transcript growth" in msgs(found, "warning"))

found = audit_guards(max_steps=6, has_whitelist=True,
                     has_no_progress_check=True, trims_transcript=True)
chk("a fully guarded loop is clean", found == [])

found = audit_guards(max_steps=50, has_whitelist=True,
                     has_no_progress_check=True, trims_transcript=True)
chk("an absurd budget is still flagged", "is high" in msgs(found, "warning"))


print("\n6. the spec")
empty = AgentSpec(name="untitled")
chk("an empty spec is not ready", empty.is_ready() is False)
chk("it names what is undecided", "Not decided." in msgs(empty.review(), "error"))

full = AgentSpec(
    name="hotel-assistant",
    performance_measure="Finds an available room within budget and distance preference.",
    environment="Three hotels, their rates, distances, ratings and per date availability.",
    actuators="list_hotels, get_room_availability, get_hotel_details",
    sensors="Tool results plus the conversation so far.",
    shape="agent",
    strategy="react",
    rung="utility_based",
    what_it_refuses=["Anything requiring payment", "Medical or legal advice"],
    pinned_facts=["stated budget", "stated dates"],
    failure_behaviour="Says it cannot find a match and names what it checked.",
    max_steps=6,
)
chk("a complete spec is ready", full.is_ready() is True)

odd = AgentSpec(
    name="x", performance_measure="p", environment="e", actuators="a", sensors="s",
    shape="workflow", strategy="react", failure_behaviour="f", max_steps=3,
    what_it_refuses=["nothing"], pinned_facts=["x"],
)
chk("a workflow with a reasoning strategy gets a note",
    "do not need a reasoning strategy" in msgs(odd.review(), "note"))


print("\n7. the linter must stay quiet on the code we teach")
for label, (sch, reg) in {
    "architectures.py": (TOOL_SCHEMA, REGISTRY),
    "tiny_agent.py": (TINY_SCHEMA, TINY_REGISTRY),
}.items():
    found = audit_tools(sch, reg)
    if found:
        print(report(found, label))
    chk(f"{label} is completely clean", found == [])

# WHY this one exists: the first version of the return type check compared
# against the type , which fails when 
# turns every annotation into a string. It fired "Returns str rather than str"
# on correct code, and scenario 7 missed it because it only looked at errors
# and warnings. A linter that nags about correct work gets switched off.


def annotated(hotel: str) -> str:
    """Correctly annotated tool."""
    return hotel


ann_schema = [{
    "type": "function",
    "function": {
        "name": "annotated",
        "description": "A correctly annotated tool used to check the linter itself.",
        "parameters": {"type": "object",
                       "properties": {"hotel": {"type": "string",
                                                "description": "Exact hotel name."}},
                       "required": ["hotel"]},
    },
}]
chk("no false positive on a str return annotation",
    audit_tools(ann_schema, {"annotated": annotated}) == [])


def returns_dict(hotel: str) -> dict:
    """Returns a dict, which we do want flagged."""
    return {}


dict_schema = [{**ann_schema[0]}]
dict_schema[0]["function"] = {**ann_schema[0]["function"], "name": "returns_dict"}
chk("a genuine non str return is still flagged",
    "rather than str" in msgs(audit_tools(dict_schema, {"returns_dict": returns_dict}), "note"))


print("\n8. report renders")
text = report(audit_guards(), "guards")
chk("counts appear in the header", "error(s)" in text)
chk("empty findings say so", "nothing to report" in report([], "clean"))

print("\n" + ("ALL PASS" if ok else "SOMETHING FAILED"))
sys.exit(0 if ok else 1)
