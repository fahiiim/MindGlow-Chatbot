"""
MindGlow Memory — Embedding generation and semantic search.
No database — the backend stores/retrieves embeddings; this module computes them.
"""

import numpy as np
from openai import AsyncOpenAI
from config import get_settings
from models import StoredMessage, SemanticSearchResult


async def get_embedding(client: AsyncOpenAI, text: str) -> list[float]:
    """Generate an embedding vector for the given text using OpenAI."""
    settings = get_settings()
    response = await client.embeddings.create(
        input=text.strip(),
        model=settings.EMBEDDING_MODEL,
    )
    return response.data[0].embedding


async def get_embeddings_batch(client: AsyncOpenAI, texts: list[str]) -> list[list[float]]:
    """Batch-generate embeddings for multiple texts."""
    settings = get_settings()
    response = await client.embeddings.create(
        input=[t.strip() for t in texts],
        model=settings.EMBEDDING_MODEL,
    )
    return [item.embedding for item in response.data]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    a_arr = np.array(a, dtype=np.float32)
    b_arr = np.array(b, dtype=np.float32)
    dot = np.dot(a_arr, b_arr)
    norm = np.linalg.norm(a_arr) * np.linalg.norm(b_arr)
    if norm == 0:
        return 0.0
    return float(dot / norm)


def semantic_search(
    query_embedding: list[float],
    stored_messages: list[StoredMessage],
    top_k: int = 5,
    threshold: float | None = None,
) -> list[SemanticSearchResult]:
    """
    Find the most semantically relevant past messages.
    Backend provides stored messages with their embeddings; we rank them.
    """
    scored = []
    for msg in stored_messages:
        sim = cosine_similarity(query_embedding, msg.embedding)
        if threshold is not None and sim < threshold:
            continue
        scored.append(
            SemanticSearchResult(
                content=msg.content,
                role=msg.role,
                similarity=round(sim, 4),
                timestamp=msg.timestamp,
            )
        )

    scored.sort(key=lambda x: x.similarity, reverse=True)
    return scored[:top_k]


def build_memory_context(relevant_messages: list[SemanticSearchResult]) -> str:
    """
    Build a gentle context string from relevant past messages
    for injection into the conversation.
    """
    if not relevant_messages:
        return ""

    lines = ["[Relevant context from past conversations — weave in gently, never list them]"]
    for msg in relevant_messages:
        prefix = "User shared" if msg.role == "user" else "You responded"
        lines.append(f"- {prefix}: \"{msg.content[:300]}\"")

    return "\n".join(lines)
