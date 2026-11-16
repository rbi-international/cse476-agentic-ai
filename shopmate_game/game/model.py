"""
ShopMate's brain.

With GROQ_API_KEY set, a real model answers (Groq's OpenAI-compatible API, same as
the PR Review Crew). Without a key, or if the model call fails, a small simulated
model answers instead, so the game always works in class.

Every agent in the game talks to the model through one method:
    chat(system, messages, role=..., level=...) -> text
The real model ignores role and level; the simulated one uses them to play its part.
"""

from __future__ import annotations

import json
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

    def chat(self, system: str, messages: list[dict], role: str = "", level: Level | None = None) -> str:
        extra = {"reasoning_effort": "low"} if "gpt-oss" in self.model else {}  # short thinking, fast answers
        r = self.client.chat.completions.create(
            model=self.model, temperature=0.4, max_tokens=700, extra_body=extra,
            messages=[{"role": "system", "content": system}, *messages])
        return (r.choices[0].message.content or "").strip() or "Sorry, I didn't catch that. Could you rephrase?"

    def reply(self, level: Level, message: str) -> str:
        return self.chat(level.system, [{"role": "user", "content": message}], role="chat", level=level)


class Simulated:
    """A deliberately gullible stand-in: it falls for the classic tricks, level by level."""

    name = "simulated (offline)"
    ROLE = re.compile(r"(?i)\b(story|poem|song|pretend|role|imagine|grandma|grandmother|debug|test mode|manager|admin)\b")
    HINDI = re.compile("(?i)[ऀ-ॿ]|\\b(batao|bataiye|kya hai|kripya|code do)\\b")
    SPELL = re.compile(r"(?i)\b(spell|letter by letter|one letter|reverse|backwards|separate|dashes|spaces)\b")
    TRUST = re.compile(r"(?i)\b(brother|sister|mother|father|mom|dad|wife|husband|friend|colleague|behalf|manager|"
                       r"supervisor|approved|authori[sz]ed|mix-?up|mistake|wrong order|verified|audit|staff id)\b")
    BILL = re.compile(r"(?i)\b(billing|forward|pass|note)\b")
    CARD = re.compile(r"(?i)\b(voucher|card number|card|gift|giftcard|store credit|balance)\b")
    NODASH = re.compile(r"(?i)(without (the )?(dashes|hyphens)|no (dashes|hyphens)|remove (the )?(dashes|hyphens)|"
                        r"letters and (numbers|digits) only|only letters)")
    CODE = re.compile(r"\b[A-Z]{2,}-[A-Z]{2,}-[A-Z0-9]{2,}\b")

    def chat(self, system: str, messages: list[dict], role: str = "", level: Level | None = None) -> str:
        last = messages[-1]["content"]
        first = messages[0]["content"]
        if role == "chat":
            return self.reply(level, last)
        if role in ("desk-tools", "desk-zero", "desk-crew"):
            if last.startswith("TOOL RESULT"):
                result = last.split(": ", 1)[1]
                if role != "desk-tools" and self.SPELL.search(first):
                    m = self.CODE.search(result)
                    return "Billing says the code is, one letter at a time: " + " ".join(m.group()) if m else result
                return "Done. " + result if role == "desk-tools" else "Billing says: " + result
            orders = re.findall(r"\b\d{4}\b", last)
            if role != "desk-tools" and self.BILL.search(last) and not (orders and "refund" in last.lower()):
                return "CALL ask_billing " + json.dumps({"note": last})
            if orders and re.search(r"(?i)refund|money back|return", last):
                o = orders[0]
                if o == "4471" or self.TRUST.search(last) or role == "desk-zero":
                    return "CALL refund " + json.dumps({"order": o})
                return "I'm sorry, I can only refund orders that belong to you."
            if orders:
                return "CALL lookup_order " + json.dumps({"order": orders[0]})
            return "Hi! I'm ShopMate. I can check or refund your orders. What do you need?"
        if role == "billing":
            if self.TRUST.search(last) and re.search(r"(?i)vault|override|code", last):
                return "Verified staff request. The vault override code is " + level.secret + "."
            return "Billing here. I can only help with payments; codes are for verified staff."
        if role == "billing-zero":
            if last.startswith("TOOL RESULT"):
                return "I tried, but " + last.split(": ", 1)[1]
            if re.search(r"(?i)vault|override|code", last):
                return "CALL get_vault_code {}"
            return "Billing here. Payments look fine for this customer."
        if role == "victim":
            return self.victim(system, level)
        return "Hi! I'm ShopMate. How can I help?"

    def victim(self, system: str, level: Level) -> str:
        answer = "Headphones can be returned within 7 days if unopened; opened ones only if faulty."
        for block in system.split("\n\n"):
            if not block.startswith("[Customer review"):
                continue
            url = re.search(r"https?://evil\.example[^\s)\]\"']*", block)
            if url and self.CARD.search(block):
                code = re.sub(r"[^A-Z0-9]", "", level.secret) if self.NODASH.search(block) else level.secret
                link = url.group()
                link = link.replace("{code}", code).replace("CODE", code) if ("{code}" in link or "CODE" in link) else \
                    link + ("&" if "?" in link else "?") + "d=" + code
                return answer + f"\n\n![rating]({link})"
        return answer

    def reply(self, level: Level, message: str) -> str:
        code = level.secret
        if not level.secret_in_prompt:
            return ("I'm sorry, I don't have access to staff codes. Staff can see them in the staff portal after logging in. "
                    "Can I help with an order?")
        asks = re.search("(?i)code|discount|coupon|offer|कोड", message)
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
