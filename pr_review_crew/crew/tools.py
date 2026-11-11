"""
The agents' tools: plain, deterministic functions.

The tools find facts (a test failed, a key-shaped string is on line 6). The model
explains and prioritises them. A finding a tool produced can never be talked away
by text inside the pull request, which is what makes the crew hard to fool.
"""

from __future__ import annotations

import os
import py_compile
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from crew.diff import FileChange

SECRET_PATTERNS = [
    (re.compile(r"""(?i)\b\w*(api[_-]?key|secret|token|passw(or)?d)\w*["']?\s*[:=]\s*["'][^"'\s]{8,}["']"""),
     "a secret-looking value assigned in code"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "an AWS access key id"),
    (re.compile(r"ghp_[A-Za-z0-9]{36}"), "a GitHub personal access token"),
    (re.compile(r"hf_[A-Za-z0-9]{30,}"), "a Hugging Face token"),
    (re.compile(r"gsk_[A-Za-z0-9]{20,}"), "a Groq API key"),
]
INJECTION = re.compile(
    r"(?i)(ignore\s+(all\s+)?(the\s+)?(previous|prior|above)\s+instructions|disregard\s+(all\s+)?(previous|prior)\s+"
    r"instructions|approve\s+this\s+(pr|pull\s+request)|you\s+are\s+now\s+|reveal\s+(your\s+)?system\s+prompt)"
)
DANGEROUS = [
    (re.compile(r"\beval\("), "eval()", "eval() runs any text as code"),
    (re.compile(r"\bexec\("), "exec()", "exec() runs any text as code"),
    (re.compile(r"shell\s*=\s*True"), "shell=True", "shell=True lets input become a shell command"),
    (re.compile(r"pickle\.loads?\("), "pickle", "pickle can run code while loading untrusted data"),
    (re.compile(r"verify\s*=\s*False"), "verify=False", "TLS verification switched off"),
]


def finding(agent, severity, title, detail, path="", line=0, source="tool", category=""):
    return {"agent": agent, "severity": severity, "title": title, "detail": detail,
            "path": path, "line": line, "source": source, "category": category or agent}


def scan_secrets(files: list[FileChange]) -> list[dict]:
    out = []
    for f in files:
        for n, text in f.added.items():
            for rx, what in SECRET_PATTERNS:
                if rx.search(text):
                    out.append(finding("security", "high", "Secret in code",
                                       f"Line looks like {what}. Anyone who can read the repo can use it; "
                                       "read it from an environment variable or a secret store.", f.path, n, category="secret"))
                    break
    return out


def scan_injection(files: list[FileChange]) -> list[dict]:
    out = []
    for f in files:
        for n, text in f.added.items():
            if INJECTION.search(text):
                out.append(finding("security", "high", "Prompt injection aimed at AI reviewers",
                                   "This line tries to give orders to an AI reviewer. The crew treats the pull "
                                   "request as data and ignored it; a human should ask why it is here.", f.path, n,
                                   category="injection"))
    return out


def scan_dangerous(files: list[FileChange]) -> list[dict]:
    out = []
    for f in files:
        if not f.is_python:
            continue
        for n, text in f.added.items():
            for rx, name, why in DANGEROUS:
                if rx.search(text):
                    out.append(finding("security", "medium", f"Dangerous call: {name}", why + ".", f.path, n,
                                       category="dangerous"))
    return out


def scan_quality(files: list[FileChange]) -> list[dict]:
    out = []
    changed_src = [f for f in files if f.is_python and not f.is_test]
    touched_tests = any(f.is_test for f in files)
    for f in changed_src:
        old_names = {t.split("def ", 1)[1].split("(", 1)[0] for t in f.removed if t.lstrip().startswith("def ")}
        new_defs = [(n, t) for n, t in f.added.items() if t.lstrip().startswith("def ")
                    and t.split("def ", 1)[1].split("(", 1)[0] not in old_names]  # changed signatures are not new
        if new_defs and not touched_tests:
            n, t = new_defs[0]
            name = t.split("def ", 1)[1].split("(", 1)[0]
            out.append(finding("quality", "medium", f"New function {name}() has no test",
                               "Nothing in this pull request tests it, so a future change can break it silently.",
                               f.path, n, category="tests-missing"))
        for n, t in f.added.items():
            if len(t) > 100:
                out.append(finding("quality", "low", "Line longer than 100 characters",
                                   "Long lines are hard to review side by side.", f.path, n, category="style"))
            if re.match(r"\s*print\(", t) and "/tests/" not in "/" + f.path:
                out.append(finding("quality", "low", "print() left in library code",
                                   "Use logging, or remove it before merging.", f.path, n, category="style"))
    return out


