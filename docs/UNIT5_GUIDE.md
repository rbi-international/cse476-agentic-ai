# Unit 5 run-along guide: testing, monitoring, and deployment

Every file in Unit 5, what it does, and how to run it. This unit turns a working
agent into a shippable service. Everything runs offline and is tested
deterministically, the same discipline as the rest of the course.

Run all commands from the repository root, on the `cse476` environment.

## Lecture 1, testing and debugging

- **Module:** `src/cse476/testing_agents.py`
- **Notebook:** `notebooks/u5/l1_testing.ipynb`
- **Test:** `tests/mock_run_u5l1.py`

Test the deterministic skeleton exactly, and the model-dependent part with a fake
model behind a seam. Debug with the reproduce-isolate-fix-lock-in recipe: a
ReplayClient makes a flaky bug reproducible, diagnose_route isolates the layer.

```bash
python tests/mock_run_u5l1.py
```

## Lecture 2, validation and hallucinations

- **Module:** `src/cse476/validation.py`
- **Notebook:** `notebooks/u5/l2_validation.ipynb`
- **Test:** `tests/mock_run_u5l2.py`

Three checks between the model and the action: structural (on the menu),
grounding (traceable to the source), and cross-check (a tool holds the truth).
Catches a model that confidently invents a fact.

```bash
python tests/mock_run_u5l2.py
```

## Lecture 3, observability

- **Module:** `src/cse476/observability.py`
- **Notebook:** `notebooks/u5/l3_observability.ipynb`
- **Test:** `tests/mock_run_u5l3.py`

The three pillars: a trace (one run, timed, find the slow step), metrics (many
runs, latency and failure rate), and structured logs (searchable). Metrics alert,
logs locate, a trace explains.

```bash
python tests/mock_run_u5l3.py
```

## Lecture 4, serving behind an API

- **Module:** `src/cse476/serving.py`
- **Notebook:** `notebooks/u5/l4_serving.ipynb`
- **Test:** `tests/mock_run_u5l4.py`

A real FastAPI serves the agent with a typed request and response and a health
endpoint. The contract rejects malformed requests for free. Tested offline with a
TestClient, no server needed.

```bash
python tests/mock_run_u5l4.py

# to actually run the service locally:
uvicorn cse476.serving:make_app --factory --reload
# then open http://127.0.0.1:8000/docs
```

## Lecture 5, deployment and CI/CD

- **Module:** `src/cse476/deployment.py`
- **Notebook:** `notebooks/u5/l5_deployment.ipynb`
- **Test:** `tests/mock_run_u5l5.py`
- **Artifacts:** `Dockerfile` (repo root), `.github/workflows/ci.yml`

Package the service with the `Dockerfile` so it runs anywhere; ship every change
with a CI/CD pipeline of gates (a failing test stops the ship). The
production-readiness checklist gathers the whole unit.

```bash
python tests/mock_run_u5l5.py

# to build and run the container (needs Docker):
docker build -t triage-service .
docker run -p 8000:8000 triage-service
```

## Run every Unit 5 test at once

```bash
for f in tests/mock_run_u5l*.py; do echo "== $f =="; python "$f" | tail -1; done
```

## What you can do after this unit

You can take a working agent and make it a product: test it (including the
non-deterministic parts), validate the model's output, watch it in production,
serve it behind an API, and ship it with a container and a pipeline. That is the
whole of Unit 5, and the last layer of the course.
