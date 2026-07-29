"""
Prove the real switch-case router works offline: classify once, route to exactly
one handler, first-match-wins ordering, and a default that catches unmatched
work. No model, deterministic, no tokens.
"""

import asyncio
import sys

sys.path.insert(0, "src")

from cse476.routing import (  # noqa: E402
    ROUTING_MAP,
    build_router,
    fan_out_vs_route,
    run_router,
)

ok = True


def chk(label, cond):
    global ok
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
    ok = ok and cond


def run(coro):
    return asyncio.run(coro)


print("\n1. the router builds")
wf = build_router()
chk("workflow exists", wf is not None)
chk("it has a run method", hasattr(wf, "run"))

print("\n2. each kind of ticket goes to exactly one matching handler")
chk("billing routes to billing", "Billing team" in run(run_router("I was charged twice, need a refund")))
chk("technical routes to technical", "Technical team" in run(run_router("the app crashes with an error")))
chk("account routes to account", "Account team" in run(run_router("I am locked out, forgot my password")))

print("\n3. only ONE handler runs, not all of them")
out = run(run_router("I was charged twice"))
chk("billing handler ran", "Billing team" in out)
chk("technical handler did NOT run", "Technical team" not in out)
chk("account handler did NOT run", "Account team" not in out)
chk("output is a single handler's result", out.count("handling:") == 1)

print("\n4. the default catches anything that matches no case")
out = run(run_router("hello, just saying hi"))
chk("unmatched ticket hits the general queue", "General queue" in out)
chk("no specific handler claimed it",
    all(team not in out for team in ("Billing team", "Technical team", "Account team")))

print("\n5. routing is deterministic")
a = run(run_router("refund my invoice please"))
b = run(run_router("refund my invoice please"))
chk("same ticket, same route, every time", a == b)
chk("and it is the billing route", "Billing team" in a)

print("\n6. first match wins (ordering matters)")
# a ticket mentioning both a charge and an error should hit billing, the first case
out = run(run_router("I was charged for a plan that gives an error"))
chk("first matching case (billing) wins over later ones", "Billing team" in out)
chk("the later technical case did not steal it", "Technical team" not in out)

print("\n7. the mapping ties routing to familiar ideas")
chk("Case is one switch branch", "switch" in ROUTING_MAP["Case(condition, target)"].lower())
chk("Default is the else branch", "else" in ROUTING_MAP["Default(target)"].lower())
chk("first match wins is explained", "order" in ROUTING_MAP["first match wins"].lower())
chk("one path runs is contrasted with fan-out", "fan-out" in ROUTING_MAP["one path runs"].lower())

print("\n8. the fan-out vs route framing is present and honest")
fr = fan_out_vs_route()
chk("names fan-out behaviour", "everyone" in fr["fan_out"])
chk("names routing behaviour", "one" in fr["route"])
chk("says when to route", "owns" in fr["use_route_when"])
chk("warns hand-rolled routing can drop work", "drop" in fr["the_default_matters"])

print("\n" + ("ALL PASS" if ok else "SOMETHING FAILED"))
sys.exit(0 if ok else 1)
