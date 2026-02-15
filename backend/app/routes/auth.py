"""
Authentication routes - Login, Register, Token refresh.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLoginRequest,
    TokenResponse,
)
from app.services.user_service import UserService
from app.security.auth import create_access_token, create_refresh_token
from app.core.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    - **name**: User's full name
    - **email**: User's email (must be unique)
    - **password**: Password (min 8 characters)
    - **user_type**: Type of user (student, resident, doctor, nurse, other)
    - **institution**: Optional institution name
    """
    try:
        # Check if user already exists
        existing_user = UserService.get_user_by_email(db, user_create.email)
        if existing_user:
            logger.warning(f"Registration attempt with existing email: {user_create.email}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        # Create user
        user = UserService.create_user(db, user_create)
        
        # Generate tokens
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login user and get access token.
    
    - **email**: User's email
    - **password**: User's password
    """
    try:
        user = UserService.authenticate_user(db, credentials.email, credentials.password)
        
        if not user:
            logger.warning(f"Failed login attempt: {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated"
            )
        
        # Generate tokens
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        
        logger.info(f"User logged in: {user.email}")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )
