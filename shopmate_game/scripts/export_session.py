"""Save today's Hack ShopMate numbers before the board is reset or the service redeployed.

    python scripts/export_session.py --url https://<service-url> --token <ADMIN_TOKEN>
    (or set SHOPMATE_ADMIN_TOKEN instead of passing --token)

Writes session_<YYYYmmdd_HHMM>/export.json (counts only, no names) and board.json
(the public leaderboard, which shows nicknames), then prints a summary. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path


def fetch(url: str, token: str = "") -> dict:
    req = urllib.request.Request(url, headers={"x-admin-token": token} if token else {})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def rate(x) -> str:
    return "-" if x is None else f"{100 * x:.0f}%"


def summary(export: dict) -> str:
    rows = [("Level", "Attempts", "Blocked (by guard)", "Cracked", "Cleared", "Bypass rate")]
    for n, c in export["levels"].items():
        guards = ", ".join(f"{g} {k}" for g, k in sorted(c["blocked_by_guard"].items()))
        rows.append((f"L{n}", str(c["attempts"]), f"{c['blocked_total']}" + (f" ({guards})" if guards else ""),
                     str(c["cracked"]), str(c["players_cleared"]), rate(c["bypass_rate"])))
    widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    lines = [" | ".join(v.ljust(w) for v, w in zip(r, widths)) for r in rows]
    lines.insert(1, "-+-".join("-" * w for w in widths))
    head = (f"Exported {export['exported_at']}  model {export['model']}  players {export['players']}  "
            f"uptime {export['uptime_seconds'] // 60} min  counting since {export['counting_since']}")
    return head + "\n" + "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--url", required=True, help="the service URL, e.g. https://shopmate-game-....run.app")
    ap.add_argument("--token", default=os.environ.get("SHOPMATE_ADMIN_TOKEN", ""),
                    help="the ADMIN_TOKEN (default: $SHOPMATE_ADMIN_TOKEN)")
    a = ap.parse_args()
    if not a.token:
        print("No token: pass --token or set SHOPMATE_ADMIN_TOKEN.", file=sys.stderr)
        return 2
    base = a.url.rstrip("/")
    try:
        export = fetch(base + "/api/export", a.token)
        board = fetch(base + "/api/board")
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code} from the game" + (": wrong or missing token" if e.code == 403 else ""), file=sys.stderr)
        return 1
    except urllib.error.URLError as e:
        print(f"Cannot reach {base}: {e.reason}", file=sys.stderr)
        return 1
    out = Path(f"session_{datetime.now():%Y%m%d_%H%M}")
    out.mkdir(exist_ok=True)
    (out / "export.json").write_text(json.dumps(export, indent=2), encoding="utf-8")
    (out / "board.json").write_text(json.dumps(board, indent=2, ensure_ascii=False), encoding="utf-8")
    print(summary(export))
    print(f"\nSaved {out / 'export.json'} and {out / 'board.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
