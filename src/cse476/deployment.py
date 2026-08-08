"""
Shipping it: deployment and CI/CD, the finale of the unit and the course.

Unit 5 Lecture 5. Your agent is a service with an API, tested, validated, and
observable. The last step is getting it out into the world and keeping it there
safely. That is two ideas:

  DEPLOYMENT, packaging the service so it runs anywhere, not just on your laptop.
  A container (Docker) is the standard recipe: it bundles your code with its exact
  dependencies so it runs the same on your machine, a colleague's, and a cloud
  server. "It works on my machine" stops being an excuse.

  CI/CD, a pipeline that tests and ships every change automatically. Continuous
  Integration runs your tests on every push; Continuous Delivery ships the change
  if they pass. The golden rule: a failing test STOPS the ship. Nothing broken
  reaches production, because the pipeline will not let it.

This module makes both concrete and checkable offline: a deploy pipeline as
ordered gates, and a production-readiness checklist that ties the whole course
together. And the real proof is that this course has had a working CI pipeline
running on every push the entire time.

    run_pipeline        ordered stages; ship only if every gate passes, in order
    readiness_score     the production-ready checklist, verified
    dockerfile_lines    the recipe that packages the service to run anywhere
"""

from __future__ import annotations


# ---------------------------------------------------------------- the pipeline

def run_pipeline(stages: list[tuple[str, bool]]) -> dict:
    """
    Run a deploy pipeline: ordered stages, each a gate that must pass.

    The stages run in order, and the FIRST failure stops everything. If tests
    fail, the build never happens and nothing ships. This is the golden rule of
    CI/CD made literal: a broken change cannot reach production, because the gate
    before production refuses to open. Ship only when every gate is green.
    """
    for name, passed in stages:
        if not passed:
            return {"shipped": False, "failed_at": name}
    return {"shipped": True, "failed_at": None}


STANDARD_PIPELINE = ["lint", "test", "build", "deploy"]


def describe_pipeline() -> dict[str, str]:
    """What each stage of a normal pipeline does, in order."""
    return {
        "lint": "check the code is clean and consistent (static, no run needed)",
        "test": "run the test suite; a single failure stops the pipeline here",
        "build": "package the service into a container image that runs anywhere",
        "deploy": "push the image to the cloud and start it, only if all above passed",
    }


# ---------------------------------------------------------------- readiness

# A checklist version of "production-ready". Each item is something you can point
# at and verify. This deliberately gathers the whole unit: tests (L1), validation
# (L2), observability (L3), an API with a health check (L4), and now packaging and
# a pipeline (L5). If any is missing, the service is not ready, and the checklist
# tells you exactly what to fix.

READINESS_CHECKS: tuple[str, ...] = (
    "has_tests",            # L1: the skeleton and model-part are tested
    "validates_output",     # L2: model output is checked before use
    "is_observable",        # L3: traces, metrics, logs
    "has_api",              # L4: reachable behind an endpoint
    "has_health_endpoint",  # L4: a heartbeat for the infrastructure
    "has_dockerfile",       # L5: packaged to run anywhere
    "has_ci",               # L5: tests run automatically on every change
)


def readiness_score(checks: dict[str, bool]) -> dict:
    """
    Score a service against the production-readiness checklist.

    Returns whether it is ready, how many checks passed, and which are still
    missing. "Ready" means every check passes, because each one is something that
    bites you in production if it is absent. The missing list is your to-do.
    """
    missing = [name for name in READINESS_CHECKS if not checks.get(name, False)]
    passed = len(READINESS_CHECKS) - len(missing)
    return {
        "ready": len(missing) == 0,
        "passed": passed,
        "total": len(READINESS_CHECKS),
        "missing": missing,
    }


# ---------------------------------------------------------------- packaging

def dockerfile_lines() -> list[str]:
    """
    The recipe that packages the service to run anywhere.

    A Dockerfile is a short, ordered set of steps that builds a self-contained
    image: start from a known Python, copy the code, install the exact deps,
    expose the port, and state the command that starts the service. Anyone who
    runs this image gets the exact same environment, which is what "runs anywhere"
    really means. This is returned as data so it can be checked, but it is a real,
    minimal Dockerfile for the L4 service.
    """
    return [
        "FROM python:3.12-slim",
        "WORKDIR /app",
        "COPY requirements.txt .",
        "RUN pip install --no-cache-dir -r requirements.txt",
        "COPY . .",
        "EXPOSE 8000",
        "CMD [\"uvicorn\", \"cse476.serving:make_app\", \"--factory\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]",
    ]


# ---------------------------------------------------------------- the mapping

DEPLOYMENT_MAP: dict[str, str] = {
    "deployment": "packaging the service so it runs anywhere, not just your laptop",
    "a container": "code plus exact dependencies, so it runs the same everywhere",
    "CI": "continuous integration: run the tests automatically on every change",
    "CD": "continuous delivery: ship the change automatically, if the tests pass",
    "the golden rule": "a failing test stops the ship; nothing broken reaches production",
    "production-ready": "a checklist: tested, validated, observable, served, packaged, automated",
}


def the_course_arc() -> dict[str, str]:
    """
    The whole course in one place, stated for the final slide.

    Each unit added one layer, and together they turn a first idea into a
    shippable product. A student who has done all six can take a real problem and
    build an agent, make it reliable, use real frameworks, compose many agents,
    and ship the result as a tested, observable, deployed service. That is the
    capability the course set out to teach.
    """
    return {
        "unit_1": "build a single agent that plans, uses tools, and remembers",
        "unit_2": "make it reliable: guardrails, retries, honest failure",
        "unit_3": "build on real frameworks, not a toy loop",
        "unit_4": "compose many agents: route, fan out, share, decide",
        "unit_5": "ship it: test, validate, observe, serve, and deploy",
        "the_result": "a real problem becomes a production agent system you can trust",
    }
