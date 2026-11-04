---
paths:
  - "Dockerfile"
  - "requirements-serve.txt"
  - ".github/workflows/**"
  - "src/cse476/live.py"
  - "src/cse476/quiz*"
---
# Deployment rules
- The Dockerfile must keep: ENV PYTHONPATH=/app/src, USER agent (uid 1000), EXPOSE 8000.
  tests/test_dockerfile.py checks it against deployment.dockerfile_lines(); change both together.
- requirements-serve.txt holds only what the service imports, at exact versions.
- ci.yml stays a single "check" job (lint + tests); do not add a deploy job.
- Azure Container Apps builds the Dockerfile with `az containerapp up --source .` and
  --target-port 8000, so EXPOSE 8000 and the uvicorn --port 8000 in CMD must stay in step.
- Keep ruff pinned (0.8.6); an unpinned linter turned CI red before.
- Rollback = git revert the bad commits and push; never force-push main.
