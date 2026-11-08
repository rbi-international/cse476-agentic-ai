"""
Run the crew from the command line.

    In GitHub Actions (the pr-review workflow sets everything):
        python -m crew.cli --base <base commit>

    On your laptop or in Codespaces, on a sample pull request against the demo project:
        python -m crew.cli --sample 02_hardcoded_key
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from crew import crew, github
from crew.llm import from_env
from crew.trace import Trace

HERE = Path(__file__).resolve().parent.parent


def main() -> int:
    ap = argparse.ArgumentParser(description="PR Review Crew")
    ap.add_argument("--base", help="base commit of the pull request (review the current checkout)")
    ap.add_argument("--sample", help="name of a sample pull request in samples/ (reviews the demo project)")
    ap.add_argument("--quiet", action="store_true", help="no JSON log lines, only the review")
    args = ap.parse_args()

    trace = Trace(quiet=args.quiet)
    llm = from_env()
    if args.sample:
        diff = (HERE / "samples" / f"{args.sample}.diff").read_text()
        result = crew.run(diff, HERE / "demo_repo", llm, trace, apply_diff=True)
    elif args.base:
        root = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                                   check=True).stdout.strip())
        diff = subprocess.run(["git", "diff", "--unified=3", f"{args.base}...HEAD"], cwd=root,
                              capture_output=True, text=True, check=True).stdout
        if not diff.strip():
            print("No changes to review.")
            return 0
        result = crew.run(diff, root, llm, trace, apply_diff=False)
    else:
        ap.error("give --base or --sample")

    body = crew.markdown(result)
    comments = crew.inline_comments(result)
    print("\n" + body)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:  # the review also appears on the Actions run page
        Path(summary).write_text(body + "\n\n<details><summary>Inline comments</summary>\n\n```json\n"
                                 + json.dumps(comments, indent=1) + "\n```\n</details>\n")

    token, repo, pr = os.environ.get("GITHUB_TOKEN"), os.environ.get("GITHUB_REPOSITORY"), os.environ.get("PR_NUMBER")
    if args.base and token and repo and pr:
        try:
            url = github.post_review(repo, int(pr), token, os.environ.get("HEAD_SHA", ""), body, comments)
            print(f"Review posted: {url}")
        except Exception as exc:  # a fork's pull request gets a read-only token: keep the summary, do not fail
            print(f"::warning::Could not post the review ({exc}); it is in the job summary instead.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
