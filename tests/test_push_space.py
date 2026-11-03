"""Where a deploy goes: the token owner's own Space, unless SPACE_ID says otherwise."""

import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("push_space", Path(__file__).resolve().parents[1] / "deploy" / "push_space.py")
push_space = importlib.util.module_from_spec(spec)
spec.loader.exec_module(push_space)


def test_a_fork_deploys_to_its_owners_space():
    assert push_space.space_id("asha-2025") == "asha-2025/cse476-triage-live"


def test_space_id_can_be_overridden():
    assert push_space.space_id("asha-2025", "team7/demo") == "team7/demo"


def test_the_app_url_is_the_hf_space_address():
    assert push_space.app_url("rbi-international/cse476-triage-live") == "https://rbi-international-cse476-triage-live.hf.space"
    assert push_space.app_url("Asha_K/cse476-triage-live") == "https://asha-k-cse476-triage-live.hf.space"
