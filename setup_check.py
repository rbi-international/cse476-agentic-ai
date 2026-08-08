#!/usr/bin/env python3
"""
CSE476 setup check.

Run this before the first practical:

    python setup_check.py

It checks your Python version, your packages, your .env file, and every lane
you have configured. It never guesses. If something is missing it tells you the
exact command or the exact line to add.

Nothing here needs a paid account. Groq has a free tier, and Ollama runs free on your own machine.
"""

from __future__ import annotations

import importlib.metadata as md
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

GREEN, RED, YELLOW, DIM, BOLD, OFF = (
    "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[1m", "\033[0m"
)
if os.name == "nt" and not os.getenv("WT_SESSION"):
    GREEN = RED = YELLOW = DIM = BOLD = OFF = ""

PASS, FAIL, WARN = f"{GREEN}pass{OFF}", f"{RED}FAIL{OFF}", f"{YELLOW}warn{OFF}"

problems: list[str] = []
warnings: list[str] = []


def line(status: str, label: str, detail: str = "") -> None:
    print(f"  [{status}] {label}" + (f"  {DIM}{detail}{OFF}" if detail else ""))


def header(text: str) -> None:
    print(f"\n{BOLD}{text}{OFF}")


# ---------------------------------------------------------------- python
header("Python")
v = sys.version_info
if v >= (3, 12):
    line(PASS, f"Python {v.major}.{v.minor}.{v.micro}")
elif v >= (3, 10):
    line(WARN, f"Python {v.major}.{v.minor}", "3.12 recommended, 3.10 will mostly work")
    warnings.append("Upgrade to Python 3.12 when convenient.")
else:
    line(FAIL, f"Python {v.major}.{v.minor}", "too old")
    problems.append("Install Python 3.12 from python.org, then recreate your venv.")

# ---------------------------------------------------------------- packages
header("Packages")
REQUIRED = ["openai", "python-dotenv", "pydantic", "httpx"]
OPTIONAL = ["agent-framework-core", "semantic-kernel", "rich", "pytest"]

for pkg in REQUIRED:
    try:
        line(PASS, pkg, md.version(pkg))
    except md.PackageNotFoundError:
        line(FAIL, pkg, "not installed")
        problems.append("Run: pip install -r requirements.txt")

for pkg in OPTIONAL:
    try:
        line(PASS, pkg, md.version(pkg))
    except md.PackageNotFoundError:
        line(DIM + "skip" + OFF, pkg, "not installed, needed from Unit 3 on")

# ---------------------------------------------------------------- env file
header("Configuration")
env_path = ROOT / ".env"
if env_path.exists():
    line(PASS, ".env found")
else:
    line(FAIL, ".env missing")
    problems.append("Run: cp .env.example .env   (Windows: copy .env.example .env)")

gitignore = ROOT / ".gitignore"
if gitignore.exists() and ".env" in gitignore.read_text(encoding="utf-8"):
    line(PASS, ".env is gitignored", "your keys will not be committed")
else:
    line(FAIL, ".env is NOT gitignored")
    problems.append("Add a line containing .env to .gitignore before you commit anything.")

# ---------------------------------------------------------------- lanes
header("Lanes")
try:
    from cse476.lanes import LANES, PROVIDER, get_model
except Exception as exc:  # noqa: BLE001
    line(FAIL, "cannot import cse476.lanes", str(exc))
    problems.append("Run: pip install -e .   from the repository root.")
    LANES, PROVIDER = {}, "groq"

configured: list[str] = []
for key, lane in LANES.items():
    if getattr(lane, "retired", False):
        continue  # GitHub Models retired 30 July 2026; do not offer it
    if key == "local":
        try:
            import httpx

            httpx.get("http://localhost:11434/api/tags", timeout=1.5)
            line(PASS, f"{key}  {lane.name}", "Ollama is running")
            configured.append(key)
        except Exception:  # noqa: BLE001
            line(DIM + "skip" + OFF, f"{key}  {lane.name}", "Ollama not running, optional")
        continue

    if key == "foundry":
        ok = bool(os.getenv("AZURE_OPENAI_ENDPOINT")) and bool(os.getenv("AZURE_OPENAI_API_KEY"))
    else:
        ok = bool(os.getenv(lane.key_env))

    if ok:
        line(PASS, f"{key}  {lane.name}", "credential present")
        configured.append(key)
    else:
        need = lane.key_env or "no credential needed"
        line(DIM + "skip" + OFF, f"{key}  {lane.name}", f"{need} not set")

if not configured:
    line(FAIL, "no lane is usable")
    problems.append(
        "Set at least one lane. The easiest free options are:\n"
        "      PROVIDER=groq  with GROQ_API_KEY in .env (key at console.groq.com/keys), or\n"
        "      PROVIDER=local with Ollama running on your own machine (no key needed)."
    )
elif PROVIDER not in configured:
    line(FAIL, f"PROVIDER={PROVIDER}", "selected lane is not configured")
    problems.append(f"Set PROVIDER to one of: {', '.join(configured)}")
else:
    line(PASS, f"PROVIDER={PROVIDER}", f"model {get_model()}")

# ---------------------------------------------------------------- live call
header("Live call")
if PROVIDER in configured:
    try:
        from cse476.lanes import get_client
        from cse476.lanes import get_model as gm

        client = get_client()
        r = client.chat.completions.create(
            model=gm(),
            messages=[{"role": "user", "content": "Reply with exactly: ok"}],
            max_tokens=5,
        )
        text = (r.choices[0].message.content or "").strip()
        line(PASS, "model responded", repr(text[:40]))
    except Exception as exc:  # noqa: BLE001
        line(FAIL, "call failed", type(exc).__name__)
        print(f"      {DIM}{str(exc)[:300]}{OFF}")
        problems.append(
            "The credential exists but the call failed. Common causes:\n"
            "      wrong model name for this lane, expired token, or no internet.\n"
            "      See docs/TROUBLESHOOTING.md"
        )
else:
    line(DIM + "skip" + OFF, "no usable lane selected")

# ---------------------------------------------------------------- verdict
print()
if problems:
    print(f"{RED}{BOLD}Not ready yet. {len(problems)} thing(s) to fix:{OFF}")
    for i, p in enumerate(problems, 1):
        print(f"  {i}. {p}")
    print(f"\n{DIM}Stuck? Post this entire output in the course channel.{OFF}")
    sys.exit(1)

print(f"{GREEN}{BOLD}You are ready.{OFF}")
if warnings:
    for w in warnings:
        print(f"  {YELLOW}note{OFF} {w}")
sys.exit(0)
