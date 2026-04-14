"""
Pydantic schemas for chatbot endpoint.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class ChatbotQueryRequest(BaseModel):
    """User query payload for chatbot."""

    question: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=1, ge=1, le=5)


class ChatbotResult(BaseModel):
    """Single ranked chatbot result."""

    id: int
    categoria: str
    pregunta: str
    respuesta: str
    score: float


class ChatbotQueryResponse(BaseModel):
    """Chatbot query response payload."""

    answer: str
    found: bool
    results: list[ChatbotResult]


class ChatbotContext(BaseModel):
    """User-specific context used in response generation."""

    skill_level: int | None
    recent_error_topics: list[str]


class ChatbotQueryContextResponse(BaseModel):
    """Contextual chatbot response payload."""

    answer: str
    found: bool
    confidence: float
    sources: list[ChatbotResult]
    context: ChatbotContext


class ChatbotHistoryItem(BaseModel):
    """Logged chatbot interaction."""

    id: int
    question: str
    answer: str
    confidence: float
    source_id: int | None
    source_category: str | None
    created_at: datetime


class ChatbotHistoryResponse(BaseModel):
    """History response payload."""

    total: int
    items: list[ChatbotHistoryItem]
