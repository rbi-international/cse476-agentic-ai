"""
The model behind the agents.

Groq's OpenAI-compatible endpoint by default (free key at console.groq.com/keys).
Any OpenAI-compatible server works: set CREW_BASE_URL and CREW_MODEL.
No key means offline mode: every agent falls back to its deterministic tools.
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass


@dataclass
class Reply:
    text: str
    ms: float
    tokens: int


class LLM:
    """A thin chat client. One method: ask(system, user) -> Reply."""

    def __init__(self, api_key: str, model: str, base_url: str):
        from openai import OpenAI  # imported here so offline mode needs no package

        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=60, max_retries=2)
        self.model = model

    def ask(self, system: str, user: str, max_tokens: int = 900) -> Reply:
        start = time.perf_counter()
        r = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            max_tokens=max_tokens,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        )
        ms = (time.perf_counter() - start) * 1000
        tokens = getattr(r.usage, "total_tokens", 0) if r.usage else 0
        return Reply(r.choices[0].message.content or "", round(ms, 1), tokens)


def from_env() -> LLM | None:
    """The configured model, or None for offline mode."""
    key = os.environ.get("GROQ_API_KEY") or os.environ.get("CREW_API_KEY")
    if not key:
        return None
    return LLM(
        api_key=key,
        model=os.environ.get("CREW_MODEL", "openai/gpt-oss-20b"),
        base_url=os.environ.get("CREW_BASE_URL", "https://api.groq.com/openai/v1"),
    )


def parse_json(text: str) -> dict:
    """The first JSON object in a model reply, or {} if there is none.

    Models wrap JSON in prose or code fences; we never trust the shape, we look for it.
    """
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return {}
    try:
        value = json.loads(m.group(0))
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}
