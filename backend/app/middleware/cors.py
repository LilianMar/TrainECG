"""
CORS middleware configuration.
"""

from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings

settings = get_settings()


def setup_cors_middleware(app):
    """Configure CORS middleware for the application."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
