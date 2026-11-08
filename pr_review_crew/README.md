# PR Review Crew

A team of AI agents that reviews every pull request in this repository, posts one
review on GitHub, and suggests fixes that it has already tested.

```
                 lead  (reads the change, picks the team)
                   |
    +--------------+---------------+--------------+
  tests          security         quality         docs        <- run in parallel
 (pytest)   (keys, eval, injection) (missing tests) (docstrings)
    +--------------+---------------+--------------+
                   |
                 judge (merges, drops weak findings, decides; the only one that posts)
                   |
                 fixer (one-line fixes, kept only if the whole test suite still passes)
```

Tools find the facts (a test failed, a key-shaped string is on line 6). The model explains
and prioritises them. A high-severity fact from a tool cannot be dropped by the model, so
text inside a pull request cannot talk the crew out of it.

## 1. Run it on your laptop or in Codespaces

```bash
cd pr_review_crew
pip install -r requirements.txt
python -m crew.cli --sample 02_hardcoded_key     # one review, printed
uvicorn crew.web:app --port 8080                 # the live web page: http://127.0.0.1:8080
python -m pytest -q                              # the crew's own tests
```

Without a key the crew runs **offline**: every agent uses its tools only. With a free Groq
key it also uses the model (explanations, extra findings, the judge's summary, fixes):

```bash
export GROQ_API_KEY=gsk_...        # Windows PowerShell: $env:GROQ_API_KEY="gsk_..."
```

Never put the key in a file in this repository.

## 2. Let it review your pull requests on GitHub

1. On your fork: **Settings > Secrets and variables > Actions > New repository secret**,
   name `GROQ_API_KEY`, value your key. (Optional: without it the crew reviews offline.)
2. **Actions** tab: enable workflows on your fork if GitHub asks.
3. Make a branch, change something, push, and open a pull request **into your own fork's main**.
4. The `pr-review-crew` workflow runs and posts its review on the pull request.

Try the samples on the real code: copy a mistake from `samples/` into your branch, for example
a hard-coded key in `src/cse476/serving.py`, and watch the review arrive.

## 3. Deploy the web page (Docker)

```bash
docker build -t pr-review-crew .
docker run -p 8080:8080 -e GROQ_API_KEY=$GROQ_API_KEY pr-review-crew
```

The container listens on `$PORT` (default 8080), so Google Cloud Run and AWS run it unchanged.

## Files

| Path | What it is |
|---|---|
| `crew/agents.py` | the seven agents and their prompts |
| `crew/tools.py` | the deterministic tools: pytest, secret, injection and danger scanners, fix testing |
| `crew/crew.py` | the orchestration: lead, parallel specialists, judge, fixer |
| `crew/trace.py` | every step as an event: live page, Actions log, cloud logs |
| `crew/web.py` | the web page with the live trace |
| `crew/cli.py`, `crew/github.py` | GitHub Actions entry point and the review posting |
| `demo_repo/`, `samples/` | a small project and five sample pull requests for the web demo |
| `../.github/workflows/pr-review.yml` | runs the crew on every pull request |
