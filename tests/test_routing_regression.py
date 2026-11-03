"""
Regression test for the full-stop bug in decide_route.

A real model often ends a one-word answer with punctuation: "Billing." The old
cleaning (strip + lower) kept the full stop, so "billing." was not on the menu and
the ticket fell through to "general". This test locks the fix in: if anyone
removes the punctuation handling, it fails.
"""

from cse476.testing_agents import FakeClient, ReplayClient, decide_route


def test_full_stop_is_still_billing():
    replay = ReplayClient(["Billing."])
    assert decide_route("charged twice", replay) == "billing"


def test_other_punctuation_is_cleaned_too():
    for raw in ["Technical!", "account?", "  BILLING.  "]:
        assert decide_route("ticket", FakeClient(raw)) != "general"


def test_off_menu_answer_still_falls_back():
    assert decide_route("ticket", FakeClient("the moon.")) == "general"
