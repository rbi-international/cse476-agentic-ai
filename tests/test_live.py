"""
The live classroom service, tested offline with TestClient: no server, no network.
Every route the students and the projector use is covered here, so CI refuses to
deploy a version where any of them is broken.
"""

from fastapi.testclient import TestClient

from cse476.live import make_live_app
from cse476.serving import TEAMS


def client() -> TestClient:
    return TestClient(make_live_app())


def test_the_phone_form_and_dashboard_load():
    c = client()
    assert "Send ticket" in c.get("/").text
    assert "Live triage dashboard" in c.get("/dashboard").text


def test_a_ticket_is_routed_and_counted():
    c = client()
    r = c.post("/ticket", json={"text": "I paid the hostel fee twice, please refund"})
    assert r.status_code == 200
    assert r.json()["team"] == "billing"
    stats = c.get("/stats").json()
    assert stats["total"] == 1 and stats["teams"] == {"billing": 1}


def test_escalation_is_counted():
    c = client()
    c.post("/ticket", json={"text": "someone tried to hack my UMS, urgent"})
    assert c.get("/stats").json()["escalations"] == 1


def test_bad_input_is_rejected_before_the_agent_runs():
    c = client()
    assert c.post("/ticket", json={"text": "hi"}).status_code == 422
    assert c.post("/ticket", json={"text": "x" * 301}).status_code == 422
    assert c.get("/stats").json()["total"] == 0


def test_every_answer_is_on_the_menu():
    c = client()
    for text in ["refund please", "the portal shows an error", "library timings?"]:
        assert c.post("/ticket", json={"text": text}).json()["team"] in TEAMS


def test_the_original_api_is_unchanged():
    c = client()
    assert c.get("/health").json() == {"status": "ok"}
    assert c.post("/triage", json={"text": "refund"}).json() == {"team": "billing", "escalate": False}
