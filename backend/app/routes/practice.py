"""
Practice mode routes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.routes.users import get_current_user
from app.schemas.ecg import (
    PracticeAnswerRequest,
    PracticeAnswerResponse,
    PracticeQuestionList,
    PracticeQuestionResponse,
)
from app.services.ecg_service import ECGService
from app.services.progress_service import ProgressService
from app.utils import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/practice", tags=["Practice Mode"])


@router.get("/questions", response_model=PracticeQuestionList)
async def get_practice_questions(
    limit: int = 10,
    difficulty: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get practice questions."""
    questions = ECGService.get_practice_questions(db, limit, difficulty)
    return {
        "total": len(questions),
        "questions": questions,
    }


@router.get("/questions/{question_id}", response_model=PracticeQuestionResponse)
async def get_practice_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific practice question."""
    question = ECGService.get_practice_question(db, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )
    return question


@router.post("/answer", response_model=PracticeAnswerResponse)
async def submit_answer(
    answer: PracticeAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit an answer to a practice question."""
    try:
        question = ECGService.get_practice_question(db, answer.question_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found",
            )

        is_correct = answer.selected_answer == question.correct_answer

        ECGService.create_practice_attempt(
            db=db,
            user_id=current_user.id,
            question_id=answer.question_id,
            selected_answer=answer.selected_answer,
            is_correct=is_correct,
            time_spent_seconds=answer.time_spent_seconds,
        )

        ProgressService.update_progress(
            db=db,
            user_id=current_user.id,
            practice_attempts=1,
            correct_answers=1 if is_correct else 0,
        )

        logger.info(
            "Practice attempt recorded: user %s, correct=%s",
            current_user.id,
            is_correct,
        )

        return PracticeAnswerResponse(
            is_correct=is_correct,
            correct_answer=question.correct_answer,
            explanation=question.explanation,
            correct_class=question.correct_class,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Answer submission error: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit answer",
        ) from exc


@router.get("/stats")
async def get_practice_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's practice statistics."""
    total, correct, accuracy = ECGService.get_user_practice_stats(db, current_user.id)
    return {
        "total_attempts": total,
        "correct_answers": correct,
        "accuracy_percentage": accuracy,
    }
