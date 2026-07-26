"""
Memory that persists, and retrieval that stops the model inventing facts.

Unit 3 Lecture 4. Your agent can act, but it still forgets between runs, and it
still answers from its own weights, which means it will confidently make things
up. Two fixes, both real.

First, memory: Agent Framework gives an agent a session, so a conversation
carries across turns without you rebuilding the transcript by hand. This is your
Unit 2 Session, now owned by the framework.

Second, retrieval augmented generation: instead of trusting the model to know a
fact, you search a pile of your own documents, pull the relevant pieces, and put
them in front of the model so it answers from them. This is the Knowledge panel
you saw on the Foundry tour, finally built for real.

    RagStore        chunk, embed, and search documents by meaning
    the embedder is pluggable, so retrieval mechanics test offline
    answer_with_context   the RAG shape: retrieve, then generate

The retrieval mechanics (chunking, cosine similarity, ranking) are ordinary
code and run with no model. Only the real embedding and the final answer need a
lane, exactly like the transport seam from Unit 2 Lecture 3.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Protocol


# ---------------------------------------------------------------- the embedder seam

class Embedder(Protocol):
    """
    Turns text into a vector of numbers. Real code uses a model. Tests use a
    simple deterministic function. Because RagStore depends on this Protocol and
    not on a specific model, the whole retrieval layer is testable offline, the
    same seam idea as the Transport in Unit 2 Lecture 3.
    """

    def embed(self, text: str) -> list[float]:
        ...


class HashingEmbedder:
    """
    A tiny, deterministic embedder for teaching and testing. It is NOT a real
    semantic embedder, it just maps words to fixed dimensions by hashing, so
    documents sharing words land near each other. Good enough to demonstrate how
    retrieval works, and it needs no model, no key, and no network.
    """

    def __init__(self, dims: int = 64):
        self.dims = dims

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dims
        for word in _tokenize(text):
            vec[hash(word) % self.dims] += 1.0
        return _normalize(vec)


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _normalize(vec: list[float]) -> list[float]:
    length = math.sqrt(sum(x * x for x in vec))
    if length == 0:
        return vec
    return [x / length for x in vec]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """
    How aligned two vectors are, from -1 to 1. This one number is the whole
    engine of semantic search: higher means more similar in meaning. You do not
    need a model to compute it, only the two vectors.
    """
    return sum(x * y for x, y in zip(a, b))  # inputs are already normalized


# ---------------------------------------------------------------- chunking

def chunk_text(text: str, max_words: int = 40) -> list[str]:
    """
    Split a document into pieces small enough to retrieve precisely.

    WHY chunk at all: if you embed a whole ten page document as one vector, a
    search matches the document as a blurry average, and you hand the model ten
    pages to find one sentence in. Chunking lets you retrieve the paragraph that
    actually answers the question, not the book it lives in.
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunk = " ".join(words[i : i + max_words])
        if chunk.strip():
            chunks.append(chunk)
    return chunks


# ---------------------------------------------------------------- the store

@dataclass
class Chunk:
    text: str
    source: str
    vector: list[float] = field(default_factory=list)


@dataclass
class RagStore:
    """
    A minimal retrieval store: hold chunks, embed them, and find the ones
    closest in meaning to a query.

    This is the beating heart of RAG, and it is small enough to read in one
    sitting. Real systems swap this for a vector database, but the idea is
    exactly this: embed everything once, then at question time embed the query
    and return the nearest chunks.
    """

    embedder: Embedder
    chunks: list[Chunk] = field(default_factory=list)

    def add_document(self, text: str, source: str, max_words: int = 40) -> int:
        """Chunk a document, embed each piece, and store it. Returns chunks added."""
        added = 0
        for piece in chunk_text(text, max_words=max_words):
            self.chunks.append(
                Chunk(text=piece, source=source, vector=self.embedder.embed(piece))
            )
            added += 1
        return added

    def search(self, query: str, top_k: int = 3) -> list[tuple[Chunk, float]]:
        """
        Return the top_k chunks most similar in meaning to the query.

        This is retrieval. Embed the query once, score every chunk by cosine
        similarity, sort, and take the best few. No model is involved in the
        search itself; the model only comes in afterwards, to write an answer
        from what we retrieved.
        """
        if not self.chunks:
            return []
        q = self.embedder.embed(query)
        scored = [(c, cosine_similarity(q, c.vector)) for c in self.chunks]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:top_k]

    def context_for(self, query: str, top_k: int = 3) -> str:
        """Assemble the retrieved chunks into a block to hand the model."""
        hits = self.search(query, top_k=top_k)
        if not hits:
            return "No relevant documents found."
        lines = []
        for chunk, score in hits:
            lines.append(f"[from {chunk.source}] {chunk.text}")
        return "\n\n".join(lines)


# ---------------------------------------------------------------- the RAG shape

RAG_INSTRUCTIONS = (
    "You answer using ONLY the provided context. If the context does not contain "
    "the answer, say you do not have that information. Do not use outside "
    "knowledge, and do not guess. Cite the source in brackets when you can."
)


def build_rag_prompt(question: str, context: str) -> str:
    """
    The prompt that turns retrieval into an answer.

    Notice the shape: the context comes first, then the question, then a strict
    instruction to answer only from the context. This is what stops the model
    inventing facts. It is not that the model became more truthful; it is that
    you gave it the facts and forbade it from using anything else.
    """
    return (
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        f"Answer using only the context above."
    )


async def answer_with_context(agent, store: RagStore, question: str, top_k: int = 3) -> str:
    """
    The full RAG call: retrieve, then generate. Needs a lane, because the final
    answer is a live model call. The retrieval before it is all offline.
    """
    context = store.context_for(question, top_k=top_k)
    prompt = build_rag_prompt(question, context)
    result = await agent.run(prompt)
    return str(result)


# ---------------------------------------------------------------- the real embedder

# In production you swap HashingEmbedder for a real semantic embedder built on
# the Agent Framework embedding client:
#
#     from agent_framework.openai import OpenAIEmbeddingClient
#     client = OpenAIEmbeddingClient(model=..., api_key=..., base_url=...)
#     vectors = await client.get_embeddings([text])
#
# get_embeddings is async and makes a live call, so the notebook wires it behind
# the same Embedder seam this module already uses. Nothing else in RagStore
# changes: real semantic search drops straight in where the toy embedder was.
# That is the whole point of the seam, the same lesson as the Transport in
# Unit 2 Lecture 3.
