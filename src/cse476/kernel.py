"""
Semantic Kernel, the foundation layer, for real.

Unit 3 Lecture 2. Semantic Kernel survived the 2026 merger as the base of
Microsoft Agent Framework, so its three core ideas, the kernel, plugins, and
connectors, are not dead knowledge. They are the foundation of the thing you
build on. This module uses the real semantic-kernel package.

The good news for learning: a Semantic Kernel plugin is just a class with
decorated methods, and you can register and invoke those methods WITHOUT a
model. So the plugin mechanics are fully testable offline. Only the parts that
ask a model to choose a function need a lane.

    WeatherPlugin       a real SK plugin: methods decorated as kernel functions
    TicketPlugin        a second plugin, so we can show plugin composition
    build_kernel        a real Kernel with plugins registered
    invoke_directly     call a plugin function with no model in the loop

Every framework concept here has a hand-built twin from Units 1 and 2, named in
the comments, because the whole point of this course is that frameworks are
packaging, not magic.
"""

from __future__ import annotations

from typing import Annotated

from semantic_kernel import Kernel
from semantic_kernel.functions import KernelArguments, kernel_function


# ---------------------------------------------------------------- a real plugin

# WHY a class with decorated methods: this is Semantic Kernel's plugin model,
# and it is the direct descendant of your REGISTRY plus TOOL_SCHEMA from Unit 1.
# The @kernel_function decorator is what your hand-written schema dict was doing:
# giving the model a name, a description, and typed parameters to route on. The
# difference is the framework generates the schema from your type hints and
# docstrings, so you stop maintaining two things that can drift apart.
class WeatherPlugin:
    """Current weather for a few cities. A real Semantic Kernel plugin."""

    _DATA = {
        "mumbai": "Mumbai: 31C, humid, light rain.",
        "delhi": "Delhi: 38C, hazy, dry.",
        "jammu": "Jammu: 29C, clear.",
    }

    @kernel_function(
        name="get_weather",
        description="Get the current weather for one city as a short summary.",
    )
    def get_weather(
        self,
        city: Annotated[str, "The city name, for example 'Mumbai'."],
    ) -> str:
        key = city.strip().lower()
        if key not in self._DATA:
            return f"No weather on file for '{city}'. Known: {', '.join(self._DATA)}."
        return self._DATA[key]

    @kernel_function(
        name="list_cities",
        description="List the cities weather is available for. Takes no arguments.",
    )
    def list_cities(self) -> str:
        return "Cities: " + ", ".join(self._DATA)


class TicketPlugin:
    """A second plugin, so we can show two plugins on one kernel."""

    _SLA = {"billing": 24, "technical": 4, "account": 12, "sales": 48, "abuse": 1}

    @kernel_function(
        name="get_sla_hours",
        description="Get the service level agreement, in hours, for a support queue.",
    )
    def get_sla_hours(
        self,
        queue: Annotated[str, "The queue name, for example 'billing'."],
    ) -> str:
        hours = self._SLA.get(queue.strip().lower())
        if hours is None:
            return f"No SLA on file for queue '{queue}'."
        return f"The {queue} queue has a {hours} hour SLA."


# ---------------------------------------------------------------- the kernel

def build_kernel() -> Kernel:
    """
    A real Semantic Kernel with two plugins registered.

    The Kernel is the framework's central object: it holds your plugins (tools),
    and later your model connectors (your lanes). It is the industrial version
    of the little dispatch loop you wrote by hand, where a name gets looked up
    and the matching function is called. Here the kernel owns that lookup.
    """
    kernel = Kernel()
    kernel.add_plugin(WeatherPlugin(), plugin_name="weather")
    kernel.add_plugin(TicketPlugin(), plugin_name="tickets")
    return kernel


def list_registered_functions(kernel: Kernel) -> list[str]:
    """Every function the kernel knows about, as 'plugin.function' names."""
    names = []
    for meta in kernel.get_full_list_of_function_metadata():
        names.append(f"{meta.plugin_name}.{meta.name}")
    return sorted(names)


# ---------------------------------------------------------------- invoke, no model

async def invoke_directly(kernel: Kernel, plugin: str, function: str, **args) -> str:
    """
    Call a plugin function directly, with no model deciding anything.

    This is the part beginners miss: you do not need a model to run a plugin
    function. The model's only job is to CHOOSE which function to call. The
    calling itself is ordinary code the kernel dispatches. So the whole plugin
    layer, the part you actually write, is testable without spending a token.
    """
    fn = kernel.get_function(plugin, function)
    result = await kernel.invoke(fn, KernelArguments(**args))
    return str(result)


def function_metadata(kernel: Kernel, plugin: str, function: str) -> dict:
    """
    The schema the framework generated from your type hints and docstrings.

    Compare this to the TOOL_SCHEMA dict you wrote by hand in Unit 1. Same
    information, name, description, typed parameters, but you never wrote it.
    The decorator and your annotations produced it. That is the plugin model
    earning its keep: one source of truth instead of a schema and a function
    that can drift apart.
    """
    fn = kernel.get_function(plugin, function)
    return {
        "name": fn.name,
        "description": fn.description,
        "parameters": [
            {"name": p.name, "description": p.description}
            for p in fn.parameters
        ],
    }
