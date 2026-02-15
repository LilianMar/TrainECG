"""
User profile routes - Get, Update user information.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserResponse, UserUpdate
from app.models.user import User
from app.services.user_service import UserService
from app.security.auth import verify_token
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["User Profile"])


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to get current authenticated user."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    token = authorization
    if authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()

    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile information."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update current user's profile information."""
    try:
        updated_user = UserService.update_user(db, current_user.id, user_update)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"User profile updated: {updated_user.email}")
        return updated_user
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.get("/profile/{user_id}", response_model=UserResponse)
async def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get user profile (public information)."""
    user = UserService.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
