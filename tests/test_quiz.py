"""The class questions: what students tap must be counted, and nothing else."""

from fastapi.testclient import TestClient

from cse476.live import make_live_app
from cse476.quiz import QUESTIONS


def client() -> TestClient:
    return TestClient(make_live_app())


def test_every_question_has_four_options_and_a_valid_answer():
    assert len(QUESTIONS) == 8
    for q in QUESTIONS.values():
        assert len(q["options"]) == 4 and len(q["why"]) == 4
        assert 0 <= q["answer"] <= 3


def test_a_vote_is_counted():
    c = client()
    assert c.post("/q/1/vote", json={"choice": 1}).status_code == 200
    assert c.get("/q/1/counts").json()["counts"] == [0, 1, 0, 0]


def test_bad_votes_are_rejected():
    c = client()
    assert c.post("/q/1/vote", json={"choice": 7}).status_code == 422
    assert c.post("/q/99/vote", json={"choice": 0}).status_code == 404


def test_the_phone_and_projector_pages_load():
    c = client()
    assert "Question" in c.get("/q/3").text
    assert "votes" in c.get("/q/3/results").text
