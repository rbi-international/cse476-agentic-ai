"""Route a support ticket to a team."""

TEAMS = ("billing", "technical", "general")
URGENT_WORDS = ("urgent", "asap", "immediately", "down")


def triage(text: str) -> dict:
    """Return the team for a ticket and whether it needs escalation.

    text: the ticket as the student typed it.
    """
    low = text.lower()
    if any(w in low for w in ("refund", "charged", "invoice", "fee")):
        team = "billing"
    elif any(w in low for w in ("error", "crash", "login", "bug")):
        team = "technical"
    else:
        team = "general"
    escalate = any(w in low for w in URGENT_WORDS)
    return {"team": team, "escalate": escalate}
