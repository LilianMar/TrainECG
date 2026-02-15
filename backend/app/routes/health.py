"""
Health check and status routes.
"""

from fastapi import APIRouter
from app.core.config import get_settings

router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.API_TITLE,
        "version": settings.API_VERSION
    }


@router.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to ECG Insight Mentor API",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }
