# CSE476 Agentic AI course repo

## Deployment (live classroom service)
- App: src/cse476/live.py (make_live_app). Phone questions: src/cse476/quiz.py + quiz_questions.json
- Run locally: uvicorn cse476.live:make_live_app --factory --reload
- Tests must pass before any push: pytest -q (29 tests)
- CI (.github/workflows/ci.yml) is the "check" job only: lint + tests. It deploys nothing.
- Deploy is a manual class demo from the laptop on Azure Container Apps:
  az containerapp up --source . (Azure builds the Dockerfile; no local Docker needed).
- Never put tokens, keys or passwords in code or in committed files.

## PR Review Crew (pr_review_crew/)
- Multi-agent pull request reviewer: lead, tests/security/quality/docs in parallel, judge, fixer.
- Own config and tests: cd pr_review_crew && ruff check . && python -m pytest -q (13 tests, no key needed).
- Runs on every PR via .github/workflows/pr-review.yml. Keep the trigger pull_request, never
  pull_request_target (the crew runs the PR's tests; pull_request_target would expose secrets).
- High-severity tool findings must stay un-droppable by the model (test_the_judge_cannot_drop...).
- Model key only from the GROQ_API_KEY secret / environment; offline mode must keep working.
