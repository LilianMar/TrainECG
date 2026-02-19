"""
SQLAlchemy models for User entity.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.sql import func
from app.database.base import Base
import enum


class UserTypeEnum(str, enum.Enum):
    """Enum for user types."""
    STUDENT = "student"
    RESIDENT = "resident"
    DOCTOR = "doctor"
    NURSE = "nurse"
    OTHER = "other"


class User(Base):
    """User model for authentication and profile management."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    user_type = Column(Enum(UserTypeEnum), default=UserTypeEnum.STUDENT, nullable=False)
    institution = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Skill level tracking (1-5, None if initial test not completed)
    skill_level = Column(Integer, nullable=True, default=None)
    initial_test_completed = Column(Boolean, default=False, nullable=False)
    initial_test_score = Column(Integer, nullable=True)  # Score from initial test
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"
