"""
SQLAlchemy model for chatbot query logs.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func

from app.database.base import Base


class ChatbotQueryLog(Base):
    """Stores chatbot query/response interactions for traceability."""

    __tablename__ = "chatbot_query_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False, default=0.0)
    source_id = Column(Integer, nullable=True)
    source_category = Column(String(120), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
