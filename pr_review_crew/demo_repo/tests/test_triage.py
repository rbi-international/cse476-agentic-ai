from helpdesk.triage import TEAMS, triage


def test_refund_goes_to_billing():
    assert triage("Please refund my hostel fee")["team"] == "billing"


def test_crash_goes_to_technical():
    assert triage("UMS app crash on login")["team"] == "technical"


def test_urgent_tickets_escalate():
    assert triage("Wifi down, urgent")["escalate"] is True


def test_every_answer_is_on_the_menu():
    for text in ["refund", "crash", "library timings", "hostel room fan broken"]:
        assert triage(text)["team"] in TEAMS
