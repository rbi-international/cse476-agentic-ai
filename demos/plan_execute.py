"""Planner-executor, offline. A fixed planner stands in for the model so the
loop is runnable and repeatable; swap planner() for an LLM call that returns
the same Plan shape and nothing else changes."""
from dataclasses import dataclass, field


@dataclass
class Step:
    task: str
    worker: str
    done: bool = False
    result: str = ""


@dataclass
class Plan:
    goal: str
    steps: list[Step] = field(default_factory=list)


def planner(goal: str) -> Plan:
    return Plan(goal, [
        Step("collect CA2 submissions", "collector"),
        Step("check plagiarism", "checker"),
        Step("upload marks to UMS", "uploader"),
    ])


WORKERS = {
    "collector": lambda t: "58 reports collected",
    "checker": lambda t: "3 reports above 30% similarity",
    "uploader": lambda t: (_ for _ in ()).throw(RuntimeError("UMS session expired")),
    "relogin": lambda t: "logged in again",
}


def replan(plan: Plan, failed: Step) -> None:
    i = plan.steps.index(failed)
    plan.steps.insert(i, Step("log in to UMS again", "relogin"))
    WORKERS["uploader"] = lambda t: "58 marks uploaded"


def run(goal: str, max_rounds: int = 6) -> None:
    plan = planner(goal)
    print("PLAN:", [s.task for s in plan.steps])
    rounds = 0
    while not all(s.done for s in plan.steps) and rounds < max_rounds:
        rounds += 1
        step = next(s for s in plan.steps if not s.done)
        try:
            step.result = WORKERS[step.worker](step.task)
            step.done = True
            print(f"round {rounds}: {step.worker:9s} OK    {step.result}")
        except RuntimeError as e:
            print(f"round {rounds}: {step.worker:9s} FAIL  {e}  -> replan")
            replan(plan, step)
    print("DONE" if all(s.done for s in plan.steps) else "GAVE UP", "in", rounds, "rounds")


if __name__ == "__main__":
    run("finish CA2 evaluation for K2E2330")
