"""
Chatbot routes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.chatbot import ChatbotQueryLog
from app.models.user import User
from app.routes.users import get_current_user
from app.schemas.chatbot import (
    ChatbotQueryRequest,
    ChatbotQueryResponse,
    ChatbotContext,
    ChatbotQueryContextResponse,
    ChatbotHistoryItem,
    ChatbotHistoryResponse,
)
from app.services.chatbot_service import ChatbotService
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])


@router.post("/query", response_model=ChatbotQueryResponse)
async def query_chatbot(
    request: ChatbotQueryRequest,
    current_user: User = Depends(get_current_user),
):
    """Get chatbot response from TF-IDF corpus search."""
    try:
        results = ChatbotService.search(request.question, request.top_k)
        if not results:
            return ChatbotQueryResponse(
                answer=(
                    "No encontré una respuesta exacta a tu pregunta. "
                    "Intenta reformularla o consulta la sección de Biblioteca ECG para más información."
                ),
                found=False,
                results=[],
            )

        return ChatbotQueryResponse(
            answer=results[0]["respuesta"],
            found=True,
            results=results,
        )
    except FileNotFoundError as exc:
        logger.error("Chatbot corpus not found: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Corpus de chatbot no disponible en el servidor",
        ) from exc
    except Exception as exc:
        logger.error("Chatbot query error for user %s: %s", current_user.id, str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo procesar la consulta del chatbot",
        ) from exc


@router.post("/query-context", response_model=ChatbotQueryContextResponse)
async def query_chatbot_with_context(
    request: ChatbotQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get contextual chatbot response with sources and user-tailored hints."""
    try:
        sources = ChatbotService.search(request.question, request.top_k)
        recent_error_topics = ChatbotService.get_recent_error_topics(db, current_user.id)
        skill_level = current_user.skill_level

        if not sources:
            answer = (
                "No encontré una respuesta exacta a tu pregunta. "
                "Intenta reformularla o consulta la sección de Biblioteca ECG para más información."
            )
            response = ChatbotQueryContextResponse(
                answer=answer,
                found=False,
                confidence=0.0,
                sources=[],
                context=ChatbotContext(
                    skill_level=skill_level,
                    recent_error_topics=recent_error_topics,
                ),
            )
            db.add(
                ChatbotQueryLog(
                    user_id=current_user.id,
                    question=request.question,
                    answer=response.answer,
                    confidence=response.confidence,
                    source_id=None,
                    source_category=None,
                )
            )
            db.commit()
            return response

        top_source = sources[0]
        base_answer = top_source["respuesta"]
        personalized_answer = ChatbotService.compose_personalized_answer(
            base_answer=base_answer,
            skill_level=skill_level,
            recent_error_topics=recent_error_topics,
        )

        response = ChatbotQueryContextResponse(
            answer=personalized_answer,
            found=True,
            confidence=float(top_source.get("score", 0.0)),
            sources=sources,
            context=ChatbotContext(
                skill_level=skill_level,
                recent_error_topics=recent_error_topics,
            ),
        )

        db.add(
            ChatbotQueryLog(
                user_id=current_user.id,
                question=request.question,
                answer=response.answer,
                confidence=response.confidence,
                source_id=int(top_source.get("id")),
                source_category=str(top_source.get("categoria", "")),
            )
        )
        db.commit()
        return response
    except FileNotFoundError as exc:
        logger.error("Chatbot corpus not found: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Corpus de chatbot no disponible en el servidor",
        ) from exc
    except Exception as exc:
        logger.error(
            "Chatbot contextual query error for user %s: %s",
            current_user.id,
            str(exc),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo procesar la consulta contextual del chatbot",
        ) from exc


@router.get("/history", response_model=ChatbotHistoryResponse)
async def get_chatbot_history(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return authenticated user's chatbot history."""
    safe_limit = max(1, min(limit, 100))
    rows = (
        db.query(ChatbotQueryLog)
        .filter(ChatbotQueryLog.user_id == current_user.id)
        .order_by(desc(ChatbotQueryLog.created_at))
        .limit(safe_limit)
        .all()
    )

    items = [
        ChatbotHistoryItem(
            id=row.id,
            question=row.question,
            answer=row.answer,
            confidence=float(row.confidence or 0.0),
            source_id=row.source_id,
            source_category=row.source_category,
            created_at=row.created_at,
        )
        for row in rows
    ]

    return ChatbotHistoryResponse(total=len(items), items=items)


@router.get("/sources/{source_id}")
async def get_chatbot_source(
    source_id: int,
    current_user: User = Depends(get_current_user),
):
    """Return a specific corpus source by id."""
    source = ChatbotService.get_source_by_id(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Fuente no encontrada")

    return source
