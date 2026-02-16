"""
MindGlow Pydantic Models — Request/response schemas for the API.
All models a backend developer needs to integrate with the system.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────────────────
class ChatbotType(str, Enum):
    REFLECT = "reflect"
    INNER_LEARNING = "inner_learning"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


# ─────────────────────────────────────────────────────────────────────────────
# Message Models
# ─────────────────────────────────────────────────────────────────────────────
class Message(BaseModel):
    """A single conversation message (from user or assistant)."""
    role: MessageRole
    content: str
    timestamp: Optional[datetime] = None
    language: Optional[str] = None


class ConversationHistory(BaseModel):
    """Past conversation messages sent by the backend."""
    messages: list[Message] = Field(default_factory=list)


class UserInfo(BaseModel):
    """User information provided by the backend."""
    user_id: str
    display_name: Optional[str] = None
    preferred_language: Optional[str] = None
    metadata: Optional[dict] = None


# ─────────────────────────────────────────────────────────────────────────────
# Chat Request / Response
# ─────────────────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    """
    Request from frontend/backend to chat with a MindGlow bot.
    The backend sends user_info, the current message, and any previous conversation history.
    """
    chatbot: ChatbotType = Field(description="Which chatbot to use: 'reflect' or 'inner_learning'")
    user_info: UserInfo
    message: str = Field(description="The user's current message")
    conversation_history: ConversationHistory = Field(
        default_factory=ConversationHistory,
        description="Previous messages from this conversation (backend provides from DB)"
    )
    past_summaries: list[str] = Field(
        default_factory=list,
        description="Neutral summaries of past sessions (backend provides from DB)"
    )


class ChatResponse(BaseModel):
    """Response returned by the API after processing a user message."""
    reply: str
    detected_language: str
    crisis_detected: bool = False
    crisis_resources: Optional[str] = None
    response_was_filtered: bool = False
    filter_log: Optional[str] = None
    embedding: Optional[list[float]] = Field(
        default=None,
        description="Embedding vector of the user message — backend can store for semantic search"
    )
    reply_embedding: Optional[list[float]] = Field(
        default=None,
        description="Embedding vector of the assistant reply — backend can store for semantic search"
    )
    summary: Optional[str] = Field(
        default=None,
        description="Neutral summary of this exchange — backend can store for continuity"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Semantic Search (backend sends stored embeddings, we find relevant ones)
# ─────────────────────────────────────────────────────────────────────────────
class StoredMessage(BaseModel):
    """A message with its embedding, provided by backend from DB."""
    role: MessageRole
    content: str
    embedding: list[float]
    timestamp: Optional[datetime] = None


class SemanticSearchRequest(BaseModel):
    """Backend sends stored messages with embeddings; we find semantically relevant ones."""
    query: str = Field(description="The current user message to find relevant context for")
    stored_messages: list[StoredMessage] = Field(description="Messages with embeddings from DB")
    top_k: int = Field(default=5, ge=1, le=50)
    threshold: Optional[float] = Field(default=None, description="Min similarity score (0-1)")


class SemanticSearchResult(BaseModel):
    content: str
    role: MessageRole
    similarity: float
    timestamp: Optional[datetime] = None


class SemanticSearchResponse(BaseModel):
    results: list[SemanticSearchResult]
    query_embedding: list[float] = Field(description="Embedding of the query — backend can cache")


# ─────────────────────────────────────────────────────────────────────────────
# Summary Generation
# ─────────────────────────────────────────────────────────────────────────────
class SummaryRequest(BaseModel):
    """Request to generate a neutral summary of a conversation session."""
    chatbot: ChatbotType
    messages: list[Message]


class SummaryResponse(BaseModel):
    summary: str
    detected_language: str


# ─────────────────────────────────────────────────────────────────────────────
# Filter Log (for safety team)
# ─────────────────────────────────────────────────────────────────────────────
class FilterLogEntry(BaseModel):
    """Log entry when a response is filtered — backend stores these for review."""
    timestamp: datetime
    chatbot: ChatbotType
    user_id: str
    original_response: str
    filtered_reason: str
    regenerated_response: str


class CrisisLogEntry(BaseModel):
    """Log entry when crisis is detected — backend stores for safety team."""
    timestamp: datetime
    user_id: str
    user_message: str
    detected_indicators: list[str]
    language: str
