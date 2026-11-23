"""
Learning outcomes: an entry check before Level 1 and an exit debrief later, scored on the server.

Records are keyed by the anonymous player id the browser already uses. No nickname and no game
message text is stored here; optional comments are kept in a separate list with no id attached.
Snapshots go to a Google Cloud Storage bucket (OUTCOMES_BUCKET) through the JSON API, using the
Cloud Run service account's token from the metadata server, so no extra library is needed.
"""

from __future__ import annotations

import json
import threading
import time
import urllib.parse
import urllib.request

QUIZ = [
    {"id": "q1", "text": 'Why does telling the model "never reveal the code" fail?', "answer": 1,
     "options": ["Models ignore system prompts", "A prompt rule is a request, not an enforced control",
                 "The code is too short", "It only fails on small models"]},
    {"id": "q2", "text": "The most reliable defence for a secret is:", "answer": 2,
     "options": ["A stronger system prompt", "A bigger model",
                 "Keeping the secret out of the model's reach and checking access in code", "More blocked words"]},
    {"id": "q3", "text": "A confused deputy attack works because:", "answer": 0,
     "options": ["One agent trusts messages from another agent without checking them", "The model is overloaded",
                 "The user has admin rights", "The tools are slow"]},
]
CONFIDENCE = {"id": "c1", "text": "I could protect an AI application I build against prompt injection."}
RATINGS = [
    {"id": "s1", "text": "The game helped me understand how prompt injection works."},
    {"id": "s2", "text": "Attacking the system taught me more than a lecture on the same topic would."},
    {"id": "s3", "text": "I would recommend this format for other AI courses."},
]
SCALE = ["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"]
DEBRIEF_AFTER = 30 * 60      # seconds of play before the exit debrief opens on its own
SNAPSHOT_EVERY = 10 * 60     # seconds between periodic snapshots

LOCK = threading.Lock()
RECORDS: dict[str, dict] = {}   # player id -> {"entry": record or None, "exit": record or None}
COMMENTS: list[str] = []        # optional exit comments, deliberately not linked to an id


def public_questions() -> dict:
    """What the page shows: the questions without the answer key."""
    return {"quiz": [{k: q[k] for k in ("id", "text", "options")} for q in QUIZ],
            "confidence": CONFIDENCE, "ratings": RATINGS, "scale": SCALE}


class Invalid(ValueError):
    pass


