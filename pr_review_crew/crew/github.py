"""
Post the judge's review to a GitHub pull request.

Uses the GITHUB_TOKEN that GitHub Actions gives every run (no personal token), with
permission to comment on pull requests only. The review is always a COMMENT: a bot
never approves and never blocks; a human decides.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request


def post_review(repo: str, pr: int, token: str, commit: str, body: str, comments: list[dict]) -> str:
    url = f"https://api.github.com/repos/{repo}/pulls/{pr}/reviews"
    payload = {"commit_id": commit, "body": body, "event": "COMMENT", "comments": comments}
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST", headers={
        "Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "pr-review-crew"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read()).get("html_url", "posted")
    except urllib.error.HTTPError as exc:
        if comments and exc.code == 422:  # a line GitHub will not accept: post the summary alone
            return post_review(repo, pr, token, commit, body + "\n\n(Inline comments could not be attached.)", [])
        raise
