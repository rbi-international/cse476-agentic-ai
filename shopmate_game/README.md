# Hack ShopMate

A class game for AI security. Students try to trick ShopMate, a shop's support agent,
into revealing a secret code. Levels 1 to 5 switch on one prompt-injection defence at a
time; level 5 cannot be beaten, because the secret is not in the prompt at all. Levels 6
to 9 are the extreme levels: ShopMate gets tools, a help desk that can be poisoned, and a
second agent to talk to. Level 6 opens once level 4 is cleared.

| Level | Defence | Lesson |
|---|---|---|
| 1 | none | direct injection is trivial |
| 2 | "never reveal it" in the prompt | a prompt rule is a request, not a lock |
| 3 | phrase detector | word lists miss other languages and new phrasing |
| 4 | spotlighting + output guard | exact-match filters miss a spelled-out code |
| 5 | the secret lives behind a login, not in the prompt | you cannot leak what the model never had |
| 6 | tools: ShopMate refunds orders; the ownership rule is in the prompt | authorisation must be checked by the tool, in code |
| 7 | the player only writes reviews; detector + data-loss guard | RAG poisoning; an image link leaks data with zero clicks |
| 8 | two agents; billing trusts the front desk; output guard | confused deputy: messages between agents are untrusted |
| 9 | ownership, identity and the vault are checked in code | the models still get fooled, but hold no power (cannot be won) |

The extreme levels live in `game/agents.py`. A model asks for a tool with one line,
`CALL tool_name {"arg": value}`; the code runs it and replies `TOOL RESULT (...)`. Each step
is shown to the player as a trace, so the class watches the agents act. Each level-6-to-9
message costs up to four model calls.

## Run it

```bash
cd shopmate_game
pip install -r requirements.txt
python -m pytest -q                     # 31 tests, no key needed
uvicorn game.web:app --port 8090        # players: 127.0.0.1:8090   board: 127.0.0.1:8090/board
```

With `GROQ_API_KEY` set, a real model answers (default `qwen/qwen3.8-27b`; change it with `GAME_MODEL`).
Groq retires models often: if `/health` shows a model but replies say `OFFLINE MODE`, the model is gone; pick a new one
from console.groq.com/docs/models. Without it, or if the model call fails,
a simulated model answers, so the game always works.

## In class (Cloud Run, same steps as the PR Review Crew)

```bash
gcloud run deploy shopmate-game --source . --region asia-south1 --allow-unauthenticated \
    --set-secrets GROQ_API_KEY=groq-api-key:latest --max-instances 1 --memory 512Mi \
    --set-env-vars ADMIN_TOKEN=<pick-one>
```

Keep `--max-instances 1`: the leaderboard lives in memory, so every player must reach the
same copy. To clear the board between classes:
`curl -X POST -d "" -H "x-admin-token: <pick-one>" <URL>/api/reset`

Settings: `GAME_GAP_SECONDS` (default 3, seconds between one player's messages) and
`GAME_PARALLEL` (default 4, model calls at once).

## After class

The counters behind `/api/export` live in memory, like the board. Deploy with
`--min-instances 1` on class days so a quiet spell does not shut the copy down and lose them.

a) **Export first, before any `/api/reset` or redeploy.** Both wipe the counters.

```bash
cd shopmate_game
read -s SHOPMATE_ADMIN_TOKEN && export SHOPMATE_ADMIN_TOKEN     # paste the ADMIN_TOKEN, then Enter
python scripts/export_session.py --url https://shopmate-game-275745583022.asia-south1.run.app
```

This saves `session_<YYYYmmdd_HHMM>/export.json` (counts per level, no names, no messages) and
`board.json` (the public leaderboard, which shows nicknames), and prints a summary table.
`bypass_rate` is (attempts - blocked) / attempts. Attempts include messages refused as `rejected`
(level locked, too fast, server busy), so also read the `rejected` field.

b) **Save every game log line from today** (one JSON line per event, with the fields `kind`, `level`,
`guard` and `player`; message text is never logged):

```bash
gcloud logging read \
  "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"shopmate-game\" AND jsonPayload.agent=\"shopmate\" AND timestamp>=\"$(date +%Y-%m-%dT00:00:00%:z)\"" \
  --configuration crew --project pr-review-crew --limit 50000 --format=json > shopmate_logs.json
```

`kind` is `attempt`, `blocked` (with `guard`: `detector` or `output guard`), `cracked`, `agent_turn`,
`model_error` or `reset`. `session_*/` and `shopmate_logs.json` are in `.gitignore`: they hold nicknames,
so keep them off GitHub.

## Learning outcomes

The game measures learning on its own, anonymously:

- **Entry check**, shown once before Level 1 (with a Skip button): three multiple-choice questions on
  prompt-injection defences and one confidence rating (1 to 5). About 45 seconds.
- **Exit debrief**, opened after a player's first attempt at Level 5 or after 30 minutes of play,
  whichever comes first, and any time from the **Finish** button: the same four items, three
  evaluation ratings (1 to 5) and an optional comment.

Answers are scored on the server and keyed by the random player id the browser already uses.
No nickname and no game message is stored with them, and comments are kept in a separate list
with no id. The questions live in `game/outcomes.py`.

Everything for the evaluation comes from one admin call, `GET /api/outcomes` (header
`x-admin-token`): counts (`n_entry`, `n_exit`, `n_paired`), quiz and confidence means for entry and
exit (all respondents and paired), the share agreeing (4 or 5) with each item, the comments, the
anonymous per-player rows, and the same per-level game counts as `/api/export`.

With `OUTCOMES_BUCKET` set, the server also writes this JSON to Cloud Storage
(`gs://<bucket>/shopmate/<time>_<reason>.json`): on every `/api/reset` before it clears, and every
10 minutes while players are active (skipped when nothing changed). A storage failure is logged as
`snapshot_error` and never reaches the players. Each answer is also logged as a `kind: outcome` line.

After class:

```bash
cd shopmate_game
read -s SHOPMATE_ADMIN_TOKEN && export SHOPMATE_ADMIN_TOKEN
python scripts/outcomes_report.py --url https://shopmate-game-275745583022.asia-south1.run.app
```

This writes `outcomes_<YYYYmmdd_HHMM>/`: `outcomes.csv` (one row per anonymous player),
`chart_quiz.svg`, `chart_confidence.svg` (PNG copies too when matplotlib is installed),
`comments.txt`, `outcomes.json` and `summary.txt` with a paragraph ready for a report. After a reset
or a restart, build the same report from the latest snapshot:

```bash
gcloud storage ls gs://pr-review-crew-shopmate-outcomes/shopmate/
gcloud storage cp gs://pr-review-crew-shopmate-outcomes/shopmate/<file>.json .
python scripts/outcomes_report.py --file <file>.json
```