SIG = re.compile(r"^\s*def\s+(\w+)\s*\((.*?)\)")


def scan_docs(files: list[FileChange]) -> list[dict]:
    """A signature changed but nothing else in the change mentions the new parameter."""
    out = []
    for f in files:
        if not f.is_python:
            continue
        old = {m.group(1): m.group(2) for m in (SIG.match(t) for t in f.removed) if m}
        for n, t in f.added.items():
            m = SIG.match(t)
            if not m or m.group(1) not in old or old[m.group(1)] == m.group(2):
                continue
            params = [p.split(":")[0].split("=")[0].strip() for p in m.group(2).split(",")]
            before = [p.split(":")[0].split("=")[0].strip() for p in old[m.group(1)].split(",")]
            new_params = [p for p in params if p and p not in before and p != "self"]
            others = " ".join(v for k, v in f.added.items() if k != n)
            missing = [p for p in new_params if p not in others]
            if missing:
                out.append(finding("docs", "low", f"{m.group(1)}() gained {', '.join(missing)} but its docstring did not",
                                   "Callers read the docstring, not the code; describe what the new parameter does.",
                                   f.path, n, category="docs"))
    return out


def run_tests(repo: Path, timeout: int = 300) -> dict:
    """Run the project's pytest suite exactly as CI would."""
    env = dict(os.environ, PYTHONPATH=os.pathsep.join(filter(None, [str(repo), str(repo / "src"), os.environ.get("PYTHONPATH", "")])))
    try:
        p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=repo,
                           capture_output=True, text=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return {"passed": False, "summary": f"pytest timed out after {timeout} s", "failures": [], "output": ""}
    lines = (p.stdout + p.stderr).splitlines()
    summary = next((ln.strip("= ") for ln in reversed(lines) if " passed" in ln or " failed" in ln or " error" in ln), "no tests ran")
    failures = [ln for ln in lines if ln.startswith("FAILED") or ln.startswith("E   ")][:12]
    return {"passed": p.returncode == 0, "summary": summary, "failures": failures, "output": "\n".join(lines[-40:])}


def to_lf(root: Path) -> None:
    """Windows checkouts turn line endings into CRLF; git apply on Linux then fails. Make every text file LF."""
    for f in root.rglob("*"):
        if f.is_file() and f.suffix in {".py", ".md", ".toml", ".txt", ".cfg", ".ini", ".json"}:
            b = f.read_bytes()
            if b"\r" in b:
                f.write_bytes(b.replace(b"\r\n", b"\n").replace(b"\r", b""))


def workspace(repo: Path, diff_text: str | None) -> Path:
    """A throwaway copy of the project, with the pull request applied if one is given."""
    tmp = Path(tempfile.mkdtemp(prefix="crew-"))
    dst = tmp / "repo"
    shutil.copytree(repo, dst, ignore=shutil.ignore_patterns(".git", "__pycache__", ".venv", "*.pyc"))
    to_lf(dst)
    if diff_text:
        # bytes, not text: on Windows a text pipe would turn every \n back into \r\n
        data = diff_text.replace("\r\n", "\n").replace("\r", "").encode()
        p = subprocess.run(["git", "apply", "--whitespace=nowarn", "-"], cwd=dst, input=data, capture_output=True)
        if p.returncode != 0:
            err = p.stderr.decode(errors="replace").strip()
            raise ValueError("The diff does not apply to the demo project: " + err[:300])
    return dst


def try_fixes(repo: Path, fixes: list[dict]) -> dict:
    """Apply the proposed one-line fixes to a copy, compile, run the tests."""
    copy = workspace(repo, None)
    try:
        for fx in fixes:
            p = copy / fx["path"]
            lines = p.read_text().splitlines(keepends=True)
            indent = re.match(r"\s*", lines[fx["line"] - 1]).group(0)
            lines[fx["line"] - 1] = indent + fx["replacement"].strip() + "\n"
            p.write_text("".join(lines))
            py_compile.compile(str(p), doraise=True)
        return run_tests(copy)
    except (py_compile.PyCompileError, IndexError, OSError) as exc:
        return {"passed": False, "summary": f"fix did not compile: {exc}", "failures": [], "output": ""}
    finally:
        shutil.rmtree(copy.parent, ignore_errors=True)
