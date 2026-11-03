# CSE476 Agentic AI course repo

## Deployment (live classroom service)
- App: src/cse476/live.py (make_live_app). Phone questions: src/cse476/quiz.py + quiz_questions.json
- Run locally: uvicorn cse476.live:make_live_app --factory --reload
- Tests must pass before any push: pytest -q (29 tests)
- Push to main → .github/workflows/ci.yml runs "check", then "deploy" → Hugging Face Space
  rbi-international/cse476-triage-live (https://rbi-international-cse476-triage-live.hf.space)
- Never put tokens in code. HF_TOKEN lives only in GitHub repository secrets.
