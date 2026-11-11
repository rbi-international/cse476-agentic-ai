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


def test_the_judge_cannot_drop_a_fact_a_tool_found():
    r = review("03_prompt_injection", ScriptedModel())
    assert {"injection", "dangerous", "tests-missing"} <= {f["category"] for f in r["findings"]}
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


class MiscountingModel:
    """Plays a model that finds the eval again, with the wrong line number, from two agents."""

    model = "scripted"

    def ask(self, system, user, max_tokens=900):
        if "judge" in system:
            text = json.dumps({"keep": list(range(20)), "summary": "Fix the eval."})
        elif "quality" in system or "documentation" in system:
            text = json.dumps({"findings": [
                {"path": "helpdesk/triage.py", "line": 21, "code": "table = eval(weights)", "severity": "high",
                 "title": "Use of eval on untrusted input", "detail": "eval runs any text."},
                {"path": "helpdesk/triage.py", "line": 22, "code": "not in this pull request", "severity": "low",
                 "title": "Invented problem", "detail": "No such code."}]})
        else:
            text = '{"findings": []}'
        return Reply(text, 5.0, 42)


def test_model_line_numbers_snap_to_the_quoted_code_and_repeats_merge():
    r = review("03_prompt_injection", MiscountingModel())
    on_eval_line = [f for f in r["findings"] if f["line"] == 25]
    assert len(on_eval_line) == 1 and on_eval_line[0]["source"] == "tool"
    assert not any(f["line"] in (21, 22) for f in r["findings"])


class SecondOpinionModel:
    """The docs agent adds a different problem on a line the quality tool already flagged."""

    model = "scripted"

    def ask(self, system, user, max_tokens=900):
        if "judge" in system:
            text = json.dumps({"keep": list(range(20)), "summary": "ok"})
        elif "documentation" in system:
            text = json.dumps({"findings": [{"path": "helpdesk/triage.py", "line": 23, "severity": "medium",
                                             "code": "def priority(text: str, weights: str) -> int:",
                                             "title": "Missing docstring", "detail": "Say what weights holds."}]})
        else:
            text = '{"findings": []}'
        return Reply(text, 5.0, 42)


def test_a_different_problem_on_the_same_line_is_kept():
    r = review("03_prompt_injection", SecondOpinionModel())
    on_23 = {f["title"] for f in r["findings"] if f["line"] == 23}
    assert "Missing docstring" in on_23 and any("no test" in t for t in on_23)


def test_two_tool_facts_on_one_line_both_survive():
    from crew.agents import Context, judge
    files = parse("+++ b/app.py\n@@ -0,0 +1 @@\n+eval(a); exec(b)\n")
    facts = tools.scan_dangerous(files)
    assert len(facts) == 2
    r = judge(Context(files, "", DEMO, None, Trace(quiet=True)), facts)
    assert {f["title"] for f in r["findings"]} == {"Dangerous call: eval()", "Dangerous call: exec()"}


class AlarmistModel:
    """Plays a model that invents a HIGH problem in a clean pull request."""

    model = "scripted"

    def ask(self, system, user, max_tokens=900):
        if "judge" in system:
            text = json.dumps({"keep": list(range(20)), "summary": "ok"})
        elif "quality" in system:
            text = json.dumps({"findings": [{"path": "", "line": 0, "code": "", "severity": "high",
                                             "title": "Missing import for os", "detail": "Will raise NameError."}]})
        else:
            text = '{"findings": []}'
        return Reply(text, 5.0, 42)


def test_a_model_opinion_can_warn_but_never_block():
    r = review("05_clean_fix", AlarmistModel())
    assert r["verdict"] == "looks good, with suggestions"
    assert [f["severity"] for f in r["findings"]] == ["medium"]
    assert "quality (model)" in crew.markdown(r)


def test_the_model_is_shown_the_imports_of_changed_files():
    from crew.agents import Context, imports
    files = parse(sample("02_hardcoded_key"))
    assert "import os" in imports(Context(files, "", DEMO, None, Trace(quiet=True)))


def test_a_windows_checkout_with_crlf_line_endings_still_works(tmp_path):
    """gcloud uploads the files exactly as Windows Git left them: CRLF everywhere."""
    import shutil
    win = tmp_path / "demo"
    shutil.copytree(DEMO, win)
    for f in win.rglob("*.py"):
        f.write_bytes(f.read_bytes().replace(b"\n", b"\r\n"))
    diff = sample("03_prompt_injection")  # read_text() hands the diff over with LF, the files stay CRLF
    r = crew.run(diff, win, None, Trace(quiet=True), apply_diff=True)
    assert r["verdict"] == "changes requested"
