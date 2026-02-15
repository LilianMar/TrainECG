"""
Pydantic schemas for user progress and analytics.
"""

from datetime import datetime
from pydantic import BaseModel


class ArrhythmiaPerformance(BaseModel):
    """Schema for performance by arrhythmia type."""
    arrhythmia: str
    correct: int
    total: int
    accuracy: float


class UserProgressResponse(BaseModel):
    """Schema for user progress response."""
    total_ecgs_analyzed: int
    classification_accuracy: float
    total_practice_attempts: int
    practice_accuracy: float
    total_practice_correct: int
    current_streak_days: int
    longest_streak_days: int
    total_achievements: int
    last_activity_date: datetime | None

    class Config:
        from_attributes = True


class UserRecommendation(BaseModel):
    """Schema for personalized recommendations."""
    type: str  # "improvement" or "strength"
    arrhythmia: str
    accuracy: float
    message: str


class UserProgressDetailResponse(BaseModel):
    """Schema for detailed user progress with recommendations."""
    progress: UserProgressResponse
    arrhythmia_performance: list[ArrhythmiaPerformance]
    recommendations: list[UserRecommendation]
