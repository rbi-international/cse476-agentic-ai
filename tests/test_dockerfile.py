"""The Dockerfile and dockerfile_lines() must say the same thing, line for line."""

from pathlib import Path

from cse476.deployment import dockerfile_lines

ROOT = Path(__file__).resolve().parents[1]


def test_dockerfile_matches_the_documented_recipe():
    on_disk = [ln for ln in (ROOT / "Dockerfile").read_text().splitlines() if ln.strip()]
    assert on_disk == dockerfile_lines()


def test_the_container_can_import_our_package():
    # our code lives in src/; without this line the container cannot import cse476
    assert "ENV PYTHONPATH=/app/src" in dockerfile_lines()


def test_the_container_does_not_run_as_root():
    assert any(ln.startswith("USER ") and ln != "USER root" for ln in dockerfile_lines())
