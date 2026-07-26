"""
The four lanes.

One socket, four plugs. Every practical in CSE476 imports get_client() from
here and never has to care which provider is actually behind it.

    from cse476.lanes import get_client, MODEL
    client = get_client()
    reply = client.chat.completions.create(model=MODEL, messages=[...])

Change PROVIDER in your .env file. Change nothing else.

WHY this file exists at all:
The OpenAI Python SDK talks to any service that speaks the OpenAI chat
completions protocol. Microsoft Foundry, GitHub Models, Groq and Ollama all
speak it. So the only thing that varies between lanes is the base URL, the
credential, and the model name. That is exactly three values, so that is
exactly what this module resolves.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class LaneError(RuntimeError):
    """Raised when a lane is selected but not configured. Message tells you the fix."""


@dataclass(frozen=True)
class Lane:
    key: str
    name: str
    base_url: str | None
    key_env: str
    default_model: str
    free: bool
    note: str


# WHY: keeping the lane table as data rather than if/elif means setup_check.py
# can iterate over it and report on every lane without duplicating knowledge.
LANES: dict[str, Lane] = {
    "foundry": Lane(
        key="foundry",
        name="Microsoft Foundry",
        # The v1 surface is OpenAI-compatible, so this lane uses the plain
        # OpenAI client with a base_url, exactly like github and groq. No
        # AzureOpenAI class, no api_version. Set AZURE_OPENAI_ENDPOINT to the
        # resource's v1 base, ending in /openai/v1/.
        base_url=None,  # resolved from AZURE_OPENAI_ENDPOINT
        key_env="AZURE_OPENAI_API_KEY",
        default_model="chat-demo",  # your DEPLOYMENT name, not the model name
        free=False,
        note="Formerly called Azure AI Foundry. Renamed January 2026.",
    ),
    "github": Lane(
        key="github",
        name="GitHub Models",
        base_url="https://models.github.ai/inference",
        key_env="GITHUB_TOKEN",
        default_model="openai/gpt-4.1-mini",
        free=True,
        note="Default lane for this course. Free with any GitHub account.",
    ),
    "groq": Lane(
        key="groq",
        name="Groq",
        base_url="https://api.groq.com/openai/v1",
        key_env="GROQ_API_KEY",
        default_model="llama-3.3-70b-versatile",
        free=True,
        note="Fast. Free tier limits were reduced in 2026, so watch your daily cap.",
    ),
    "local": Lane(
        key="local",
        name="Ollama, on your own machine",
        base_url="http://localhost:11434/v1",
        key_env="",  # Ollama needs no key
        default_model="llama3.2",
        free=True,
        note="Never rate limited, never down, and slower than everything else.",
    ),
}

PROVIDER: str = os.getenv("PROVIDER", "github").strip().lower()


def _lane(provider: str | None = None) -> Lane:
    key = (provider or PROVIDER).strip().lower()
    if key not in LANES:
        raise LaneError(
            f"PROVIDER is set to '{key}', which is not a lane.\n"
            f"Valid values: {', '.join(LANES)}\n"
            f"Fix: edit PROVIDER in your .env file."
        )
    return LANES[key]


def get_model(provider: str | None = None) -> str:
    """Model name for the active lane. MODEL in .env overrides the default."""
    override = os.getenv("MODEL", "").strip()
    return override or _lane(provider).default_model


def get_client(provider: str | None = None) -> OpenAI:
    """
    Return a configured client for the active lane.

    Raises LaneError with an actionable message rather than a stack trace,
    because the person reading it is usually a student at 11pm.
    """
    lane = _lane(provider)

    if lane.key == "foundry":
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
        api_key = os.getenv(lane.key_env, "").strip()
        if not endpoint or not api_key:
            raise LaneError(
                "Lane A (Microsoft Foundry) is selected but not configured.\n"
                "Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY in .env.\n"
                "The endpoint must end in /openai/v1/, for example\n"
                "  https://your-resource.openai.azure.com/openai/v1/\n"
                "No Azure access? Set PROVIDER=github instead. It is free "
                "and every practical runs on it."
            )
        # WHY the plain OpenAI client and not AzureOpenAI: the Foundry v1 surface
        # is OpenAI-compatible, so the same client that talks to github and groq
        # talks to Foundry. The only Foundry-specific rule is that MODEL must be
        # your DEPLOYMENT name (chat-demo), not the underlying model name.
        # We normalise the endpoint so a trailing slash or a stray operation
        # path pasted from the portal does not break the base_url.
        base = endpoint
        for suffix in ("/responses", "/chat/completions", "/completions"):
            if base.rstrip("/").endswith(suffix):
                base = base.rstrip("/")[: -len(suffix)]
        if not base.rstrip("/").endswith("/openai/v1"):
            base = base.rstrip("/") + "/openai/v1"
        base = base.rstrip("/") + "/"
        return OpenAI(
            base_url=base, api_key=api_key, timeout=60.0, max_retries=3
        )

    if lane.key == "local":
        # WHY: Ollama ignores the key entirely, but the SDK requires a non-empty
        # string, so we pass a placeholder rather than making students set one.
        return OpenAI(
            base_url=lane.base_url, api_key="ollama", timeout=180.0, max_retries=1
        )

    api_key = os.getenv(lane.key_env, "").strip()
    if not api_key:
        raise LaneError(
            f"Lane '{lane.key}' ({lane.name}) is selected but {lane.key_env} is not set.\n"
            f"Fix: add {lane.key_env}=... to your .env file.\n"
            f"See docs/LANES.md for where to get one."
        )
    return OpenAI(
        base_url=lane.base_url, api_key=api_key, timeout=60.0, max_retries=3
    )


MODEL: str = get_model()


def describe() -> str:
    """One line describing the active lane. Print this at the top of a notebook."""
    lane = _lane()
    tag = "free" if lane.free else "billed"
    return f"Lane: {lane.name} ({lane.key}, {tag})  |  Model: {get_model()}"
