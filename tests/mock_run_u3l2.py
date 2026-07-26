"""
Prove the real Semantic Kernel plugin layer works, offline. The kernel and its
plugins are real; function invocation needs no model, so all of this runs
without a lane or a token.
"""

import asyncio
import sys

sys.path.insert(0, "src")

from cse476.kernel import (  # noqa: E402
    TicketPlugin,
    WeatherPlugin,
    build_kernel,
    function_metadata,
    invoke_directly,
    list_registered_functions,
)

ok = True


def chk(label, cond):
    global ok
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
    ok = ok and cond


def run(coro):
    return asyncio.run(coro)


print("\n1. a real kernel is built with real plugins")
kernel = build_kernel()
chk("kernel exists", kernel is not None)
names = list_registered_functions(kernel)
chk("weather.get_weather is registered", "weather.get_weather" in names)
chk("weather.list_cities is registered", "weather.list_cities" in names)
chk("tickets.get_sla_hours is registered", "tickets.get_sla_hours" in names)
chk("two plugins, three functions total", len(names) == 3)

print("\n2. a plugin function runs with no model at all")
out = run(invoke_directly(kernel, "weather", "get_weather", city="Mumbai"))
chk("returned the real data", "Mumbai" in out and "31C" in out)

print("\n3. the second plugin works too")
out = run(invoke_directly(kernel, "tickets", "get_sla_hours", queue="billing"))
chk("billing SLA is 24 hours", "24 hour" in out)

print("\n4. a no-argument function works")
out = run(invoke_directly(kernel, "weather", "list_cities"))
chk("lists the cities", "mumbai" in out and "delhi" in out)

print("\n5. an unknown city is handled inside the function")
out = run(invoke_directly(kernel, "weather", "get_weather", city="Paris"))
chk("says no data", "No weather" in out)
chk("suggests the known cities", "mumbai" in out)

print("\n6. the framework generated the schema from your annotations")
meta = function_metadata(kernel, "weather", "get_weather")
chk("name came through", meta["name"] == "get_weather")
chk("description came through", "weather" in meta["description"].lower())
chk("the typed parameter was captured", meta["parameters"][0]["name"] == "city")
chk("the parameter description came from the annotation",
    "city name" in meta["parameters"][0]["description"].lower())

print("\n7. the plugin is just a class, testable on its own")
# no kernel needed: a plugin method is an ordinary method
w = WeatherPlugin()
chk("the method returns data directly", "Delhi" in w.get_weather("delhi"))
t = TicketPlugin()
chk("the ticket method too", "4 hour" in t.get_sla_hours("technical"))

print("\n8. the metadata matches the hand-written schema idea from Unit 1")
# the point: this dict is what TOOL_SCHEMA was, but generated, not written
meta = function_metadata(kernel, "tickets", "get_sla_hours")
chk("has a name", "name" in meta)
chk("has a description", meta["description"])
chk("has typed parameters", meta["parameters"][0]["name"] == "queue")

print("\n" + ("ALL PASS" if ok else "SOMETHING FAILED"))
sys.exit(0 if ok else 1)
