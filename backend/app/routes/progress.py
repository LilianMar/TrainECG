"""
Progress tracking routes.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.routes.users import get_current_user
from app.schemas.progress import UserProgressDetailResponse
from app.services.progress_service import ProgressService
from app.utils import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/progress", tags=["Progress Tracking"])


@router.get("")
async def get_user_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's progress overview."""
    progress = ProgressService.get_or_create_progress(db, current_user.id)
    return {
        "total_ecgs_analyzed": progress.total_ecgs_analyzed,
        "classification_accuracy": progress.classification_accuracy,
        "total_practice_attempts": progress.total_practice_attempts,
        "practice_accuracy": progress.practice_accuracy,
        "current_streak_days": progress.current_streak_days,
        "longest_streak_days": progress.longest_streak_days,
        "total_achievements": progress.total_achievements,
        "last_activity_date": progress.last_activity_date,
    }


@router.get("/detailed", response_model=UserProgressDetailResponse)
async def get_detailed_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get detailed progress with recommendations."""
    progress = ProgressService.get_or_create_progress(db, current_user.id)
    performance = ProgressService.get_arrhythmia_performance(db, current_user.id)
    recommendations = ProgressService.generate_recommendations(db, current_user.id)

    return UserProgressDetailResponse(
        progress=progress,
        arrhythmia_performance=list(performance.values()),
        recommendations=recommendations,
    )


@router.get("/recommendations")
async def get_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get personalized recommendations based on performance."""
    recommendations = ProgressService.generate_recommendations(db, current_user.id)
    return {
        "recommendations": recommendations,
        "count": len(recommendations),
    }


@router.get("/stats/by-arrhythmia")
async def get_arrhythmia_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get performance breakdown by arrhythmia type."""
    performance = ProgressService.get_arrhythmia_performance(db, current_user.id)
    return {
        "arrhythmia_stats": performance,
    }


@router.get("/progression")
async def get_practice_progression(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's practice progression by week."""
    progression = ProgressService.get_practice_progression(db, current_user.id, weeks=6)
    return {
        "progression": progression,
    }


@router.get("/test-attempts")
async def get_test_attempts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get last 6 test attempts with scores."""
    from app.models.ecg import ECGClassification
    
    attempts = db.query(ECGClassification).filter(
        ECGClassification.user_id == current_user.id
    ).order_by(ECGClassification.created_at.desc()).limit(6).all()
    
    # Reverse to show chronologically (oldest to newest)
    attempts = list(reversed(attempts))
    
    test_data = []
    for idx, attempt in enumerate(attempts, 1):
        # Score is confidence * 100 (assuming it's between 0-1)
        score = int(attempt.confidence * 100) if attempt.confidence else 0
        test_data.append({
            "attempt": f"Test {idx}",
            "score": score,
            "confidence": attempt.confidence,
            "predicted_class": attempt.predicted_class.value if attempt.predicted_class else None,
            "created_at": attempt.created_at.isoformat() if attempt.created_at else None,
        })
    
    return {
        "test_attempts": test_data,
    }
