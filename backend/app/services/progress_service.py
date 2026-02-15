"""
Progress service - handles user progress tracking and recommendations.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.progress import UserProgress
from app.models.ecg import PracticeAttempt, ArrhythmiaClassEnum
from app.services.ecg_service import ECGService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ProgressService:
    """Service for tracking user progress and generating recommendations."""

    @staticmethod
    def get_or_create_progress(db: Session, user_id: int) -> UserProgress:
        """Get or create user progress record."""
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == user_id
        ).first()

        if not progress:
            progress = UserProgress(user_id=user_id)
            db.add(progress)
            db.commit()
            db.refresh(progress)

        return progress

    @staticmethod
    def update_progress(
        db: Session, user_id: int, ecgs_analyzed: int = 0, 
        practice_attempts: int = 0, correct_answers: int = 0
    ) -> UserProgress:
        """Update user progress metrics."""
        progress = ProgressService.get_or_create_progress(db, user_id)

        if ecgs_analyzed > 0:
            progress.total_ecgs_analyzed += ecgs_analyzed

        if practice_attempts > 0:
            progress.total_practice_attempts += practice_attempts
            progress.total_practice_correct += correct_answers
            
            # Recalculate accuracy
            if progress.total_practice_attempts > 0:
                accuracy = (progress.total_practice_correct / 
                           progress.total_practice_attempts) * 100
                progress.practice_accuracy = accuracy

        db.commit()
        db.refresh(progress)

        logger.info(f"Progress updated for user {user_id}")
        return progress

    @staticmethod
    def get_arrhythmia_performance(db: Session, user_id: int) -> dict:
        """
        Get user's performance breakdown by arrhythmia type.

        Returns:
            Dict with arrhythmia types and performance metrics
        """
        attempts = db.query(PracticeAttempt).filter(
            PracticeAttempt.user_id == user_id
        ).all()

        performance = {}
        for arrhythmia in ArrhythmiaClassEnum:
            performance[arrhythmia.value] = {
                "correct": 0,
                "total": 0,
                "accuracy": 0.0
            }

        # This would need to be enhanced based on actual question data
        return performance

    @staticmethod
    def generate_recommendations(
        db: Session, user_id: int
    ) -> list[dict]:
        """
        Generate personalized recommendations based on performance.

        Returns:
            List of recommendation objects
        """
        progress = ProgressService.get_or_create_progress(db, user_id)
        performance = ProgressService.get_arrhythmia_performance(db, user_id)
        recommendations = []

        # Logic to generate recommendations based on weak areas
        for arrhythmia, stats in performance.items():
            if stats["total"] > 0 and stats["accuracy"] < 70:
                recommendations.append({
                    "type": "improvement",
                    "arrhythmia": arrhythmia,
                    "accuracy": stats["accuracy"],
                    "message": f"Practica más casos de {arrhythmia}. "
                              f"Tu precisión es del {stats['accuracy']:.1f}%"
                })
            elif stats["accuracy"] >= 85:
                recommendations.append({
                    "type": "strength",
                    "arrhythmia": arrhythmia,
                    "accuracy": stats["accuracy"],
                    "message": f"Excelente rendimiento en {arrhythmia}. "
                              f"Sigue así ({stats['accuracy']:.1f}%)"
                })

        return recommendations
