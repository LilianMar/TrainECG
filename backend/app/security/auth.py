"""
Security module for authentication and authorization.
Handles JWT tokens, password hashing, and security utilities.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from app.core.config import get_settings

settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hashed version."""
    return pwd_context.verify(plain_password, hashed_password)


class TokenPayload(BaseModel):
    """JWT token payload structure."""
    sub: int  # User ID
    exp: datetime


def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        user_id: ID of the user
        expires_delta: Optional expiration delta
    
    Returns:
        Encoded JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access"
    }
    
    encoded_jwt = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(user_id: int) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        user_id: ID of the user
    
    Returns:
        Encoded JWT token
    """
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh"
    }
    
    encoded_jwt = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[int]:
    """
    Verify a JWT token and extract user ID.
    
    Args:
        token: JWT token string
    
    Returns:
        User ID if token is valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            return None
        return user_id
    except (JWTError, ValueError):
        return None
