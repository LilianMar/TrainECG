"""
Practice mode routes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.ecg import PostPracticeTest
from app.routes.users import get_current_user
from app.schemas.ecg import (
    PracticeAnswerRequest,
    PracticeAnswerResponse,
    PracticeQuestionList,
    PracticeQuestionResponse,
    RecommendationResponse,
)
from app.services.ecg_service import ECGService
from app.services.progress_service import ProgressService
from app.services.llm_service import LLMService
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

@router.post("/complete-initial-test")
async def complete_initial_test(
    request_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Complete the initial test and assign skill level to the user.
    
    Body:
    - **score**: Number of correct answers
    - **total**: Total number of questions
    """
    try:
        score = request_data.get("score")
        total = request_data.get("total")

        if score is None or total is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing score or total",
            )

        if total == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Total questions must be greater than 0",
            )

        # Calculate accuracy percentage
        accuracy = (score / total) * 100

        # Calculate skill level based on accuracy
        skill_level = ECGService.calculate_skill_level(accuracy)

        # Update user with skill level and test completion
        current_user.skill_level = skill_level
        current_user.initial_test_completed = True
        current_user.initial_test_score = score

        db.add(current_user)
        db.commit()
        db.refresh(current_user)

        logger.info(
            f"User {current_user.id} completed initial test with score {score}/{total} "
            f"(accuracy: {accuracy}%, skill_level: {skill_level})"
        )

        return {
            "success": True,
            "skill_level": skill_level,
            "accuracy": accuracy,
            "message": f"Initial test completed. Your skill level is {skill_level}/5",
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error completing initial test: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete initial test",
        ) from exc


@router.post("/post-practice-test", response_model=dict)
async def post_practice_test(
    request_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit post-practice test answers and get recommendations.
    
    This test evaluates progress after practice sessions.
    Compares initial skill level with new level after post-practice test.
    
    Body:
    - **answers**: List of {question_id, selected_answer, time_spent_seconds}
    - **test_questions**: List of full question objects with correct answers (for calculation)
    """
    try:
        if not current_user.initial_test_completed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Complete initial test first",
            )

        answers = request_data.get("answers", [])
        test_questions = request_data.get("test_questions", [])

        if not answers or not test_questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing answers or test questions",
            )

        # Calculate score
        score = 0
        wrong_questions = []
        total_attempts = 0
        question_answers = []  # Track question IDs and correctness for arrhythmia breakdown

        logger.info(f"Processing {len(answers)} answers for {len(test_questions)} test questions")

        for answer in answers:
            question_id = answer.get("question_id")
            selected_answer = answer.get("selected_answer")

            # Get the correct answer directly from database, not from test_questions
            # (test_questions from frontend may not have correct_answer field)
            question_from_db = ECGService.get_practice_question(db, question_id)
            
            if not question_from_db:
                logger.warning(f"Question {question_id} not found in database")
                continue

            correct_answer = question_from_db.correct_answer
            is_correct = selected_answer == correct_answer
            total_attempts += 1

            logger.info(
                f"Question {question_id}: selected={selected_answer}, correct_from_db={correct_answer}, is_correct={is_correct}"
            )

            if is_correct:
                score += 1
            else:
                # Use question from DB for wrong_questions
                wrong_questions.append({
                    "id": question_from_db.id,
                    "question_text": question_from_db.question_text,
                    "correct_class": question_from_db.correct_class,
                    "correct_answer": question_from_db.correct_answer,
                    "explanation": question_from_db.explanation
                })

            # Track this question answer for arrhythmia breakdown
            question_answers.append({
                "question_id": question_id,
                "is_correct": is_correct,
                "correct_class": question_from_db.correct_class
            })

            # Record attempt
            ECGService.create_practice_attempt(
                db=db,
                user_id=current_user.id,
                question_id=question_id,
                selected_answer=selected_answer,
                is_correct=is_correct,
                time_spent_seconds=answer.get("time_spent_seconds", 0),
            )

        # Update practice progress counters
        ProgressService.update_progress(
            db=db,
            user_id=current_user.id,
            practice_attempts=total_attempts,
            correct_answers=score,
        )

        # Calculate new skill level
        total = len(test_questions)
        accuracy = (score / total) * 100 if total > 0 else 0
        new_skill_level = ECGService.calculate_skill_level(accuracy)

        # Update progress
        progress = ProgressService.get_or_create_progress(db, current_user.id)
        previous_level = current_user.skill_level
        
        logger.info(
            f"Post-practice test scoring: score={score}/{total} (accuracy={accuracy:.1f}%), "
            f"new_skill_level={new_skill_level}, previous_level={previous_level}"
        )

        progress.post_practice_tests_taken += 1
        progress.post_practice_score = accuracy
        progress.post_practice_level_achieved = new_skill_level

        # Update user skill level to the new level from this test
        current_user.skill_level = new_skill_level
        if previous_level is None:
            logger.info(
                f"User {current_user.id} assigned initial level {new_skill_level} from post-practice test"
            )
        elif new_skill_level != previous_level:
            logger.info(
                f"User {current_user.id} level updated from {previous_level} to {new_skill_level}"
            )

        db.add(progress)
        db.add(current_user)
        db.commit()

        # Save post-practice test result with question answers for arrhythmia breakdown
        import json
        post_test = PostPracticeTest(
            user_id=current_user.id,
            score=score,
            total=total,
            accuracy=accuracy,
            previous_level=previous_level,
            new_level=new_skill_level,
            level_improved=str(new_skill_level > previous_level if previous_level else False),
            question_answers=json.dumps(question_answers),
        )
        db.add(post_test)
        db.commit()

        # Generate recommendations using LLM
        recommendations = LLMService.generate_recommendations(
            wrong_questions=wrong_questions,
            skill_level=new_skill_level,
            previous_level=previous_level,
        )

        logger.info(
            f"User {current_user.id} completed post-practice test with score {score}/{total} "
            f"(accuracy: {accuracy}%, new_level: {new_skill_level})"
        )

        return {
            "success": True,
            "score": score,
            "total": total,
            "accuracy": accuracy,
            "previous_level": previous_level,
            "new_level": new_skill_level,
            "level_improved": new_skill_level > previous_level if previous_level else False,
            "recommendations": recommendations,
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error in post-practice test: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete post-practice test",
        ) from exc
