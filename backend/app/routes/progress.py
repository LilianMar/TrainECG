"""
Progress tracking routes.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.ecg import PostPracticeTest
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
    import json
    
    progress = ProgressService.get_or_create_progress(db, current_user.id)
    
    # Calculate test accuracy (excluding 'unknown' classifications)
    post_tests = db.query(PostPracticeTest).filter(
        PostPracticeTest.user_id == current_user.id
    ).all()
    
    test_correct = 0
    test_total = 0
    for test in post_tests:
        if test.question_answers:
            try:
                question_answers = json.loads(test.question_answers)
                for qa in question_answers:
                    correct_class = qa.get("correct_class", "unknown")
                    if correct_class != "unknown":
                        test_total += 1
                        if qa.get("is_correct"):
                            test_correct += 1
            except json.JSONDecodeError:
                pass
    
    test_accuracy = int((test_correct / test_total) * 100) if test_total > 0 else 0
    
    return {
        "total_ecgs_analyzed": progress.total_ecgs_analyzed,
        "classification_accuracy": progress.classification_accuracy,
        "total_practice_attempts": progress.total_practice_attempts,
        "practice_accuracy": progress.practice_accuracy,
        "total_practice_correct": progress.total_practice_correct,
        "test_accuracy": test_accuracy,
        "test_correct": test_correct,
        "test_total": test_total,
        "current_streak_days": progress.current_streak_days,
        "longest_streak_days": progress.longest_streak_days,
        "total_achievements": progress.total_achievements,
        "last_activity_date": progress.last_activity_date,
        "skill_level": current_user.skill_level,
    }


@router.get("/detailed", response_model=UserProgressDetailResponse)
async def get_detailed_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get detailed progress with recommendations."""
    progress = ProgressService.get_or_create_progress(db, current_user.id)
    performance = ProgressService.get_arrhythmia_performance(db, current_user.id)
    recommendations = ProgressService.generate_recommendations(db, current_user.id, current_user.name)

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
    recommendations = ProgressService.generate_recommendations(db, current_user.id, current_user.name)
    return recommendations


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
    """Get practice session attempts with accuracy percentage."""
    from app.models.ecg import PracticeAttempt
    
    # Get all practice attempts ordered chronologically
    attempts = db.query(PracticeAttempt).filter(
        PracticeAttempt.user_id == current_user.id
    ).order_by(PracticeAttempt.created_at.asc()).all()
    
    if not attempts:
        return {"test_attempts": []}
    
    # Group attempts into sessions (every 10 questions or by day)
    sessions = []
    current_session = []
    session_size = 10  # Group every 10 attempts as a session
    
    for attempt in attempts:
        current_session.append(attempt)
        if len(current_session) >= session_size:
            # Calculate accuracy for this session
            correct_count = sum(1 for a in current_session if a.is_correct == "True")
            accuracy = (correct_count / len(current_session)) * 100
            sessions.append({
                "attempt": f"Intento {len(sessions) + 1}",
                "score": round(accuracy, 1),
                "correct": correct_count,
                "total": len(current_session),
                "created_at": current_session[-1].created_at.isoformat() if current_session[-1].created_at else None,
            })
            current_session = []
    
    # Add remaining attempts if any
    if current_session:
        correct_count = sum(1 for a in current_session if a.is_correct == "True")
        accuracy = (correct_count / len(current_session)) * 100
        sessions.append({
            "attempt": f"Intento {len(sessions) + 1}",
            "score": round(accuracy, 1),
            "correct": correct_count,
            "total": len(current_session),
            "created_at": current_session[-1].created_at.isoformat() if current_session[-1].created_at else None,
        })
    
    # Return last 10 sessions
    sessions = sessions[-10:]
    
    return {
        "test_attempts": sessions,
    }


@router.get("/post-test-attempts")
async def get_post_test_attempts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get test progression including initial test and post-practice tests."""
    # Build test data array starting with initial reference point and initial test score
    test_data = []
    
    # Add initial reference point (0, 0) - starting point
    test_data.append({
        "attempt": "Inicio",
        "score": 0.0,
        "correct": 0,
        "total": 0,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
    })
    
    # Add initial test score as Test 1
    if current_user.initial_test_completed and current_user.initial_test_score is not None:
        initial_accuracy = (current_user.initial_test_score / 10) * 100  # Assuming 10 questions
        test_data.append({
            "attempt": "Test 1",
            "score": round(initial_accuracy, 1),
            "correct": current_user.initial_test_score,
            "total": 10,
            "created_at": current_user.updated_at.isoformat() if current_user.updated_at else None,
        })
    
    # Get all post-practice test results ordered chronologically
    tests = db.query(PostPracticeTest).filter(
        PostPracticeTest.user_id == current_user.id
    ).order_by(PostPracticeTest.created_at.asc()).all()
    
    # Add post-practice tests starting from Test 2
    for i, test in enumerate(tests):
        test_data.append({
            "attempt": f"Test {i + 2}",
            "score": round(test.accuracy, 1),
            "correct": test.score,
            "total": test.total,
            "created_at": test.created_at.isoformat() if test.created_at else None,
        })
    
    # Return last 20 tests
    test_data = test_data[-20:]
    
    return {
        "post_test_attempts": test_data,
    }

