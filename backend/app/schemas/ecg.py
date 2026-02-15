"""
Pydantic schemas for ECG Classification.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.ecg import ArrhythmiaClassEnum


class WindowCoordinate(BaseModel):
    """Schema for Grad-CAM window coordinates."""
    x: int
    y: int
    width: int
    height: int
    confidence: float


class ECGClassificationRequest(BaseModel):
    """Schema for ECG classification request."""
    # File is handled separately in multipart form


class ECGClassificationResponse(BaseModel):
    """Schema for ECG classification response."""
    id: int
    predicted_class: ArrhythmiaClassEnum
    confidence: float
    windows_analyzed: int
    affected_windows: int
    gradcam_windows: List[WindowCoordinate]
    llm_explanation: str
    processing_time_ms: int
    created_at: datetime

    class Config:
        from_attributes = True


class PracticeQuestionResponse(BaseModel):
    """Schema for practice question response."""
    id: int
    image_path: str
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    difficulty_level: int
    # Note: correct_answer, explanation hidden until answered

    class Config:
        from_attributes = True


class PracticeAnswerRequest(BaseModel):
    """Schema for practice answer submission."""
    question_id: int
    selected_answer: int = Field(..., ge=0, le=3)
    time_spent_seconds: int = Field(..., gt=0)


class PracticeAnswerResponse(BaseModel):
    """Schema for practice answer feedback."""
    is_correct: bool
    correct_answer: int
    explanation: str
    correct_class: ArrhythmiaClassEnum


class PracticeQuestionList(BaseModel):
    """Schema for returning multiple practice questions."""
    total: int
    questions: List[PracticeQuestionResponse]
