"""
Pydantic schemas for User entities.
Used for request/response validation and serialization.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserTypeEnum


class UserBase(BaseModel):
    """Base user schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    user_type: UserTypeEnum
    institution: Optional[str] = Field(None, max_length=255)


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for user profile updates."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    institution: Optional[str] = Field(None, max_length=255)


class UserResponse(UserBase):
    """Schema for user response (read operations)."""
    id: int
    is_active: bool
    is_verified: bool
    skill_level: Optional[int] = None
    initial_test_completed: bool = False
    initial_test_score: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str
