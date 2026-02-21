"""
SQLAlchemy models for ECG Classification.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.base import Base
import enum


class ArrhythmiaClassEnum(str, enum.Enum):
    """Enum for ECG beat classifications."""
    NORMAL = "normal"
    SUPRAVENTRICULAR_ECTOPIC = "supraventricular_ectopic"
    VENTRICULAR_ECTOPIC = "ventricular_ectopic"
    FUSION = "fusion"
    UNKNOWN = "unknown"
    PACED = "paced"


class ECGClassification(Base):
    """Model for storing ECG classification results."""

    __tablename__ = "ecg_classifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    image_filename = Column(String(255), nullable=False)
    image_path = Column(String(500), nullable=False)
    
    # Classification results
    predicted_class = Column(Enum(ArrhythmiaClassEnum), nullable=False)
    confidence = Column(Float, nullable=False)
    
    # Grad-CAM and window information
    gradcam_data = Column(Text, nullable=True)  # JSON string of window coordinates
    windows_analyzed = Column(Integer, default=0, nullable=False)
    affected_windows = Column(Integer, default=0, nullable=False)
    
    # LLM explanation
    llm_explanation = Column(Text, nullable=True)
    
    # Metadata
    processing_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<ECGClassification(id={self.id}, user_id={self.user_id}, class={self.predicted_class})>"


class PracticeQuestion(Base):
    """Model for practice mode questions."""

    __tablename__ = "practice_questions"

    id = Column(Integer, primary_key=True, index=True)
    image_filename = Column(String(255), nullable=False)
    image_path = Column(String(500), nullable=False)
    question_text = Column(Text, nullable=False)
    correct_answer = Column(Integer, nullable=False)  # Index of correct option (0-3)
    option_a = Column(String(255), nullable=False)
    option_b = Column(String(255), nullable=False)
    option_c = Column(String(255), nullable=False)
    option_d = Column(String(255), nullable=False)
    explanation = Column(Text, nullable=False)
    correct_class = Column(String(100), nullable=False)  # Store as string for SQLite compatibility
    difficulty_level = Column(Integer, default=1, nullable=False)  # 1-5
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<PracticeQuestion(id={self.id}, correct_class={self.correct_class})>"


class PracticeAttempt(Base):
    """Model for tracking practice attempts."""

    __tablename__ = "practice_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("practice_questions.id"), nullable=False, index=True)
    selected_answer = Column(Integer, nullable=False)
    is_correct = Column(String(50), nullable=False)  # True/False
    time_spent_seconds = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<PracticeAttempt(id={self.id}, user_id={self.user_id}, correct={self.is_correct})>"


class PostPracticeTest(Base):
    """Model for tracking post-practice test results."""

    __tablename__ = "post_practice_tests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    score = Column(Integer, nullable=False)  # Number of correct answers
    total = Column(Integer, nullable=False)  # Total questions in the test
    accuracy = Column(Float, nullable=False)  # Percentage (0-100)
    previous_level = Column(Integer, nullable=True)  # Skill level before test
    new_level = Column(Integer, nullable=False)  # Skill level after test
    level_improved = Column(String(50), nullable=False)  # "True" or "False"
    question_answers = Column(Text, nullable=True)  # JSON: List of {question_id, is_correct} for arrhythmia breakdown
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<PostPracticeTest(id={self.id}, user_id={self.user_id}, accuracy={self.accuracy}%)>"
