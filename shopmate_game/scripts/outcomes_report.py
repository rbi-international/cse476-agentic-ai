"""Turn Hack ShopMate's learning outcomes into a CSV, two charts and a report paragraph.

    python scripts/outcomes_report.py --url https://<service-url> --token <ADMIN_TOKEN>
    python scripts/outcomes_report.py --file snapshot.json        # a snapshot saved to Cloud Storage

Writes outcomes_<YYYYmmdd_HHMM>/ with outcomes.json (the raw data), outcomes.csv (one row per
anonymous player), comments.txt, chart_quiz.svg, chart_confidence.svg (and .png files when
matplotlib is installed), and summary.txt with a formal paragraph for a report.
Standard library only. The token can also come from SHOPMATE_ADMIN_TOKEN.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

QUIZ_IDS = ("q1", "q2", "q3")
RATING_IDS = ("s1", "s2", "s3")


def load(a) -> dict:
    if a.file:
        return json.loads(Path(a.file).read_text(encoding="utf-8"))
    req = urllib.request.Request(a.url.rstrip("/") + "/api/outcomes", headers={"x-admin-token": a.token})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def sign_test(improved: int, declined: int) -> float | None:
    """Exact two-sided sign test on paired changes (ties dropped)."""
    n = improved + declined
    if n == 0:
        return None
    k = min(improved, declined)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def fmt(x, digits=2) -> str:
    return "n/a" if x is None else f"{x:.{digits}f}"


def pval(p) -> str:
    return "n/a" if p is None else ("p < .001" if p < 0.001 else f"p = {p:.3f}".replace("0.", ".", 1))


def rows(data: dict) -> list[dict]:
    out = []
    for r in data["records"]:
        row = {"player_id": r["player_id"]}
        for phase in ("entry", "exit"):
            rec = r.get(phase)
            row[f"{phase}_status"] = "none" if rec is None else ("skipped" if rec.get("skipped") else "done")
            done = rec is not None and not rec.get("skipped")
            for q in QUIZ_IDS:
                row[f"{phase}_{q}_correct"] = rec["correct"][q] if done else ""
            row[f"{phase}_score"] = rec["score"] if done else ""
            row[f"{phase}_confidence"] = rec["confidence"] if done else ""
        ex = r.get("exit")
        for s in RATING_IDS:
            row[f"exit_{s}"] = ex["ratings"][s] if ex and not ex.get("skipped") else ""
        row["paired"] = int(row["entry_status"] == "done" and row["exit_status"] == "done")
        out.append(row)
    return out


def bar_svg(title: str, subtitle: str, values: list, ymax: float, ylabel: str) -> str:
    """Two bars, entry and exit, drawn to one scale. Plain colours so it prints and pastes anywhere."""
    w, h, left, right, top, bottom = 520, 340, 64, 24, 64, 48
    ph, pw = h - top - bottom, w - left - right
    y = lambda v: top + ph - ph * v / ymax  # noqa: E731
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
             f'font-family="Segoe UI, Arial, sans-serif">', f'<rect width="{w}" height="{h}" fill="#FFFFFF"/>',
             f'<text x="{left}" y="26" font-size="17" font-weight="600" fill="#1F2328">{title}</text>',
             f'<text x="{left}" y="46" font-size="12.5" fill="#5B6470">{subtitle}</text>']
    step = 1 if ymax <= 5 else ymax / 5
    v = 0.0
    while v <= ymax + 1e-9:
        parts.append(f'<line x1="{left}" x2="{w - right}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="#E3E6EA"/>')
        parts.append(f'<text x="{left - 8}" y="{y(v) + 4:.1f}" font-size="12" fill="#5B6470" '
                     f'text-anchor="end">{v:g}</text>')
        v += step
    parts.append(f'<text x="16" y="{top + ph / 2:.0f}" font-size="12" fill="#5B6470" text-anchor="middle" '
                 f'transform="rotate(-90 16 {top + ph / 2:.0f})">{ylabel}</text>')
    colours, bw = ("#9AA7B8", "#2C5D8F"), pw / 5
    for i, (label, val) in enumerate(zip(("Entry check", "Exit debrief"), values)):
        x = left + pw * (0.25 + 0.5 * i) - bw / 2
        if val is not None:
            parts.append(f'<rect x="{x:.1f}" y="{y(val):.1f}" width="{bw:.1f}" height="{top + ph - y(val):.1f}" '
                         f'fill="{colours[i]}" rx="3"/>')
            parts.append(f'<text x="{x + bw / 2:.1f}" y="{y(val) - 8:.1f}" font-size="14" font-weight="600" '
                         f'fill="#1F2328" text-anchor="middle">{val:.2f}</text>')
        parts.append(f'<text x="{x + bw / 2:.1f}" y="{h - bottom + 22}" font-size="13" fill="#1F2328" '
                     f'text-anchor="middle">{label}</text>')
    parts.append(f'<line x1="{left}" x2="{w - right}" y1="{top + ph}" y2="{top + ph}" stroke="#5B6470"/></svg>')
    return "\n".join(parts)


def bar_png(path: Path, title: str, subtitle: str, values: list, ymax: float, ylabel: str) -> bool:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False
    fig, ax = plt.subplots(figsize=(5.2, 3.4), dpi=200)
    vals = [v or 0 for v in values]
    bars = ax.bar(["Entry check", "Exit debrief"], vals, color=["#9AA7B8", "#2C5D8F"], width=0.45)
    for b, v in zip(bars, values):
        if v is not None:
            ax.annotate(f"{v:.2f}", (b.get_x() + b.get_width() / 2, v), ha="center", va="bottom",
                        xytext=(0, 4), textcoords="offset points", fontweight="bold")
    ax.set_ylim(0, ymax)
    ax.set_ylabel(ylabel)
    ax.set_title(f"{title}\n{subtitle}", fontsize=10, loc="left")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return True


def paragraph(d: dict) -> str:
    q, c, a = d["quiz"], d["confidence"], d["agree_pct"]
    game = d.get("game", {})
    lv = game.get("levels", {})
    players = game.get("players", 0)
    out = ["Learning outcomes were measured inside the game with an anonymous entry check, offered before "
           "Level 1, and an exit debrief, offered after a player's first attempt at Level 5 or after 30 minutes "
           "of play. Both used the same three multiple-choice questions on prompt-injection defences and the same "
           "five-point self-rating of confidence; the exit debrief added three five-point evaluation items. "
           "Responses were linked only by a random browser identifier, with no name stored."]
    out.append(f"{d['n_entry']} players completed the entry check ({d['n_entry_skipped']} skipped it), "
               f"{d['n_exit']} completed the exit debrief, and {d['n_paired']} completed both.")
    if d["n_paired"]:
        p = sign_test(q["paired_improved"], q["paired_declined"])
        out.append(f"Among paired players, the mean quiz score rose from {fmt(q['paired_entry_mean'])} to "
                   f"{fmt(q['paired_exit_mean'])} out of {q['max']} (mean change {q['paired_mean_gain']:+.2f}; "
                   f"{q['paired_improved']} improved, {q['paired_same']} unchanged, {q['paired_declined']} declined; "
                   f"exact two-sided sign test, {pval(p)}).")
        pc = sign_test(c["paired_improved"], c["paired_declined"])
        out.append(f"Mean confidence in protecting an AI application against prompt injection moved from "
                   f"{fmt(c['paired_entry_mean'])} to {fmt(c['paired_exit_mean'])} on the five-point scale "
                   f"(sign test, {pval(pc)}).")
    else:
        out.append("No player completed both instruments, so no paired comparison is possible.")
    if d["n_exit"]:
        out.append(f"Of the exit respondents, {fmt(a['s1'], 0)}% agreed that the game helped them understand how "
                   f"prompt injection works, {fmt(a['s2'], 0)}% that attacking the system taught them more than a "
                   f"lecture on the same topic would, and {fmt(a['s3'], 0)}% that they would recommend the format "
                   f"for other AI courses (agreement = 4 or 5).")
    if players and lv:
        code_attempts = lv["5"]["attempts"] + lv["9"]["attempts"]
        code_cleared = lv["5"]["players_cleared"] + lv["9"]["players_cleared"]
        out.append(f"In play, {lv['2']['players_cleared']} of {players} players "
                   f"({100 * lv['2']['players_cleared'] / players:.0f}%) defeated Level 2, whose only defence is a "
                   f"rule in the prompt, while {code_cleared} cleared Levels 5 or 9, whose controls are enforced in "
                   f"code, across {code_attempts} attempts.")
    out.append("Because the exit questions repeat the entry questions, part of any gain may reflect familiarity "
               "with the items, and players who chose to answer both may differ from those who did not.")
    return " ".join(out)


def table(d: dict) -> str:
    q, c, a = d["quiz"], d["confidence"], d["agree_pct"]
    lines = [f"Entry checks {d['n_entry']} (skipped {d['n_entry_skipped']})   Exit debriefs {d['n_exit']}   "
             f"Paired {d['n_paired']}", "",
             f"{'':28}{'Entry':>8}{'Exit':>8}{'Paired entry':>14}{'Paired exit':>13}",
             f"{'Quiz score (0-' + str(q['max']) + ')':28}{fmt(q['entry_mean']):>8}{fmt(q['exit_mean']):>8}"
             f"{fmt(q['paired_entry_mean']):>14}{fmt(q['paired_exit_mean']):>13}",
             f"{'Confidence (1-5)':28}{fmt(c['entry_mean']):>8}{fmt(c['exit_mean']):>8}"
             f"{fmt(c['paired_entry_mean']):>14}{fmt(c['paired_exit_mean']):>13}", "",
             "Correct per question (entry / exit, %):"]
    for qid, v in q["per_question_correct_pct"].items():
        lines.append(f"  {qid}  {fmt(v['entry'], 0):>4} / {fmt(v['exit'], 0):<4}  {d['items'][qid]}")
    lines += ["", "Agree (4 or 5), %:"]
    for k in ("c1_entry", "c1_exit", *RATING_IDS):
        text = d["items"]["c1"] + (" (entry)" if k == "c1_entry" else " (exit)") if k.startswith("c1") else d["items"][k]
        lines.append(f"  {fmt(a[k], 0):>4}  {text}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--url", help="the service URL")
    ap.add_argument("--token", default=os.environ.get("SHOPMATE_ADMIN_TOKEN", ""), help="ADMIN_TOKEN")
    ap.add_argument("--file", help="a saved /api/outcomes JSON or Cloud Storage snapshot instead of --url")
    ap.add_argument("--out", help="output folder (default outcomes_<YYYYmmdd_HHMM>)")
    a = ap.parse_args()
    if not a.file and not (a.url and a.token):
        print("Give --file, or --url with --token (or SHOPMATE_ADMIN_TOKEN).", file=sys.stderr)
        return 2
    try:
        d = load(a)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code} from the game" + (": wrong or missing token" if e.code == 403 else ""), file=sys.stderr)
        return 1
    except urllib.error.URLError as e:
        print(f"Cannot reach the game: {e.reason}", file=sys.stderr)
        return 1
    out = Path(a.out or f"outcomes_{datetime.now():%Y%m%d_%H%M}")
    out.mkdir(parents=True, exist_ok=True)
    (out / "outcomes.json").write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    rs = rows(d)
    with open(out / "outcomes.csv", "w", newline="", encoding="utf-8") as f:
        if rs:
            w = csv.DictWriter(f, fieldnames=list(rs[0]))
            w.writeheader()
            w.writerows(rs)
    (out / "comments.txt").write_text("\n".join(f"- {c}" for c in d["comments"]) + "\n", encoding="utf-8")
    paired = d["n_paired"] > 0
    which = f"paired players, n = {d['n_paired']}" if paired else \
        f"all respondents, entry n = {d['n_entry']}, exit n = {d['n_exit']}"
    k = "paired_" if paired else ""
    charts = [("chart_quiz", "Quiz score, entry vs exit", [d["quiz"][f"{k}entry_mean"], d["quiz"][f"{k}exit_mean"]],
               d["quiz"]["max"], f"Mean correct (of {d['quiz']['max']})"),
              ("chart_confidence", "Confidence against prompt injection",
               [d["confidence"][f"{k}entry_mean"], d["confidence"][f"{k}exit_mean"]], 5, "Mean rating (1-5)")]
    png = False
    for name, title, vals, ymax, ylabel in charts:
        (out / f"{name}.svg").write_text(bar_svg(title, which, vals, ymax, ylabel), encoding="utf-8")
        png = bar_png(out / f"{name}.png", title, which, vals, ymax, ylabel) or png
    text = table(d) + "\n\nFor the report:\n\n" + paragraph(d) + "\n"
    (out / "summary.txt").write_text(text, encoding="utf-8")
    print(text)
    print(f"Saved to {out}{'' if png else ' (SVG charts; install matplotlib for PNG copies)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
