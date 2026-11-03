"""
Ship the service to a Hugging Face Space: a free, public host that builds and runs
our Dockerfile and gives it a URL anyone can open on a phone.

CI runs this after every green push to main. It needs HF_TOKEN, a Hugging Face
write token stored as a GitHub Actions secret. Without it, it prints a notice and
exits cleanly, so forks and pull requests stay green.

    python deploy/push_space.py
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPACE_ID = os.environ.get("SPACE_ID", "rbi-international/cse476-triage-live")

# Only what the container needs. The Space never sees notebooks, tests or .env.
SHIP = ["Dockerfile", "requirements-serve.txt", "src"]


def bundle(target: Path) -> None:
    """Copy exactly what the image needs, plus the Space's own README."""
    for name in SHIP:
        src = ROOT / name
        if src.is_dir():
            shutil.copytree(src, target / name, ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"))
        else:
            shutil.copy2(src, target / name)
    shutil.copy2(ROOT / "deploy" / "space_README.md", target / "README.md")


def main() -> int:
    token = os.environ.get("HF_TOKEN")
    if not token:
        print("::notice::HF_TOKEN is not set, so nothing was deployed.")
        return 0

    from huggingface_hub import HfApi

    api = HfApi(token=token)
    api.create_repo(SPACE_ID, repo_type="space", space_sdk="docker", exist_ok=True)
    sha = os.environ.get("GITHUB_SHA", "local")[:7]
    with tempfile.TemporaryDirectory() as tmp:
        bundle(Path(tmp))
        api.upload_folder(
            folder_path=tmp,
            repo_id=SPACE_ID,
            repo_type="space",
            commit_message=f"Deploy {sha} from GitHub Actions",
            delete_patterns=["*"],  # the Space holds exactly this commit, nothing stale
        )
    print(f"Deployed {sha} to https://huggingface.co/spaces/{SPACE_ID}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
