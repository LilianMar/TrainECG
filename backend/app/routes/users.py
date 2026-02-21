"""
User profile routes - Get, Update user information.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List

from app.database import get_db
from app.schemas.user import UserResponse, UserUpdate
from app.models.user import User
from app.models.ecg import ECGClassification, PracticeAttempt
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


@router.get("/me/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's performance statistics."""
    
    # Total ECGs analyzed
    total_ecgs = db.query(func.count(ECGClassification.id))\
        .filter(ECGClassification.user_id == current_user.id)\
        .scalar() or 0
    
    # Average accuracy from post-practice tests (if available)
    # Otherwise fallback to practice attempts accuracy
    from app.models.ecg import PostPracticeTest
    
    post_practice_accuracy = db.query(func.avg(PostPracticeTest.accuracy))\
        .filter(PostPracticeTest.user_id == current_user.id)\
        .scalar()
    
    if post_practice_accuracy is not None:
        # Use post-practice test accuracy (Precisión General from Progress)
        avg_accuracy = int(post_practice_accuracy)
    else:
        # Fallback: use practice attempts accuracy
        avg_accuracy_result = db.query(func.avg(PracticeAttempt.is_correct))\
            .filter(PracticeAttempt.user_id == current_user.id)\
            .scalar()
        avg_accuracy = int((avg_accuracy_result or 0) * 100)
    
    # Consecutive days streak
    consecutive_days = 0
    current_date = datetime.utcnow().date()
    
    # Get distinct activity dates (from ECG classifications and practice attempts)
    ecg_dates = db.query(func.date(ECGClassification.created_at).label('activity_date'))\
        .filter(ECGClassification.user_id == current_user.id)\
        .distinct()
    
    practice_dates = db.query(func.date(PracticeAttempt.created_at).label('activity_date'))\
        .filter(PracticeAttempt.user_id == current_user.id)\
        .distinct()
    
    # Union of both queries - convert string dates to date objects
    activity_dates = set()
    for row in ecg_dates:
        try:
            if isinstance(row.activity_date, str):
                activity_dates.add(datetime.strptime(row.activity_date, '%Y-%m-%d').date())
            else:
                activity_dates.add(row.activity_date)
        except (ValueError, TypeError):
            pass
    
    for row in practice_dates:
        try:
            if isinstance(row.activity_date, str):
                activity_dates.add(datetime.strptime(row.activity_date, '%Y-%m-%d').date())
            else:
                activity_dates.add(row.activity_date)
        except (ValueError, TypeError):
            pass
    
    # Calculate consecutive days
    if activity_dates:
        sorted_dates = sorted(activity_dates, reverse=True)
        if sorted_dates and sorted_dates[0] >= current_date - timedelta(days=1):
            consecutive_days = 1
            for i in range(len(sorted_dates) - 1):
                if (sorted_dates[i] - sorted_dates[i + 1]).days == 1:
                    consecutive_days += 1
                else:
                    break
    
    # Determine rank based on skill_level from initial test
    rank = "Principiante"
    if current_user.skill_level:
        if current_user.skill_level in [4, 5]:
            rank = "Avanzado"
        elif current_user.skill_level == 3:
            rank = "Intermedio"
        else:  # skill_level 1 or 2
            rank = "Principiante"
    else:
        # Fallback to practice accuracy if no skill_level yet
        if total_ecgs >= 50 and avg_accuracy >= 80:
            rank = "Avanzado"
        elif total_ecgs >= 20 and avg_accuracy >= 70:
            rank = "Intermedio"
    
    return {
        "total_ecgs": total_ecgs,
        "avg_accuracy": avg_accuracy,
        "consecutive_days": consecutive_days,
        "rank": rank,
        "skill_level": current_user.skill_level,
    }


@router.get("/me/activity")
async def get_user_activity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's recent activity (last 3 actions)."""
    
    activities = []
    
    # Get recent ECG classifications
    recent_ecgs = db.query(ECGClassification)\
        .filter(ECGClassification.user_id == current_user.id)\
        .order_by(ECGClassification.created_at.desc())\
        .limit(5)\
        .all()
    
    for ecg in recent_ecgs:
        days_ago = (datetime.utcnow() - ecg.created_at).days
        date_str = "Hoy" if days_ago == 0 else f"Hace {days_ago} día{'s' if days_ago > 1 else ''}"
        
        activities.append({
            "date": date_str,
            "activity": f"Analizó ECG: {ecg.predicted_class}",
            "score": f"{int(ecg.confidence * 100)}% confianza",
            "timestamp": ecg.created_at
        })
    
    # Get recent practice attempts
    recent_practice = db.query(PracticeAttempt)\
        .filter(PracticeAttempt.user_id == current_user.id)\
        .order_by(PracticeAttempt.created_at.desc())\
        .limit(5)\
        .all()
    
    for attempt in recent_practice:
        days_ago = (datetime.utcnow() - attempt.created_at).days
        date_str = "Hoy" if days_ago == 0 else f"Hace {days_ago} día{'s' if days_ago > 1 else ''}"
        
        result = "correcta" if attempt.is_correct else "incorrecta"
        activities.append({
            "date": date_str,
            "activity": f"Práctica: respuesta {result}",
            "score": f"Pregunta ID {attempt.question_id}",
            "timestamp": attempt.created_at
        })
    
    # Sort all activities by timestamp and get top 3
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_activities = activities[:3]
    
    # Remove timestamp from response
    for activity in recent_activities:
        del activity['timestamp']
    
    return {"activities": recent_activities}