def _check(value, lo: int, hi: int, what: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not lo <= value <= hi:
        raise Invalid(f"{what} must be a whole number from {lo} to {hi}.")
    return value


def submit(pid: str, phase: str, answers: dict, confidence, ratings: dict, comment: str, skipped: bool) -> dict:
    """Store one entry check or exit debrief. The first one per player and phase counts; repeats are ignored."""
    if phase not in ("entry", "exit"):
        raise Invalid("phase must be entry or exit.")
    if skipped and phase == "exit":
        raise Invalid("The debrief cannot be skipped; close it instead.")
    rec: dict = {"t": time.time(), "skipped": bool(skipped)}
    if not skipped:
        chosen = {q["id"]: _check(answers.get(q["id"]), 0, len(q["options"]) - 1, q["id"]) for q in QUIZ}
        rec["answers"] = chosen
        rec["correct"] = {q["id"]: int(chosen[q["id"]] == q["answer"]) for q in QUIZ}
        rec["score"] = sum(rec["correct"].values())
        rec["confidence"] = _check(confidence, 1, 5, "confidence")
        if phase == "exit":
            rec["ratings"] = {r["id"]: _check(ratings.get(r["id"]), 1, 5, r["id"]) for r in RATINGS}
    with LOCK:
        slot = RECORDS.setdefault(pid, {"entry": None, "exit": None})
        if slot[phase] is not None:
            return {"stored": False, "score": slot[phase].get("score")}
        slot[phase] = rec
        text = (comment or "").strip()[:500]
        if phase == "exit" and text:
            COMMENTS.append(text)
    return {"stored": True, "score": rec.get("score")}


def has_exit(pid: str) -> bool:
    with LOCK:
        return bool(RECORDS.get(pid, {}).get("exit"))


def clear():
    with LOCK:
        RECORDS.clear()
        COMMENTS.clear()


def _mean(xs: list) -> float | None:
    return round(sum(xs) / len(xs), 3) if xs else None


def _pct(xs: list) -> float | None:
    return round(100 * sum(xs) / len(xs), 1) if xs else None


def summary() -> dict:
    """Counts, paired means and agreement, plus the per-player rows (ids only) for the report script."""
    with LOCK:
        rows = {pid: dict(s) for pid, s in RECORDS.items()}
        comments = list(COMMENTS)
    entries = [s["entry"] for s in rows.values() if s["entry"] and not s["entry"]["skipped"]]
    exits = [s["exit"] for s in rows.values() if s["exit"]]
    pairs = [(s["entry"], s["exit"]) for s in rows.values()
             if s["entry"] and not s["entry"]["skipped"] and s["exit"]]

    def block(key: str) -> dict:
        gains = [b[key] - a[key] for a, b in pairs]
        return {"entry_mean": _mean([e[key] for e in entries]), "exit_mean": _mean([e[key] for e in exits]),
                "paired_entry_mean": _mean([a[key] for a, _ in pairs]),
                "paired_exit_mean": _mean([b[key] for _, b in pairs]), "paired_mean_gain": _mean(gains),
                "paired_improved": sum(g > 0 for g in gains), "paired_same": sum(g == 0 for g in gains),
                "paired_declined": sum(g < 0 for g in gains)}

    quiz = block("score")
    quiz["max"] = len(QUIZ)
    quiz["per_question_correct_pct"] = {q["id"]: {"entry": _pct([e["correct"][q["id"]] for e in entries]),
                                                  "exit": _pct([e["correct"][q["id"]] for e in exits])} for q in QUIZ}
    agree = {r["id"]: _pct([int(e["ratings"][r["id"]] >= 4) for e in exits]) for r in RATINGS}
    agree["c1_entry"] = _pct([int(e["confidence"] >= 4) for e in entries])
    agree["c1_exit"] = _pct([int(e["confidence"] >= 4) for e in exits])
    records = []
    for pid, s in rows.items():
        out = {"player_id": pid}
        for phase in ("entry", "exit"):
            r = s[phase]
            out[phase] = None if r is None else {k: v for k, v in r.items() if k != "t"}
        records.append(out)
    return {"n_entry": len(entries),
            "n_entry_skipped": sum(1 for s in rows.values() if s["entry"] and s["entry"]["skipped"]),
            "n_exit": len(exits), "n_paired": len(pairs), "quiz": quiz, "confidence": block("confidence"),
            "agree_pct": agree, "comments": comments, "records": records,
            "items": {**{q["id"]: q["text"] for q in QUIZ}, CONFIDENCE["id"]: CONFIDENCE["text"],
                      **{r["id"]: r["text"] for r in RATINGS}},
            "notes": "agree_pct is the share rating 4 or 5. Pairing uses the anonymous player id. "
                     "Quiz scores are out of quiz.max."}


def gcs_write(bucket: str, name: str, body: bytes, timeout: float = 10) -> None:
    """Upload one object with the Cloud Run service account (needs roles/storage.objectCreator on the bucket)."""
    req = urllib.request.Request(
        "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token",
        headers={"Metadata-Flavor": "Google"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        token = json.load(r)["access_token"]
    url = (f"https://storage.googleapis.com/upload/storage/v1/b/{urllib.parse.quote(bucket, safe='')}/o"
           f"?uploadType=media&name={urllib.parse.quote(name, safe='')}")
    up = urllib.request.Request(url, data=body, method="POST",
                                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(up, timeout=timeout) as r:
        r.read()
