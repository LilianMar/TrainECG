"""
Achievement service - handles badge unlocking and tracking.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.achievement import UserAchievement, BADGE_DEFINITIONS
from app.models.progress import UserProgress
from app.models.ecg import ECGClassification
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AchievementService:
    """Service for managing user achievements and badges."""

    @staticmethod
    def get_user_achievements(db: Session, user_id: int) -> dict:
        """Get all achievements for a user."""
        achievements = db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id
        ).all()

        return {
            "earned_badges": [
                {
                    "id": a.id,
                    "name": a.badge_name,
                    "description": a.description,
                    "icon": a.icon,
                    "color": a.color,
                    "earned_at": a.earned_at.isoformat() if a.earned_at else None,
                }
                for a in achievements
            ],
            "total_earned": len(achievements),
            "available_badges": len(BADGE_DEFINITIONS),
        }

    @staticmethod
    def unlock_achievement(
        db: Session, 
        user_id: int, 
        achievement_type: str, 
        test_attempt_id: int = None
    ) -> UserAchievement:
        """Unlock a badge for a user."""
        
        # Check if already earned
        existing = db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id,
            UserAchievement.achievement_type == achievement_type
        ).first()
        
        if existing:
            logger.info(f"Achievement already earned: {user_id} - {achievement_type}")
            return existing

        badge_def = BADGE_DEFINITIONS.get(achievement_type)
        if not badge_def:
            logger.warning(f"Unknown achievement type: {achievement_type}")
            return None

        achievement = UserAchievement(
            user_id=user_id,
            achievement_type=achievement_type,
            badge_name=badge_def["name"],
            description=badge_def["description"],
            icon=badge_def["icon"],
            color=badge_def["color"],
            test_attempt_id=test_attempt_id,
        )
        
        db.add(achievement)
        db.commit()
        db.refresh(achievement)
        
        logger.info(f"Achievement unlocked: {user_id} - {achievement_type}")
        return achievement

    @staticmethod
    def check_and_unlock_badges(
        db: Session, 
        user_id: int, 
        test_attempt_id: int = None,
        test_data: dict = None
    ) -> list:
        """Check conditions and unlock any applicable badges after test."""
        
        unlocked = []
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == user_id
        ).first()

        if not progress:
            return unlocked

        # 1. First diagnostic test
        diagnostic_tests = db.query(ECGClassification).filter(
            ECGClassification.user_id == user_id
        ).count()
        
        if diagnostic_tests == 1:
            achievement = AchievementService.unlock_achievement(
                db, user_id, "diagnostic_complete", test_attempt_id
            )
            if achievement:
                unlocked.append(achievement)

        # 2. Improvement 15%
        if test_data and "improvement_percentage" in test_data:
            if test_data["improvement_percentage"] >= 15:
                achievement = AchievementService.unlock_achievement(
                    db, user_id, "improvement_15", test_attempt_id
                )
                if achievement:
                    unlocked.append(achievement)

        # 3. Score 90%+
        if test_data and "accuracy" in test_data:
            if test_data["accuracy"] >= 90:
                achievement = AchievementService.unlock_achievement(
                    db, user_id, "score_90", test_attempt_id
                )
                if achievement:
                    unlocked.append(achievement)

        # 4. Arrhythmia mastery (90%+ in specific types)
        if test_data and "arrhythmia_breakdown" in test_data:
            for arrhythmia_data in test_data["arrhythmia_breakdown"]:
                arrhythmia_name = arrhythmia_data.get("name", "").lower()
                accuracy = arrhythmia_data.get("accuracy", 0)
                
                if accuracy >= 90:
                    if "fibrillation" in arrhythmia_name or "fa" in arrhythmia_name:
                        achievement = AchievementService.unlock_achievement(
                            db, user_id, "master_fa", test_attempt_id
                        )
                        if achievement:
                            unlocked.append(achievement)
                    elif "ventricular" in arrhythmia_name or "tv" in arrhythmia_name:
                        achievement = AchievementService.unlock_achievement(
                            db, user_id, "master_vt", test_attempt_id
                        )
                        if achievement:
                            unlocked.append(achievement)
                    elif "block" in arrhythmia_name or "av" in arrhythmia_name:
                        achievement = AchievementService.unlock_achievement(
                            db, user_id, "master_av_block", test_attempt_id
                        )
                        if achievement:
                            unlocked.append(achievement)

        # 5. Three tests completed
        tests_completed = db.query(ECGClassification).filter(
            ECGClassification.user_id == user_id
        ).count()
        
        if tests_completed >= 3:
            achievement = AchievementService.unlock_achievement(
                db, user_id, "three_tests", test_attempt_id
            )
            if achievement:
                unlocked.append(achievement)

        # 6. 100+ correct answers in practice
        if progress.total_practice_correct >= 100:
            achievement = AchievementService.unlock_achievement(
                db, user_id, "hundred_correct", test_attempt_id
            )
            if achievement:
                unlocked.append(achievement)

        return unlocked
