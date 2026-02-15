"""
ECG service - handles business logic for ECG classification and practice.
"""

import json
from datetime import datetime
from typing import List, Tuple
from sqlalchemy.orm import Session
from app.models.ecg import (
    ECGClassification,
    PracticeQuestion,
    PracticeAttempt,
    ArrhythmiaClassEnum,
)
from app.schemas.ecg import WindowCoordinate
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ECGService:
    """Service for ECG-related operations."""

    @staticmethod
    def create_classification(
        db: Session,
        user_id: int,
        image_filename: str,
        image_path: str,
        predicted_class: str,
        confidence: float,
        windows_analyzed: int,
        affected_windows: int,
        gradcam_windows: List[WindowCoordinate],
        llm_explanation: str,
        processing_time_ms: int,
    ) -> ECGClassification:
        """Create a new ECG classification record."""
        try:
            # Convert windows to JSON
            windows_json = json.dumps(
                [window.model_dump() for window in gradcam_windows]
            )

            classification = ECGClassification(
                user_id=user_id,
                image_filename=image_filename,
                image_path=image_path,
                predicted_class=predicted_class,
                confidence=confidence,
                windows_analyzed=windows_analyzed,
                affected_windows=affected_windows,
                gradcam_data=windows_json,
                llm_explanation=llm_explanation,
                processing_time_ms=processing_time_ms,
            )

            db.add(classification)
            db.commit()
            db.refresh(classification)

            logger.info(
                f"Classification created for user {user_id}: {predicted_class}"
            )
            return classification
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating classification: {str(e)}")
            raise

    @staticmethod
    def get_user_classifications(
        db: Session, user_id: int, limit: int = 10
    ) -> List[ECGClassification]:
        """Get user's classification history."""
        return (
            db.query(ECGClassification)
            .filter(ECGClassification.user_id == user_id)
            .order_by(ECGClassification.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_practice_questions(
        db: Session, limit: int = None, difficulty: int = None
    ) -> List[PracticeQuestion]:
        """Get practice questions with optional filters."""
        query = db.query(PracticeQuestion)

        if difficulty:
            query = query.filter(PracticeQuestion.difficulty_level == difficulty)

        if limit:
            query = query.limit(limit)

        return query.all()

    @staticmethod
    def get_practice_question(db: Session, question_id: int) -> PracticeQuestion | None:
        """Get a specific practice question."""
        return db.query(PracticeQuestion).filter(
            PracticeQuestion.id == question_id
        ).first()

    @staticmethod
    def create_practice_attempt(
        db: Session,
        user_id: int,
        question_id: int,
        selected_answer: int,
        is_correct: bool,
        time_spent_seconds: int,
    ) -> PracticeAttempt:
        """Record a practice attempt."""
        try:
            attempt = PracticeAttempt(
                user_id=user_id,
                question_id=question_id,
                selected_answer=selected_answer,
                is_correct=str(is_correct),
                time_spent_seconds=time_spent_seconds,
            )

            db.add(attempt)
            db.commit()
            db.refresh(attempt)

            logger.info(
                f"Practice attempt recorded: user {user_id}, "
                f"question {question_id}, correct={is_correct}"
            )
            return attempt
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating practice attempt: {str(e)}")
            raise

    @staticmethod
    def get_user_practice_stats(
        db: Session, user_id: int
    ) -> Tuple[int, int, float]:
        """
        Get user's practice statistics.

        Returns:
            Tuple of (total_attempts, correct_answers, accuracy_percentage)
        """
        attempts = db.query(PracticeAttempt).filter(
            PracticeAttempt.user_id == user_id
        ).all()

        if not attempts:
            return 0, 0, 0.0

        total = len(attempts)
        correct = sum(1 for attempt in attempts if attempt.is_correct == "True")
        accuracy = (correct / total) * 100 if total > 0 else 0.0

        return total, correct, accuracy

    @staticmethod
    def create_practice_question(
        db: Session,
        image_filename: str,
        image_path: str,
        question_text: str,
        correct_answer: int,
        option_a: str,
        option_b: str,
        option_c: str,
        option_d: str,
        explanation: str,
        correct_class: str,
        difficulty_level: int = 1,
    ) -> PracticeQuestion:
        """Create a new practice question."""
        try:
            question = PracticeQuestion(
                image_filename=image_filename,
                image_path=image_path,
                question_text=question_text,
                correct_answer=correct_answer,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                explanation=explanation,
                correct_class=correct_class,
                difficulty_level=difficulty_level,
            )

            db.add(question)
            db.commit()
            db.refresh(question)

            logger.info(f"Practice question created: {question.id}")
            return question
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating practice question: {str(e)}")
            raise
