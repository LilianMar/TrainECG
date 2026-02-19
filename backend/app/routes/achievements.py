"""
Achievement tracking routes.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.routes.users import get_current_user
from app.services.achievement_service import AchievementService
from app.utils import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/achievements", tags=["Achievements"])


@router.get("")
async def get_achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all achievements/badges for the current user (earned and available)."""
    achievements = AchievementService.get_user_achievements(db, current_user.id)
    return achievements
