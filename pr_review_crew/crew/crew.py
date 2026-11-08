"""
The crew: lead -> specialists in parallel -> judge -> fixer -> one review.
"""

from __future__ import annotations

import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from crew import agents, tools
from crew.diff import parse
from crew.llm import LLM
from crew.trace import Trace

SEV_ICON = {"high": "HIGH", "medium": "MEDIUM", "low": "LOW"}


def run(diff_text: str, repo: Path, llm: LLM | None, trace: Trace, apply_diff: bool = False) -> dict:
    """Review one pull request.

    diff_text   the pull request as a unified diff
    repo        the project; with apply_diff=True the diff is applied to a copy first (web demo),
                otherwise repo is already the pull request's code (GitHub Actions checkout)
    """
    files = parse(diff_text)
    work = tools.workspace(repo, diff_text) if apply_diff else repo
    trace.emit("crew", "start", "model: " + (llm.model if llm else "none, offline mode (tools only)"))
    try:
        ctx = agents.Context(files, diff_text, work, llm, trace)
        team = agents.lead(ctx)
        with ThreadPoolExecutor(max_workers=len(team)) as pool:  # the specialists work at the same time
            results = list(pool.map(lambda name: agents.SPECIALISTS[name](ctx), team))
        findings = [f for group in results for f in group]
        decision = agents.judge(ctx, findings)
        fixes = agents.fixer(ctx, decision["findings"])
    finally:
        if apply_diff:
            shutil.rmtree(work.parent, ignore_errors=True)
    result = {**decision, "fixes": fixes, "team": team, "totals": trace.totals()}
    trace.emit("crew", "done", f"{result['verdict']} in {result['totals']['seconds']} s, "
               f"{result['totals']['llm_calls']} model call(s), {result['totals']['tokens']} tokens", result=result)
    return result


def markdown(result: dict) -> str:
    """The single review comment the judge posts."""
    t = result["totals"]
    out = [f"## PR Review Crew: {result['verdict']}", "", result["summary"], "",
           f"Team sent by the lead: {', '.join(result['team'])}. "
           f"{t['llm_calls']} model call(s), {t['tokens']} tokens, {t['seconds']} s. "
           f"The judge dropped {result['dropped']} weak or duplicate finding(s).", ""]
    if result["findings"]:
        out += ["| Severity | Found by | Finding | Where |", "|---|---|---|---|"]
        for f in result["findings"]:
            where = f"`{f['path']}:{f['line']}`" if f["line"] else "whole change"
            out.append(f"| {SEV_ICON[f['severity']]} | {f['agent']} | {f['title']} | {where} |")
        general = [f for f in result["findings"] if not f["line"]]
        for f in general:
            out += ["", f"**{f['title']}**", "", f["detail"]]
    if result["fixes"]:
        out += ["", f"{len(result['fixes'])} suggested fix(es) are attached to the lines below; "
                "each one was tested: the suite still passes with it."]
    out += ["", "_A bot review never approves or merges. A human decides._"]
    return "\n".join(out)


def inline_comments(result: dict) -> list[dict]:
    """GitHub review comments on the exact lines, with suggested changes where a fix passed the tests."""
    fixes = {(x["path"], x["line"]): x for x in result["fixes"]}
    comments = []
    for f in result["findings"]:
        if not f["line"]:
            continue
        body = f"**{SEV_ICON[f['severity']]}: {f['title']}** ({f['agent']} agent)\n\n{f['detail']}"
        fx = fixes.get((f["path"], f["line"]))
        if fx:
            body += f"\n\nSuggested fix (tests: {fx['tests']}):\n```suggestion\n{fx['suggestion']}\n```"
        comments.append({"path": f["path"], "line": f["line"], "side": "RIGHT", "body": body})
    return comments
