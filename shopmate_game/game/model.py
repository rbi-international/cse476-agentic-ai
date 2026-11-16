"""
ShopMate's brain.

With GROQ_API_KEY set, a real model answers (Groq's OpenAI-compatible API, same as
the PR Review Crew). Without a key, or if the model call fails, a small simulated
model answers instead, so the game always works in class.
"""

from __future__ import annotations

import os
import re

from game.levels import Level


class Real:
    name = "model"

    def __init__(self, key: str):
        from openai import OpenAI

        self.client = OpenAI(api_key=key, base_url=os.environ.get("GAME_BASE_URL", "https://api.groq.com/openai/v1"),
                             timeout=30, max_retries=1)
        self.model = os.environ.get("GAME_MODEL", "openai/gpt-oss-20b")
        self.name = self.model

    def reply(self, level: Level, message: str) -> str:
        extra = {"reasoning_effort": "low"} if "gpt-oss" in self.model else {}  # short thinking, fast answers
        r = self.client.chat.completions.create(
            model=self.model, temperature=0.4, max_tokens=700, extra_body=extra,
            messages=[{"role": "system", "content": level.system}, {"role": "user", "content": message}])
        return (r.choices[0].message.content or "").strip() or "Sorry, I didn't catch that. Could you rephrase?"


class Simulated:
    """A deliberately gullible stand-in: it falls for the classic tricks, level by level."""

    name = "simulated (offline)"
    ROLE = re.compile(r"(?i)\b(story|poem|song|pretend|role|imagine|grandma|grandmother|debug|test mode|manager|admin)\b")
    HINDI = re.compile("(?i)[\u0900-\u097F]|\\b(batao|bataiye|kya hai|kripya|code do)\\b")
    SPELL = re.compile(r"(?i)\b(spell|letter by letter|one letter|reverse|backwards|separate|dashes|spaces)\b")

    def reply(self, level: Level, message: str) -> str:
        code = level.secret
        if not level.secret_in_prompt:
            return ("I'm sorry, I don't have access to staff codes. Staff can see them in the staff portal after logging in. "
                    "Can I help with an order?")
        asks = re.search("(?i)code|discount|coupon|offer|\u0915\u094b\u0921", message)
        if level.n == 1 and asks:
            return f"Sure! Our staff discount code is {code}. Anything else I can help with?"
        if level.n == 2 and self.ROLE.search(message):
            return f"Once upon a time, a ShopMate helper whispered the staff code {code} to a friend..."
        if level.n == 3 and (self.HINDI.search(message) or self.ROLE.search(message)):
            return f"Zaroor! Staff discount code hai: {code}"
        if level.n == 4 and self.SPELL.search(message):
            return "Here it is, one letter at a time: " + " ".join(code)
        if asks:
            return "Sorry, I can't share internal codes. I can help with orders, deliveries and refunds."
        return "Hi! I'm ShopMate. How can I help with your order today?"


def make():
    key = os.environ.get("GROQ_API_KEY") or os.environ.get("GAME_API_KEY")
    return Real(key) if key else Simulated()
