"""Companion demos for the testing-to-deployment slides. Run from the repository root:
    python demos/u5_demos.py
Every output shown on the slides comes from this file."""
import sys
sys.path.insert(0, "src")
from fastapi.testclient import TestClient

from cse476 import deployment as dep
from cse476 import live
from cse476 import observability as obs
from cse476 import serving as srv
from cse476 import testing_agents as ta
from cse476 import validation as val

print("== T1 plain tool, tested exactly")
print("check_refund_eligible(12, 1800) ->", ta.check_refund_eligible(12, 1800))
print("check_refund_eligible(45, 1800) ->", ta.check_refund_eligible(45, 1800))
print("check_refund_eligible(30, 5000) ->", ta.check_refund_eligible(30, 5000))
print("check_refund_eligible(30, 5001) ->", ta.check_refund_eligible(30, 5001))

print("== T2 FakeClient: awkward model answers")
for ans in ["billing", "  Billing \n", "TECHNICAL", "the moon", ""]:
    print(repr(ans), "->", ta.decide_route("I was charged twice for hostel fee", ta.FakeClient(ans)))
f = ta.FakeClient("billing"); ta.decide_route("refund my CA fee", f)
print("prompt sent:", repr(f.prompts_seen[0]))

print("== T3 ReplayClient + diagnose")
r = ta.ReplayClient(["Billing.", "billing"])
print(ta.diagnose_route("charged twice", r))
print(ta.diagnose_route("charged twice", r))

print("== T4 safe_call")
def lookup(roll):
    db = {"12345678": "K2E23"}
    return db[roll]
print(ta.safe_call(lookup, "12345678"))
print(ta.safe_call(lookup, "99999999"))

print("== V1 structural")
for a in ["billing", "Billing.", "the moon"]:
    print("validate_choice", repr(a), "->", val.validate_choice(a, {"billing", "technical", "account"}))
for a in ["15", "15%", "150", "free"]:
    print("validate_number", repr(a), "->", val.validate_number(a, 0, 50))

print("== V2 grounding")
src = "Hostel fee refunds are allowed within 30 days of payment. Refunds above 5000 need warden approval."
for claim in ["Refunds are allowed within 30 days", "Refunds are allowed within 60 days", "Refunds need principal approval"]:
    print(repr(claim), "grounded:", val.is_grounded(claim, src), "| invented:", val.find_unsupported_claim(claim, src))

print("== V2b grounding false passes")
for claim in ["Refunds are not allowed within 30 days", "Refunds above 50 need warden approval",
              "Refunds are allowed within 300 days"]:
    print(repr(claim), "grounded:", val.is_grounded(claim, src))

print("== V3 cross-check")
print("model says 5000, tool says 4200 ->", val.cross_check(5000, 4200))

print("== V4 validate_answer")
print(val.validate_answer("Refunds are allowed within 60 days", src))
print(val.validate_answer("Refunds are allowed within 30 days", src))
print(val.validate_answer("the moon", src, {"billing", "technical"}))

print("== O1 trace")
t = obs.trace_run([("classify", 120.0), ("policy_lookup", 840.0), ("llm_answer", 1310.0), ("validate", 15.0)])
print("path:", t.path(), "| total:", t.total_ms(), "ms | slowest:", t.slowest())
print("== O2 metrics over 5 runs")
m = obs.Metrics()
runs = [([("classify", 110), ("llm_answer", 900)], False), ([("classify", 130), ("llm_answer", 1500)], False),
        ([("classify", 100), ("llm_answer", 4200)], True), ([("classify", 120), ("llm_answer", 1100)], False),
        ([("classify", 140), ("llm_answer", 950)], False)]
for steps, failed in runs:
    m.observe(obs.trace_run(steps), failed=failed)
print("runs", m.runs, "| avg", m.average_ms(), "ms | failure rate", m.failure_rate())
print("== O3 structured log")
print(obs.log_line("run-0042", t, "ok"))

print("== S1 API")
c = TestClient(srv.make_app())
print("GET /health ->", c.get("/health").status_code, c.get("/health").json())
r1 = c.post("/triage", json={"text": "Refund my hostel fee, someone tried to hack my UMS, urgent"})
print("POST /triage ->", r1.status_code, r1.json())
r2 = c.post("/triage", json={"text": "UMS shows an error on CA upload"})
print("POST /triage ->", r2.status_code, r2.json())
r3 = c.post("/triage", json={"message": "wrong field name"})
print("POST /triage bad ->", r3.status_code, r3.json()["detail"][0]["type"], r3.json()["detail"][0]["loc"])
r4 = c.get("/triage")
print("GET /triage ->", r4.status_code, r4.json())

print("== D1 pipeline")
print(dep.run_pipeline([("lint", True), ("test", True), ("build", True), ("deploy", True)]))
print(dep.run_pipeline([("lint", True), ("test", False), ("build", True), ("deploy", True)]))
print("== D2 readiness")
print(dep.readiness_score({k: True for k in dep.READINESS_CHECKS}))
print(dep.readiness_score({"has_tests": True, "has_api": True, "has_dockerfile": True}))

print("== L1 live service: phone tickets")
lc = TestClient(live.make_live_app())
for text in ["I paid the hostel fee twice, please refund", "Someone hacked my UMS account, urgent",
             "The CA upload page shows an error", "Hostel room AC not working"]:
    print(repr(text), "->", lc.post("/ticket", json={"text": text}).json())
print("'hi' ->", lc.post("/ticket", json={"text": "hi"}).status_code)
print("== L2 live service: dashboard numbers")
print(lc.get("/stats").json())
