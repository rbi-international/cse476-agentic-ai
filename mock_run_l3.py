"""
Prove the transcript maths and the three trimming strategies, offline.
"""

import sys

sys.path.insert(0, "src")

from cse476.conversation import (  # noqa: E402
    count_tokens,
    message_tokens,
    pin,
    simulate_cost,
    sliding_window,
    sliding_window_with_pins,
    summarise_older,
    tokenizer_is_exact,
    transcript_tokens,
)

ok = True


def chk(label, cond):
    global ok
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
    ok = ok and cond


print(f"\ntokenizer exact: {tokenizer_is_exact()}")

print("\n1. counting")
chk("empty string still costs something", count_tokens("") >= 1)
chk("longer text costs more", count_tokens("a" * 400) > count_tokens("a" * 40))
m = {"role": "user", "content": "Rooms at Taj Palace on 2026-08-14?"}
chk("message costs more than its bare text", message_tokens(m) > count_tokens(m["content"]))

print("\n2. the transcript is resent, so cost compounds")
rows = simulate_cost([50] * 10, system_tokens=100)
chk("first request is small", rows[0].sent == 150)
chk("tenth request is much larger", rows[-1].sent == 600)
chk("tenth turn sends 4x the first", rows[-1].sent == 4 * rows[0].sent)
linear = sum(r.new for r in rows) + 100
chk(
    f"cumulative {rows[-1].cumulative} far exceeds linear {linear}",
    rows[-1].cumulative > 5 * linear,
)

print("\n3. sliding window")
convo = [{"role": "system", "content": "You are a booking assistant."}]
for i in range(20):
    convo.append({"role": "user", "content": f"question number {i} about hotels"})
    convo.append({"role": "assistant", "content": f"answer number {i} about hotels"})

trimmed = sliding_window(convo, max_tokens=200)
chk("system message survived", trimmed[0]["role"] == "system")
chk("transcript shrank", len(trimmed) < len(convo))
chk("stayed inside the budget", transcript_tokens(trimmed) <= 200)
chk("kept the most recent turn", trimmed[-1]["content"] == convo[-1]["content"])
chk("dropped the oldest turn", convo[1] not in trimmed)

print("\n4. sliding window does not leave orphan tool messages")
tool_convo = [
    {"role": "system", "content": "sys"},
    {"role": "user", "content": "x" * 600},
    {
        "role": "assistant",
        "content": None,
        "tool_calls": [{"id": "c0", "type": "function",
                        "function": {"name": "get_rate", "arguments": "{}"}}],
    },
    {"role": "tool", "tool_call_id": "c0", "content": "Rs 6200"},
    {"role": "user", "content": "thanks"},
]
tight = sliding_window(tool_convo, max_tokens=60)
orphans = [
    m for m in tight
    if m.get("role") == "tool"
    and m.get("tool_call_id") not in {
        c["id"] for x in tight for c in (x.get("tool_calls") or [])
    }
]
chk("no orphaned tool message", orphans == [])

print("\n5. summarisation")
summarised = summarise_older(convo, keep_recent=4, summariser=lambda t: "user asked about hotels")
chk("much shorter than the original", len(summarised) < len(convo))
chk("a summary note was inserted", any("Summary of earlier" in (m.get("content") or "") for m in summarised))
chk("the last four turns are intact", summarised[-4:] == convo[-4:])
chk("cheaper than the original", transcript_tokens(summarised) < transcript_tokens(convo))

print("\n6. pinning survives aggressive trimming")
pinned_convo = [
    {"role": "system", "content": "sys"},
    pin({"role": "user", "content": "I am allergic to peanuts"}),
]
for i in range(30):
    pinned_convo.append({"role": "user", "content": f"filler question {i} " * 8})

kept = sliding_window_with_pins(pinned_convo, max_tokens=180)
chk("the pinned fact survived", any("peanuts" in (m.get("content") or "") for m in kept))
chk("still inside the budget", transcript_tokens(kept) <= 180)
chk("filler was dropped", len(kept) < len(pinned_convo))

print("\n7. a plain sliding window would have lost it")
naive = sliding_window(pinned_convo, max_tokens=180)
chk("plain window drops the allergy", not any("peanuts" in (m.get("content") or "") for m in naive))

print("\n" + ("ALL PASS" if ok else "SOMETHING FAILED"))
sys.exit(0 if ok else 1)
