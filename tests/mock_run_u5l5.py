"""
Prove the deployment concepts as checkable logic: a pipeline whose gates stop a
broken change from shipping, a production-readiness checklist that gathers the
whole unit, and a real Dockerfile. All offline, deterministic, no tokens.
"""

import sys

sys.path.insert(0, "src")

from cse476.deployment import (  # noqa: E402
    DEPLOYMENT_MAP,
    READINESS_CHECKS,
    STANDARD_PIPELINE,
    describe_pipeline,
    dockerfile_lines,
    readiness_score,
    run_pipeline,
    the_course_arc,
)

ok = True


def chk(label, cond):
    global ok
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
    ok = ok and cond


print("\n1. a fully green pipeline ships")
result = run_pipeline([("lint", True), ("test", True), ("build", True), ("deploy", True)])
chk("it shipped", result["shipped"] is True)
chk("nothing failed", result["failed_at"] is None)

print("\n2. the golden rule: a failing test STOPS the ship")
result = run_pipeline([("lint", True), ("test", False), ("build", True), ("deploy", True)])
chk("it did NOT ship", result["shipped"] is False)
chk("it stopped at the failed test", result["failed_at"] == "test")

print("\n3. failure stops at the FIRST bad gate, in order")
result = run_pipeline([("lint", False), ("test", False), ("build", True), ("deploy", True)])
chk("it stopped at lint, the first failure", result["failed_at"] == "lint")

print("\n4. the standard pipeline is lint, test, build, deploy")
chk("four stages in order", STANDARD_PIPELINE == ["lint", "test", "build", "deploy"])
d = describe_pipeline()
chk("test stops the pipeline on failure", "stops the pipeline" in d["test"])
chk("build packages a container", "container" in d["build"])
chk("deploy is gated on all above", "only if all above passed" in d["deploy"])

print("\n5. the readiness checklist gathers the whole unit")
chk("it has seven checks", len(READINESS_CHECKS) == 7)
chk("tests (L1) is a check", "has_tests" in READINESS_CHECKS)
chk("validation (L2) is a check", "validates_output" in READINESS_CHECKS)
chk("observability (L3) is a check", "is_observable" in READINESS_CHECKS)
chk("api and health (L4) are checks", "has_api" in READINESS_CHECKS and "has_health_endpoint" in READINESS_CHECKS)
chk("dockerfile and ci (L5) are checks", "has_dockerfile" in READINESS_CHECKS and "has_ci" in READINESS_CHECKS)

print("\n6. readiness is only true when EVERYTHING passes")
full = {name: True for name in READINESS_CHECKS}
chk("all checks pass -> ready", readiness_score(full)["ready"] is True)
one_missing = dict(full)
one_missing["is_observable"] = False
score = readiness_score(one_missing)
chk("one missing -> not ready", score["ready"] is False)
chk("it names what is missing", score["missing"] == ["is_observable"])
chk("it counts passed", score["passed"] == 6 and score["total"] == 7)

print("\n7. the Dockerfile is a real, minimal recipe")
lines = dockerfile_lines()
chk("it starts from a python base", lines[0].startswith("FROM python"))
chk("it installs requirements", any("pip install" in ln for ln in lines))
chk("it exposes a port", any("EXPOSE" in ln for ln in lines))
chk("it starts the L4 service with uvicorn", any("uvicorn" in ln and "serving" in ln for ln in lines))

print("\n8. the mapping and the course arc are present")
chk("deployment is packaging to run anywhere", "runs anywhere" in DEPLOYMENT_MAP["deployment"])
chk("CI runs tests on every change", "every change" in DEPLOYMENT_MAP["CI"])
chk("the golden rule stops broken ships", "nothing broken" in DEPLOYMENT_MAP["the golden rule"])
arc = the_course_arc()
chk("unit 1 is a single agent", "single agent" in arc["unit_1"])
chk("unit 5 is shipping it", "ship it" in arc["unit_5"])
chk("the result is a production system", "production agent system" in arc["the_result"])

print("\n" + ("ALL PASS" if ok else "SOMETHING FAILED"))
sys.exit(0 if ok else 1)
