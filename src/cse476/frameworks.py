"""
The same agent, three ways: by hand, on Agent Framework, on Semantic Kernel.

Unit 3 Lecture 1. For two units you built everything by hand, so you understand
every piece. Now we meet the real frameworks the industry uses, and the point of
this module is that they are not magic: every framework concept maps onto
something you already wrote yourself.

The frameworks named in the syllabus, Semantic Kernel and AutoGen, merged into
Microsoft Agent Framework 1.0 in April 2026. So we learn the lineage and build
on the successor, which is what you would use in a job today.

    describe_landscape   the honest 2026 map, as a data structure you can read
    hand_rolled_agent    the Unit 1 pattern, one more time, for comparison
    framework_agent      the SAME behaviour, on Microsoft Agent Framework
    kernel_agent         the SAME behaviour, on Semantic Kernel

The framework functions are async and need a configured lane to actually run.
describe_landscape and the mapping table need nothing and are always testable.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ---------------------------------------------------------------- the landscape

@dataclass(frozen=True)
class Framework:
    """One option on the 2026 agent-framework map, with the facts that matter."""

    name: str
    status: str            # current | maintenance | community fork
    lineage: str
    when_to_use: str


def describe_landscape() -> list[Framework]:
    """
    The honest state of the world in 2026, as facts you can assert on.

    An interviewer does not want to hear that you know one framework. They want
    to hear that you understand the landscape and can justify a choice. This is
    that landscape, and every claim in it is checkable.
    """
    return [
        Framework(
            name="Microsoft Agent Framework",
            status="current",
            lineage="the merger of Semantic Kernel and AutoGen, shipped 1.0 in April 2026",
            when_to_use="new production builds in the Microsoft and Azure ecosystem",
        ),
        Framework(
            name="Semantic Kernel",
            status="maintenance",
            lineage="survives as the foundation layer inside Agent Framework",
            when_to_use="existing SK code; its kernel and plugin ideas are still current",
        ),
        Framework(
            name="AutoGen",
            status="maintenance",
            lineage="its multi-agent ideas were rebuilt graph-based inside Agent Framework",
            when_to_use="learning multi-agent concepts; not for new production",
        ),
        Framework(
            name="AG2",
            status="community fork",
            lineage="the open-source continuation of AutoGen under Apache 2.0",
            when_to_use="you want an open, interoperable stack outside Microsoft's",
        ),
        Framework(
            name="LangGraph",
            status="current",
            lineage="LangChain's graph-based agent runtime, a separate lineage",
            when_to_use="you are already in the LangChain ecosystem",
        ),
        Framework(
            name="CrewAI",
            status="current",
            lineage="a role-based multi-agent framework, a separate lineage",
            when_to_use="quick role-based crews; less control than the graph frameworks",
        ),
    ]


def framework_by_status(status: str) -> list[str]:
    """Which frameworks are in a given state. Useful for the notebook."""
    return [f.name for f in describe_landscape() if f.status == status]


# The mapping every student should be able to recite: framework word on the
# left, the thing you already built on the right. This is the antidote to
# framework-as-magic.
CONCEPT_MAP: dict[str, str] = {
    "ChatClient": "your get_client from lanes.py, one call to a model",
    "Agent / ChatAgent": "your tiny_agent: instructions, tools, and a loop",
    "instructions": "the system prompt you have written since Lecture 3",
    "tools / functions": "your REGISTRY and TOOL_SCHEMA from Unit 1",
    "AgentThread / session": "your Session from Unit 2 Lecture 5",
    "WorkflowBuilder": "your Pipeline from Unit 2 Lecture 4, as a graph",
    "middleware": "the defended call_tool wrapper from Unit 2 Lecture 2",
}


# ---------------------------------------------------------------- by hand

def hand_rolled_agent_shape() -> dict[str, str]:
    """
    A description of the Unit 1 pattern, not a live call, so it is testable
    offline. The real thing lives in tiny_agent.py; here we just name its parts
    so the notebook can line them up against the framework version.
    """
    return {
        "client": "get_client() from lanes.py",
        "instructions": "a system prompt string",
        "tools": "REGISTRY dict plus TOOL_SCHEMA list",
        "loop": "for step in range(max_steps): ...",
        "lines_of_code": "about forty, all yours, nothing hidden",
    }


# ---------------------------------------------------------------- Agent Framework

async def framework_agent(prompt: str) -> str:
    """
    The same 'answer a question' agent, on Microsoft Agent Framework.

    This is real, current API (agent-framework 1.x). It needs a configured lane,
    because it makes a live model call. The construction is deliberately tiny:
    a chat client, turned into an agent with instructions, then run. Notice how
    little there is, and that every piece has a hand-built twin.
    """
    from agent_framework.openai import OpenAIChatClient

    from cse476.lanes import get_connection

    # WHY these come from the lane system: the framework's client is the
    # industrial version of get_client. Same model, same key, same base url,
    # whichever lane is active. Nothing new to configure, and no provider named.
    base_url, api_key, model = get_connection()
    client = OpenAIChatClient(model=model, api_key=api_key, base_url=base_url)

    # as_agent is the framework's tiny_agent: instructions in, an agent out.
    agent = client.as_agent(
        instructions="You are a concise assistant. Answer in one sentence.",
    )

    result = await agent.run(prompt)
    return str(result)


# ---------------------------------------------------------------- Semantic Kernel

async def kernel_agent(prompt: str) -> str:
    """
    The same agent again, on Semantic Kernel, the lineage layer.

    Worth building once because SK survives as the foundation of Agent Framework,
    so its Kernel and connector concepts are not dead knowledge. The shape is the
    same story: a connection to a model, an instruction, a run.
    """
    from semantic_kernel.agents import ChatCompletionAgent
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

    from cse476.lanes import get_connection

    _base_url, api_key, model = get_connection()
    service = OpenAIChatCompletion(
        ai_model_id=model,
        api_key=api_key,
        # SK's OpenAI connector accepts a custom base url via async_client, but
        # for the lecture we keep the shape visible and let the notebook wire the
        # exact client. The teaching point is the structure, not this one arg.
    )
    agent = ChatCompletionAgent(
        service=service,
        name="assistant",
        instructions="You are a concise assistant. Answer in one sentence.",
    )
    response = await agent.get_response(messages=prompt)
    return str(response)


# ---------------------------------------------------------------- the trap

@dataclass
class ImportTrap:
    """
    The 'pip show autogen' problem, as a checkable fact.

    Several packages share confusingly similar names. Installing the wrong one
    is the single most common reason a beginner's imports fail against the docs.
    Knowing this is an interview-worthy detail.
    """

    symptom: str = "imports fail or do not match the documentation"
    first_check: str = "run: pip show agent-framework"
    the_confusion: tuple = field(default_factory=lambda: (
        "agent-framework  is the current Microsoft package",
        "autogen  is the old, maintenance-mode name",
        "ag2  is the community fork of the old AutoGen",
        "pyautogen  is yet another historical name on PyPI",
    ))
