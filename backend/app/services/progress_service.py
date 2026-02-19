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
        Returns separate stats for practice and test attempts.

        Returns:
            Dict with arrhythmia types and performance metrics for both practice and test
        """
        from app.models.ecg import PracticeQuestion, PostPracticeTest
        import json
        
        # Get practice attempts
        practice_attempts = db.query(PracticeAttempt).filter(
            PracticeAttempt.user_id == user_id
        ).all()

        # Initialize performance dict for all arrhythmia types
        performance = {}
        for arrhythmia in ArrhythmiaClassEnum:
            performance[arrhythmia.value] = {
                "practice_correct": 0,
                "practice_total": 0,
                "practice_accuracy": 0.0,
                "test_correct": 0,
                "test_total": 0,
                "test_accuracy": 0.0,
            }

        # Process practice attempts
        for attempt in practice_attempts:
            # Get the question to know which arrhythmia type it is
            question = db.query(PracticeQuestion).filter(
                PracticeQuestion.id == attempt.question_id
            ).first()
            
            if question and question.correct_class:
                arrhythmia_type = question.correct_class.lower().replace(" ", "_")
                if arrhythmia_type in performance:
                    performance[arrhythmia_type]["practice_total"] += 1
                    if attempt.is_correct == "True":
                        performance[arrhythmia_type]["practice_correct"] += 1

        # Calculate practice accuracies
        for arrhythmia_type in performance:
            if performance[arrhythmia_type]["practice_total"] > 0:
                performance[arrhythmia_type]["practice_accuracy"] = round(
                    (performance[arrhythmia_type]["practice_correct"] / 
                     performance[arrhythmia_type]["practice_total"]) * 100, 1
                )

        # Process post-practice test attempts
        post_tests = db.query(PostPracticeTest).filter(
            PostPracticeTest.user_id == user_id
        ).all()
        
        for post_test in post_tests:
            if post_test.question_answers:
                try:
                    question_answers = json.loads(post_test.question_answers)
                    for qa in question_answers:
                        correct_class = qa.get("correct_class", "unknown").lower().replace(" ", "_")
                        if correct_class in performance:
                            performance[correct_class]["test_total"] += 1
                            if qa.get("is_correct"):
                                performance[correct_class]["test_correct"] += 1
                except json.JSONDecodeError:
                    # Skip if JSON is invalid
                    pass

        # Calculate test accuracies
        for arrhythmia_type in performance:
            if performance[arrhythmia_type]["test_total"] > 0:
                performance[arrhythmia_type]["test_accuracy"] = round(
                    (performance[arrhythmia_type]["test_correct"] / 
                     performance[arrhythmia_type]["test_total"]) * 100, 1
                )

        return performance

    @staticmethod
    def get_practice_progression(db: Session, user_id: int, weeks: int = 6) -> list[dict]:
        """
        Get user's practice progression by week (correct answers per attempt).

        Returns:
            List of weekly stats with correct answers count
        """
        from datetime import timedelta, datetime
        
        attempts = db.query(PracticeAttempt).filter(
            PracticeAttempt.user_id == user_id
        ).order_by(PracticeAttempt.created_at).all()

        if not attempts:
            return []

        # Calculate weeks data
        progression = []
        end_date = datetime.utcnow()
        
        for week_num in range(weeks - 1, -1, -1):
            week_start = end_date - timedelta(days=7 * (week_num + 1))
            week_end = end_date - timedelta(days=7 * week_num)
            
            week_attempts = [
                a for a in attempts 
                if a.created_at and week_start <= a.created_at <= week_end
            ]
            
            correct_count = len([a for a in week_attempts if a.is_correct == "True"])
            
            progression.append({
                "week": f"Sem {weeks - week_num}",
                "correct_answers": correct_count,
                "total_attempts": len(week_attempts),
                "accuracy": (correct_count / len(week_attempts) * 100) if week_attempts else 0
            })

        return progression

    @staticmethod
    def get_incorrect_answers(db: Session, user_id: int) -> list[dict]:
        """
        Extract all incorrect answers from post-practice tests.
        
        Returns:
            List of incorrect answers with question details
        """
        from app.models.ecg import PostPracticeTest
        import json
        
        incorrect_answers = []
        
        post_tests = db.query(PostPracticeTest).filter(
            PostPracticeTest.user_id == user_id
        ).all()
        
        for post_test in post_tests:
            if post_test.question_answers:
                try:
                    question_answers = json.loads(post_test.question_answers)
                    for qa in question_answers:
                        if qa.get("is_correct") == False:
                            incorrect_answers.append({
                                "correct_class": qa.get("correct_class", "unknown"),
                                "question_text": qa.get("question_text", ""),
                            })
                except json.JSONDecodeError:
                    pass
        
        return incorrect_answers

    @staticmethod
    def generate_recommendations(
        db: Session, user_id: int
    ) -> dict:
        """
        Generate personalized recommendations using GPT.

        Returns:
            Dict with LLM-generated recommendations and metadata
        """
        from app.services.llm_service import LLMService
        from app.models.ecg import PostPracticeTest
        
        progress = ProgressService.get_or_create_progress(db, user_id)
        performance = ProgressService.get_arrhythmia_performance(db, user_id)
        
        # Get test count
        test_count = db.query(PostPracticeTest).filter(
            PostPracticeTest.user_id == user_id
        ).count()
        
        # Calculate overall accuracy
        total_correct = 0
        total_tests = 0
        weak_areas = []
        
        for arrhythmia, stats in performance.items():
            test_total = stats.get("test_total", 0)
            test_correct = stats.get("test_correct", 0)
            test_accuracy = stats.get("test_accuracy", 0)
            
            total_correct += test_correct
            total_tests += test_total
            
            if test_total > 0 and test_accuracy < 70:
                weak_areas.append(arrhythmia)
        
        overall_accuracy = (total_correct / total_tests * 100) if total_tests > 0 else 0
        
        # Get incorrect answers to provide specific feedback
        incorrect_answers = ProgressService.get_incorrect_answers(db, user_id)
        
        # Generate recommendations using GPT
        recommendations_html = LLMService.generate_progress_recommendations(
            arrhythmia_performance=performance,
            test_attempts=test_count,
            accuracy=overall_accuracy,
            weak_areas=weak_areas,
            incorrect_answers=incorrect_answers,
        )
        
        return {
            "recommendations": recommendations_html,
            "test_attempts": test_count,
            "overall_accuracy": overall_accuracy,
            "weak_areas": weak_areas,
            "has_llm": True,  # Indicates GPT was used
        }

