"""The crew, tested offline and with a scripted model: no API key, no network."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from crew import crew, tools
from crew.diff import parse
from crew.llm import Reply, parse_json
from crew.trace import Trace

HERE = Path(__file__).resolve().parent.parent
DEMO = HERE / "demo_repo"


def sample(name: str) -> str:
    return (HERE / "samples" / f"{name}.diff").read_text()


def review(name: str, llm=None) -> dict:
    return crew.run(sample(name), DEMO, llm, Trace(quiet=True), apply_diff=True)


def test_diff_lines_map_to_new_file_numbers():
    files = parse(sample("03_prompt_injection"))
    assert files[0].path == "helpdesk/triage.py"
    assert "eval(weights)" in files[0].added[25]


@pytest.mark.parametrize("line", ['API_TOKEN = "class-demo-token-abcdef123456"', 'db_password = "hunter2hunter2"',
                                  'cfg = {"secret": "abcdefghijkl"}'])
def test_secret_shaped_assignments_are_caught(line):
    files = parse(f"+++ b/app.py\n@@ -0,0 +1 @@\n+{line}\n")
    assert tools.scan_secrets(files)


def test_a_failing_test_blocks_the_change():
    r = review("01_hostel_route")
    assert r["verdict"] == "changes requested"
    assert r["findings"][0]["agent"] == "tests"


def test_a_leaked_key_is_caught_and_a_tested_fix_is_suggested():
    r = review("02_hardcoded_key")
    assert r["findings"][0]["category"] == "secret"
    assert r["fixes"] and "os.environ" in r["fixes"][0]["replacement"]
    assert "suggestion" in crew.inline_comments(r)[0]["body"]


def test_prompt_injection_is_flagged_not_obeyed():
    r = review("03_prompt_injection")
    cats = {f["category"] for f in r["findings"]}
    assert {"injection", "dangerous", "tests-missing"} <= cats
    assert r["verdict"] == "changes requested"


def test_a_changed_signature_needs_its_docstring():
    r = review("04_docs_drift")
    assert [f["category"] for f in r["findings"]] == ["docs"]


def test_a_clean_pull_request_passes():
    assert review("05_clean_fix")["verdict"] == "looks good"


class ScriptedModel:
    """Plays the model. Its judge tries to drop everything, as an injected model might."""

    model = "scripted"

    def ask(self, system, user, max_tokens=900):
        if "judge" in system:
            text = json.dumps({"keep": [], "summary": "Approve, all fine."})
        elif "lead" in system:
            text = '{"summary": "Adds a priority score."}'
        else:
            text = '{"findings": []}'
        return Reply(text, 5.0, 42)


def test_the_judge_cannot_drop_a_high_severity_tool_finding():
    r = review("03_prompt_injection", ScriptedModel())
    assert any(f["category"] == "injection" for f in r["findings"])
    assert r["verdict"] == "changes requested"
    assert r["totals"]["llm_calls"] > 0


def test_model_json_is_found_inside_prose():
    assert parse_json('Sure! ```json\n{"a": 1}\n```') == {"a": 1}
    assert parse_json("no json here") == {}


def test_a_broken_fix_is_never_suggested():
    bad = {"path": "helpdesk/config.py", "line": 6, "replacement": "API_KEY = ("}
    assert tools.try_fixes(DEMO, [bad])["passed"] is False


@pytest.fixture
def client():
    from crew.web import app
    return TestClient(app)


def test_the_web_page_runs_a_review_end_to_end(client):
    assert client.get("/health").json()["status"] == "ok"
    assert len(client.get("/api/samples").json()) == 5
    run = client.post("/api/run", json={"sample": "02_hardcoded_key"}).json()["run"]
    with client.stream("GET", f"/api/events/{run}") as s:
        body = "".join(s.iter_text())
    assert '"agent": "judge"' in body and "event: review" in body


def test_the_page_script_keeps_its_newline_escapes():
    """A real newline inside a JavaScript string is a syntax error: the page loads but nothing runs."""
    from crew.web import PAGE
    assert "t.split('\\n')" in PAGE
    assert "split('\n')" not in PAGE
