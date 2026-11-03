---
paths:
  - "Dockerfile"
  - "requirements-serve.txt"
  - ".github/workflows/**"
  - "deploy/**"
  - "src/cse476/live.py"
  - "src/cse476/quiz*"
---
# Deployment rules
- The Dockerfile must keep: ENV PYTHONPATH=/app/src, USER agent (uid 1000), EXPOSE 8000.
  tests/test_dockerfile.py checks it against deployment.dockerfile_lines(); change both together.
- requirements-serve.txt holds only what the service imports, at exact versions.
- In ci.yml the deploy job must keep "needs: check" and run only on pushes to main.
- deploy/push_space.py uploads only Dockerfile, requirements-serve.txt, src/ and the Space README.
- Keep ruff pinned (0.8.6); an unpinned linter turned CI red before.
- Rollback = git revert the bad commits and push; never force-push main.
