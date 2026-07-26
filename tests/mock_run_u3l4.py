"""
Prove the retrieval mechanics work offline: chunking, embedding, cosine search,
ranking, and the RAG prompt shape. The real embedder and the final answer need
a lane; everything tested here runs with no model.
"""

import sys

sys.path.insert(0, "src")

from cse476.rag import (  # noqa: E402
    HashingEmbedder,
    RagStore,
    build_rag_prompt,
    chunk_text,
    cosine_similarity,
)

ok = True


def chk(label, cond):
    global ok
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
    ok = ok and cond


print("\n1. chunking splits a long document into pieces")
text = " ".join(f"word{i}" for i in range(100))
chunks = chunk_text(text, max_words=40)
chk("three chunks from 100 words at 40 each", len(chunks) == 3)
chk("first chunk has 40 words", len(chunks[0].split()) == 40)
chk("last chunk has the remainder", len(chunks[2].split()) == 20)

print("\n2. chunking ignores empty input")
chk("empty text gives no chunks", chunk_text("   ") == [])

print("\n3. the embedder is deterministic")
e = HashingEmbedder()
chk("same text gives same vector", e.embed("hello world") == e.embed("hello world"))
chk("vector is normalized", abs(sum(x * x for x in e.embed("hello world")) - 1.0) < 1e-6)

print("\n4. cosine similarity behaves")
a = e.embed("billing refund invoice")
b = e.embed("billing refund invoice")
c = e.embed("weather sunny mumbai")
chk("identical text scores ~1", abs(cosine_similarity(a, b) - 1.0) < 1e-6)
chk("unrelated text scores lower", cosine_similarity(a, c) < cosine_similarity(a, b))

print("\n5. the store retrieves the right chunk by meaning")
store = RagStore(embedder=HashingEmbedder())
store.add_document(
    "The billing team handles refunds and invoice disputes. "
    "Billing SLA is 24 hours.",
    source="policy.md",
)
store.add_document(
    "The technical team handles outages and software bugs. "
    "Technical SLA is 4 hours.",
    source="policy.md",
)
hits = store.search("billing refunds invoice", top_k=1)
chk("returned a hit", len(hits) == 1)
chk("retrieved the billing chunk, not technical",
    "billing" in hits[0][0].text.lower())

print("\n6. search ranks by similarity, best first")
hits = store.search("refund invoice billing", top_k=2)
chk("two hits", len(hits) == 2)
chk("best hit is the billing chunk", "billing" in hits[0][0].text.lower())
chk("scores are in descending order", hits[0][1] >= hits[1][1])

print("\n7. an empty store returns nothing, safely")
empty = RagStore(embedder=HashingEmbedder())
chk("no hits from empty store", empty.search("anything") == [])
chk("context says so", "No relevant" in empty.context_for("anything"))

print("\n8. context_for assembles retrieved chunks with their sources")
ctx = store.context_for("refund", top_k=1)
chk("context names the source", "policy.md" in ctx)
chk("context includes the retrieved text", "billing" in ctx.lower())

print("\n9. the RAG prompt puts context first and forbids outside knowledge")
prompt = build_rag_prompt("What is the billing SLA?", "billing SLA is 24 hours")
chk("context is in the prompt", "24 hours" in prompt)
chk("question is in the prompt", "billing SLA" in prompt)
chk("instructs to use only the context", "only the context" in prompt.lower())

print("\n10. retrieval finds nothing relevant gracefully")
hits = store.search("quantum chromodynamics", top_k=1)
# it still returns the closest chunk, but the store never invents content
chk("returns at most top_k", len(hits) <= 1)
chk("the returned chunk is real stored text",
    hits[0][0].text in [c.text for c in store.chunks] if hits else True)

print("\n" + ("ALL PASS" if ok else "SOMETHING FAILED"))
sys.exit(0 if ok else 1)
