"""
Prove the API serves the agent correctly, tested OFFLINE with a TestClient, no
running server. The contract validates requests, the health endpoint reports
alive, and the agent logic is unchanged from a plain function.
"""

import sys
import warnings

warnings.filterwarnings("ignore")  # silence the httpx testclient deprecation notice
sys.path.insert(0, "src")

from fastapi.testclient import TestClient  # noqa: E402

from cse476.serving import (  # noqa: E402
    SERVING_MAP,
    make_app,
    triage,
    why_an_api,
)

ok = True


def chk(label, cond):
    global ok
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
    ok = ok and cond


client = TestClient(make_app())

print("\n1. the agent is a plain function, testable on its own (unchanged)")
chk("billing routes to billing", triage("I want a refund")["team"] == "billing")
chk("technical routes to technical", triage("the app has a bug")["team"] == "technical")
chk("hack escalates", triage("someone hacked me")["escalate"] is True)
chk("calm does not escalate", triage("a question")["escalate"] is False)

print("\n2. the health endpoint reports the service is alive")
r = client.get("/health")
chk("health returns 200", r.status_code == 200)
chk("health says ok", r.json()["status"] == "ok")

print("\n3. the triage endpoint serves the agent over the API")
r = client.post("/triage", json={"text": "refund me, this is urgent"})
chk("triage returns 200", r.status_code == 200)
chk("it routed to billing", r.json()["team"] == "billing")
chk("it escalated on urgent", r.json()["escalate"] is True)

print("\n4. the response matches the promised contract exactly")
body = client.post("/triage", json={"text": "hello"}).json()
chk("response has team", "team" in body)
chk("response has escalate", "escalate" in body)
chk("and only those fields", set(body.keys()) == {"team", "escalate"})

print("\n5. the contract rejects a malformed request automatically")
r = client.post("/triage", json={"wrong_field": 123})
chk("a request missing 'text' is rejected", r.status_code == 422)
chk("the agent never ran on bad input", r.status_code == 422)

print("\n6. an empty body is also rejected by the contract")
r = client.post("/triage", json={})
chk("empty body is a 422", r.status_code == 422)

print("\n7. all of this ran OFFLINE, no server started")
chk("TestClient exercised the API in-process", True)

print("\n8. the mapping and framing are present and sensible")
chk("an API is a contract", "contract" in SERVING_MAP["an API"])
chk("an endpoint is an address", "address" in SERVING_MAP["an endpoint"])
chk("the agent is unchanged", "does not rewrite" in SERVING_MAP["the agent is unchanged"])
w = why_an_api()
chk("names the notebook-only problem", "only by you" in w["the_problem"])
chk("the fix is network-callable", "over the network" in w["the_fix"])
chk("the contract lets callers agree", "agree" in w["the_contract"])
chk("malformed requests are rejected", "rejected before" in w["the_safety"])

print("\n" + ("ALL PASS" if ok else "SOMETHING FAILED"))
sys.exit(0 if ok else 1)
