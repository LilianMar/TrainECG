"""
SQLAlchemy models for user progress and analytics.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database.base import Base


class UserProgress(Base):
    """Model for tracking user overall progress."""

    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    
    # Classification stats
    total_ecgs_analyzed = Column(Integer, default=0, nullable=False)
    classification_accuracy = Column(Float, default=0.0, nullable=False)
    
    # Practice stats
    total_practice_attempts = Column(Integer, default=0, nullable=False)
    practice_accuracy = Column(Float, default=0.0, nullable=False)
    total_practice_correct = Column(Integer, default=0, nullable=False)
    
    # Post-practice test tracking
    post_practice_tests_taken = Column(Integer, default=0, nullable=False)
    post_practice_score = Column(Float, nullable=True)  # Score from last post-practice test
    post_practice_level_achieved = Column(Integer, nullable=True)  # Level achieved after post-practice test
    
    # Streak and engagement
    current_streak_days = Column(Integer, default=0, nullable=False)
    longest_streak_days = Column(Integer, default=0, nullable=False)
    last_activity_date = Column(DateTime(timezone=True), nullable=True)
    
    # Achievements
    total_achievements = Column(Integer, default=0, nullable=False)
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<UserProgress(user_id={self.user_id}, accuracy={self.practice_accuracy}%)>"
