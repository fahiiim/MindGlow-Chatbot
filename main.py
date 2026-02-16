"""
MindGlow API — FastAPI application with endpoints for both chatbots.

Endpoints:
  POST /chat              — Main chat endpoint (Reflect or Inner Learning)
  POST /semantic-search   — Find relevant past messages by semantic similarity
  POST /summary           — Generate neutral session summary
  POST /embed             — Generate embedding for a text
  GET  /health            — Health check
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI

from config import get_settings
from models import (
    ChatRequest,
    ChatResponse,
    SemanticSearchRequest,
    SemanticSearchResponse,
    SummaryRequest,
    SummaryResponse,
)
from memory import get_embedding, semantic_search, build_memory_context
from chatbots import generate_response, generate_session_summary


# ─────────────────────────────────────────────────────────────────────────────
# App Lifespan — initialize OpenAI client once
# ─────────────────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    yield
    await app.state.openai_client.close()


app = FastAPI(
    title="MindGlow AI",
    description=(
        "Self-reflection AI system with two chatbots: "
        "**Reflect** (emotional exploration) and **Inner Learning** (Socratic discovery). "
        "No advice. No judgments. Just space to think."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _client() -> AsyncOpenAI:
    return app.state.openai_client


# ─────────────────────────────────────────────────────────────────────────────
# POST /chat — Main chat endpoint
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to either the Reflect or Inner Learning chatbot.

    **Backend integration:**
    - Send `user_info`, `message`, and `conversation_history` from your DB.
    - Optionally include `past_summaries` from stored session summaries.
    - The response includes `embedding`, `reply_embedding`, and `summary` —
      store these in your DB for future semantic search and continuity.
    - If `crisis_detected` is True, also store the event for safety team review.
    - If `response_was_filtered` is True, store `filter_log` for review.
    """
    client = _client()

    # Optional: if backend sends stored messages for semantic search in the request,
    # we could do it here. For now, the /semantic-search endpoint is separate,
    # and the backend can call it first to get memory_context.

    try:
        chat_response, filter_log_entry, crisis_log_entry = await generate_response(
            client=client,
            request=request,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation error: {str(e)}")

    return chat_response


# ─────────────────────────────────────────────────────────────────────────────
# POST /chat-with-memory — Chat with automatic semantic memory retrieval
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/chat-with-memory", response_model=ChatResponse)
async def chat_with_memory(
    request: ChatRequest,
    stored_messages_json: list[dict] | None = None,
):
    """
    Like /chat, but also accepts stored messages with embeddings for automatic
    memory context retrieval. Backend sends stored messages from DB; we find
    relevant context and inject it into the conversation.

    **Usage:** POST JSON body with `request` fields + optional `stored_messages_json`
    containing past messages with their embeddings.
    """
    client = _client()
    memory_context = ""

    if stored_messages_json:
        from models import StoredMessage
        try:
            stored = [StoredMessage(**m) for m in stored_messages_json]
            query_emb = await get_embedding(client, request.message)
            settings = get_settings()
            results = semantic_search(
                query_embedding=query_emb,
                stored_messages=stored,
                top_k=5,
                threshold=settings.SIMILARITY_THRESHOLD,
            )
            memory_context = build_memory_context(results)
        except Exception:
            pass  # Graceful degradation — proceed without memory

    try:
        chat_response, _, _ = await generate_response(
            client=client,
            request=request,
            memory_context=memory_context,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation error: {str(e)}")

    return chat_response


# ─────────────────────────────────────────────────────────────────────────────
# POST /semantic-search — Find relevant past messages
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/semantic-search", response_model=SemanticSearchResponse)
async def search_memories(request: SemanticSearchRequest):
    """
    Backend sends stored messages (with embeddings) from DB.
    We compute the query embedding and return the most relevant past messages.

    **Backend integration:**
    - Store message embeddings (from /chat response) in your vector store or DB.
    - Call this endpoint before /chat to get relevant context.
    - Pass the results as `past_summaries` or enrich conversation_history.
    """
    client = _client()

    try:
        query_embedding = await get_embedding(client, request.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding error: {str(e)}")

    threshold = request.threshold or get_settings().SIMILARITY_THRESHOLD
    results = semantic_search(
        query_embedding=query_embedding,
        stored_messages=request.stored_messages,
        top_k=request.top_k,
        threshold=threshold,
    )

    return SemanticSearchResponse(
        results=results,
        query_embedding=query_embedding,
    )


# ─────────────────────────────────────────────────────────────────────────────
# POST /summary — Generate session summary
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/summary", response_model=SummaryResponse)
async def summarize_session(request: SummaryRequest):
    """
    Generate a neutral summary of a conversation session.

    **Backend integration:**
    - Call at end of a session with all messages.
    - Store the returned summary for future session continuity.
    - Pass stored summaries in `past_summaries` field of /chat requests.
    """
    client = _client()

    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages to summarize")

    try:
        return await generate_session_summary(client, request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary error: {str(e)}")


# ─────────────────────────────────────────────────────────────────────────────
# POST /embed — Generate embedding for a text
# ─────────────────────────────────────────────────────────────────────────────
from pydantic import BaseModel


class EmbedTextRequest(BaseModel):
    text: str
    

class EmbedTextResponse(BaseModel):
    embedding: list[float]


@app.post("/embed", response_model=EmbedTextResponse)
async def embed_text(request: EmbedTextRequest):
    """
    Generate an embedding vector for any text.
    Useful for backend to embed messages before storing.
    """
    client = _client()
    try:
        emb = await get_embedding(client, request.text)
        return EmbedTextResponse(embedding=emb)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding error: {str(e)}")


# ─────────────────────────────────────────────────────────────────────────────
# GET /health
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "MindGlow AI",
        "version": "1.0.0",
        "chatbots": ["reflect", "inner_learning"],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Run with: uvicorn main:app --reload
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
