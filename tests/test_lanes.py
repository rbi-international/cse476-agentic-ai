"""
Tests for the lane abstraction.

These run in CI with no API key of any kind. They check that the switch
resolves correctly and that a misconfigured lane fails with a message a
student can act on, rather than a stack trace.
"""

import pytest

from cse476.lanes import LANES, LaneError, _lane, describe, get_client, get_model


def test_every_lane_declares_what_it_needs():
    for key, lane in LANES.items():
        assert lane.key == key
        assert lane.name
        if key != "local":
            assert lane.key_env or key == "foundry"
        assert lane.default_model


def test_unknown_provider_names_the_valid_ones():
    with pytest.raises(LaneError) as e:
        _lane("azure-openai-v3")
    msg = str(e.value)
    assert "not a lane" in msg
    for key in LANES:
        if not LANES[key].retired:
            assert key in msg


def test_missing_credential_tells_you_the_variable(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(LaneError) as e:
        get_client("groq")
    assert "GROQ_API_KEY" in str(e.value)


def test_missing_foundry_config_offers_the_free_fallback(monkeypatch):
    monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)
    with pytest.raises(LaneError) as e:
        get_client("foundry")
    assert "PROVIDER=groq" in str(e.value)


def test_local_lane_needs_no_credential(monkeypatch):
    # WHY: Ollama ignores auth entirely. A student with nothing configured
    # must still be able to construct a client.
    client = get_client("local")
    assert "11434" in str(client.base_url)


def test_model_override_wins(monkeypatch):
    monkeypatch.setenv("MODEL", "some/other-model")
    assert get_model("groq") == "some/other-model"


def test_describe_is_one_line():
    assert "\n" not in describe()


def test_foundry_needs_endpoint_and_key(monkeypatch):
    monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)
    with pytest.raises(LaneError) as e:
        get_client("foundry")
    msg = str(e.value)
    assert "/openai/v1/" in msg
    assert "PROVIDER=groq" in msg


def test_foundry_normalises_a_messy_endpoint(monkeypatch):
    # WHY: users paste the /responses operation URL straight from the portal.
    # The lane must turn any plausible paste into a valid /openai/v1/ base.
    monkeypatch.setenv(
        "AZURE_OPENAI_ENDPOINT",
        "https://cse476-foundry.openai.azure.com/openai/v1/responses",
    )
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "fake-key-for-testing")
    client = get_client("foundry")
    assert str(client.base_url).endswith("/openai/v1/")
    assert "responses" not in str(client.base_url)


def test_foundry_bare_host_gets_the_v1_path(monkeypatch):
    monkeypatch.setenv(
        "AZURE_OPENAI_ENDPOINT", "https://cse476-foundry.openai.azure.com"
    )
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "fake-key-for-testing")
    client = get_client("foundry")
    assert str(client.base_url) == "https://cse476-foundry.openai.azure.com/openai/v1/"


def test_foundry_model_leaking_into_a_free_lane_is_caught(monkeypatch):
    # MODEL set for foundry, left behind after switching to a free lane, is the
    # single most common lane mistake. It must produce a clear error, not a 404.
    monkeypatch.setenv("PROVIDER", "groq")
    monkeypatch.setenv("MODEL", "chat-demo")
    with pytest.raises(LaneError) as exc:
        get_model("groq")
    msg = str(exc.value)
    assert "chat-demo" in msg
    assert "MODEL line" in msg or "unset" in msg or "delete" in msg


def test_a_valid_groq_override_is_allowed(monkeypatch):
    monkeypatch.setenv("PROVIDER", "groq")
    monkeypatch.setenv("MODEL", "llama-3.1-8b-instant")
    assert get_model("groq") == "llama-3.1-8b-instant"


def test_retired_github_lane_explains_the_migration():
    # GitHub Models was retired on 30 July 2026. Selecting it must give a clear
    # migration message pointing at the free replacements, not a raw 410.
    with pytest.raises(LaneError) as exc:
        _lane("github")
    msg = str(exc.value)
    assert "no longer available" in msg
    assert "groq" in msg and "local" in msg
