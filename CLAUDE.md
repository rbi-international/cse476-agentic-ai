# CSE476 Agentic AI course repo

## Deployment (live classroom service)
- App: src/cse476/live.py (make_live_app). Phone questions: src/cse476/quiz.py + quiz_questions.json
- Run locally: uvicorn cse476.live:make_live_app --factory --reload
- Tests must pass before any push: pytest -q (29 tests)
- CI (.github/workflows/ci.yml) is the "check" job only: lint + tests. It deploys nothing.
- Deploy is a manual class demo from the laptop on Azure Container Apps:
  az containerapp up --source . (Azure builds the Dockerfile; no local Docker needed).
- Never put tokens, keys or passwords in code or in committed files.
