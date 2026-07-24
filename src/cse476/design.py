"""
Design review, as code.

Unit 1 Lecture 5. Design principles are easy to nod along to and easy to
forget at 1am, so this module turns the checkable ones into a linter you can
run against your own agent.

    audit_tools     static review of a tool schema and its registry
    audit_guards    is anything actually bounding this loop
    AgentSpec       the decisions you should make before writing code

Nothing here calls a model. It is all static analysis, so it costs nothing and
runs in CI.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any, Callable

# ---------------------------------------------------------------- findings

SEVERITY_ORDER = {"error": 0, "warning": 1, "note": 2}


@dataclass(frozen=True)
class Finding:
    severity: str   # error | warning | note
    where: str      # which tool, or "-" for whole agent
    message: str
    fix: str

    def __str__(self) -> str:
        return f"[{self.severity:<7}] {self.where:<26} {self.message}\n{'':>38}fix: {self.fix}"


def _sorted(findings: list[Finding]) -> list[Finding]:
    return sorted(findings, key=lambda f: (SEVERITY_ORDER[f.severity], f.where))


# ---------------------------------------------------------------- tool audit

# WHY these words: a tool name containing a conjunction or a vague verb is the
# clearest static signal of a tool doing more than one job. The model then has
# to guess when it applies, and it will guess wrong at the worst moment.
MULTI_JOB_WORDS = {"and", "handle", "process", "manage", "do", "perform", "execute"}

MIN_DESCRIPTION_CHARS = 40
MIN_PARAM_DESCRIPTION_CHARS = 8


def audit_tools(
    schema: list[dict[str, Any]],
    registry: dict[str, Callable[..., Any]],
) -> list[Finding]:
    """
    Review a tool schema against the functions it claims to describe.

    Catches the faults that are visible without running anything: the two lists
    drifting apart, descriptions too thin for the model to route on, tools doing
    more than one job, and return types that will surprise you.
    """
    findings: list[Finding] = []
    schema_names: list[str] = []

    for entry in schema:
        fn = entry.get("function", {})
        name = fn.get("name", "<unnamed>")
        schema_names.append(name)

        if not fn.get("name"):
            findings.append(Finding(
                "error", "<unnamed>", "Schema entry has no function name.",
                "Add a name that matches a key in your registry."))

        # description quality
        desc = (fn.get("description") or "").strip()
        if not desc:
            findings.append(Finding(
                "error", name, "No description at all.",
                "The description is the only thing the model routes on. Write one."))
        elif len(desc) < MIN_DESCRIPTION_CHARS:
            findings.append(Finding(
                "warning", name,
                f"Description is only {len(desc)} characters.",
                "Say what it returns AND when to use it instead of a sibling tool."))

        # one tool, one job
        parts = {w for w in name.lower().replace("-", "_").split("_") if w}
        offenders = parts & MULTI_JOB_WORDS
        if offenders:
            findings.append(Finding(
                "warning", name,
                f"Name contains {sorted(offenders)}, which suggests more than one job.",
                "Split it. A tool that does two things gets called at the wrong moment."))

        # parameters
        params = fn.get("parameters") or {}
        props = params.get("properties") or {}
        required = params.get("required") or []

        for pname, pspec in props.items():
            if not (pspec.get("description") or "").strip():
                findings.append(Finding(
                    "warning", f"{name}.{pname}",
                    "Parameter has no description.",
                    "State the exact format expected, for example YYYY-MM-DD."))
            elif len(pspec["description"].strip()) < MIN_PARAM_DESCRIPTION_CHARS:
                findings.append(Finding(
                    "note", f"{name}.{pname}",
                    "Parameter description is very short.",
                    "Ambiguous formats are the most common cause of a bad tool call."))
            if not pspec.get("type"):
                findings.append(Finding(
                    "error", f"{name}.{pname}", "Parameter has no type.",
                    "Add a JSON schema type so the model knows what to send."))

        if props and not required:
            findings.append(Finding(
                "note", name, "No parameters are marked required.",
                "If a parameter is mandatory, say so, or expect calls without it."))

        for r in required:
            if r not in props:
                findings.append(Finding(
                    "error", name, f"Required parameter '{r}' is not in properties.",
                    "Remove it from required or define it in properties."))

        # schema and registry must stay in step
        func = registry.get(name)
        if func is None:
            findings.append(Finding(
                "error", name, "In the schema but not in the registry.",
                "The model will request it and your loop will refuse. Add or remove it."))
            continue

        # signature agreement
        try:
            sig = inspect.signature(func)
        except (TypeError, ValueError):
            sig = None

        if sig is not None:
            real = set(sig.parameters)
            declared = set(props)
            for missing in sorted(declared - real):
                findings.append(Finding(
                    "error", name,
                    f"Schema declares '{missing}' but the function does not accept it.",
                    "A call with that argument raises TypeError inside your loop."))
            for undeclared in sorted(real - declared):
                p = sig.parameters[undeclared]
                if p.default is inspect.Parameter.empty:
                    findings.append(Finding(
                        "error", name,
                        f"Function requires '{undeclared}' but the schema never mentions it.",
                        "The model cannot supply what it was not told about."))

            # WHY the name comparison: `from __future__ import annotations`
            # makes every annotation a string, so `ret is str` is False even
            # when the function is annotated `-> str`. Comparing names handles
            # both the real type and the postponed string form.
            ret = sig.return_annotation
            ret_name = getattr(ret, "__name__", ret)
            if ret is not inspect.Signature.empty and ret_name != "str":
                findings.append(Finding(
                    "note", name,
                    f"Returns {ret_name} rather than str.",
                    "Results go back to the model as text. Returning a readable "
                    "string saves a serialisation step and makes traces legible."))

        if not (inspect.getdoc(func) or "").strip():
            findings.append(Finding(
                "note", name, "Function has no docstring.",
                "Future you will not remember why this tool exists."))

    for name in registry:
        if name not in schema_names:
            findings.append(Finding(
                "warning", name, "In the registry but not in the schema.",
                "The model cannot see it, so it will never be used. Dead code."))

    return _sorted(findings)


# ---------------------------------------------------------------- guard audit

def audit_guards(
    max_steps: int | None = None,
    has_whitelist: bool = False,
    has_no_progress_check: bool = False,
    max_tokens: int | None = None,
    trims_transcript: bool = False,
) -> list[Finding]:
    """
    Is anything actually bounding this loop?

    Deliberately blunt. Every one of these has already cost somebody in this
    course either money or a wrong answer, in a live class.
    """
    findings: list[Finding] = []

    if not max_steps:
        findings.append(Finding(
            "error", "loop", "No step budget.",
            "One `for step in range(max_steps)` is the difference between a "
            "bounded failure and an invoice."))
    elif max_steps > 20:
        findings.append(Finding(
            "warning", "loop", f"Step budget of {max_steps} is high.",
            "Can you justify the worst case cost of 20+ model calls per request?"))

    if not has_whitelist:
        findings.append(Finding(
            "error", "tools", "No registry check before dispatch.",
            "A model that invents a tool name will raise KeyError, which in a "
            "service is a 500 caused by a model saying a word."))

    if not has_no_progress_check:
        findings.append(Finding(
            "warning", "loop", "No no progress detection.",
            "The step budget catches runaway loops at full price. Thrashing "
            "should be caught earlier and more cheaply."))

    if not trims_transcript and not max_tokens:
        findings.append(Finding(
            "warning", "transcript", "Nothing bounds transcript growth.",
            "Cost grows with the square of conversation length. Add a token "
            "budget, a sliding window, or both."))

    return _sorted(findings)


# ---------------------------------------------------------------- the spec

@dataclass
class AgentSpec:
    """
    The decisions worth making before you write any code.

    Every blank field here is a decision you are going to make anyway, later,
    accidentally, in the middle of debugging something else.
    """

    name: str = ""
    performance_measure: str = ""     # P
    environment: str = ""             # E
    actuators: str = ""               # A
    sensors: str = ""                 # S
    shape: str = ""                   # workflow | router | agent
    strategy: str = ""                # react | plan_then_execute | none
    rung: str = ""                    # reflex | model_based | goal_based | utility_based
    what_it_refuses: list[str] = field(default_factory=list)
    pinned_facts: list[str] = field(default_factory=list)
    failure_behaviour: str = ""
    max_steps: int | None = None

    def review(self) -> list[Finding]:
        findings: list[Finding] = []

        required_text = {
            "performance_measure": "You cannot tell whether it works without this.",
            "environment": "This is also your security boundary. Name it.",
            "actuators": "The tool list. Anything not here, it cannot do.",
            "sensors": "Tool results plus the conversation, and nothing else.",
            "shape": "workflow, router or agent. Choosing agent by default is waste.",
            "failure_behaviour": "What it says when it cannot answer. Skip this and "
                                 "it will invent something fluent instead.",
        }
        for fname, why in required_text.items():
            if not str(getattr(self, fname)).strip():
                findings.append(Finding("error", fname, "Not decided.", why))

        if self.shape == "agent" and not self.strategy:
            findings.append(Finding(
                "warning", "strategy", "Shape is 'agent' but no strategy chosen.",
                "react or plan_then_execute. See the Lecture 4 decision table."))

        if self.shape in {"workflow", "router"} and self.strategy:
            findings.append(Finding(
                "note", "strategy", f"Shape is '{self.shape}' but a strategy is set.",
                "Workflows and routers do not need a reasoning strategy. "
                "Simpler is cheaper and easier to test."))

        if not self.what_it_refuses:
            findings.append(Finding(
                "warning", "what_it_refuses", "Nothing listed.",
                "An agent with no declared refusals will attempt everything, "
                "including things it should decline."))

        if not self.pinned_facts:
            findings.append(Finding(
                "note", "pinned_facts", "Nothing pinned.",
                "Which facts, if silently lost to trimming, would produce a "
                "confidently wrong answer? Those are the pins."))

        if self.max_steps is None:
            findings.append(Finding(
                "error", "max_steps", "No step budget decided.",
                "Pick a number and be able to defend it."))

        return _sorted(findings)

    def is_ready(self) -> bool:
        return not any(f.severity == "error" for f in self.review())


# ---------------------------------------------------------------- reporting

def report(findings: list[Finding], title: str = "audit") -> str:
    """Human readable summary. Print this, do not just count it."""
    counts = {s: sum(1 for f in findings if f.severity == s)
              for s in ("error", "warning", "note")}
    head = (
        f"{title}: {counts['error']} error(s), "
        f"{counts['warning']} warning(s), {counts['note']} note(s)"
    )
    if not findings:
        return head + "\n  nothing to report."
    return head + "\n" + "\n".join(str(f) for f in findings)
