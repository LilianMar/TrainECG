"""
Main FastAPI application factory and startup/shutdown handlers.
"""

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.config import get_settings
from app.database import engine, Base
from app.routes import auth, users, health, ecg, practice, progress, achievements
from app.middleware.cors import setup_cors_middleware
from app.middleware.logging import setup_logging_middleware
from app.utils.logger import get_logger, ensure_upload_directory, ensure_logs_directory
from app.ml_pipeline.model_manager import get_model_manager

logger = get_logger(__name__)
settings = get_settings()


def create_tables():
    """Create database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise


def load_ml_model():
    """Load ML model on startup."""
    try:
        model_manager = get_model_manager()
        logger.info("ML model loaded successfully")
    except Exception as e:
        logger.warning(f"ML model not available: {str(e)}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan.
    Runs startup code before yielding and shutdown code after yielding.
    """
    # Startup
    logger.info("Starting ECG Insight Mentor API...")
    ensure_logs_directory()
    ensure_upload_directory()
    create_tables()
    load_ml_model()
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ECG Insight Mentor API...")
    logger.info("Application shut down successfully")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version=settings.API_VERSION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Setup middleware
    # Note: Middleware is executed in reverse order (LIFO), so CORS should be added LAST
    # to be executed FIRST in the request chain
    setup_logging_middleware(app)
    setup_cors_middleware(app)

    # Include routers
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(ecg.router)
    app.include_router(practice.router)
    app.include_router(progress.router)
    app.include_router(achievements.router)

    # Mount static files for practice ECG images
    uploads_path = Path(__file__).parent.parent / "uploads"
    if uploads_path.exists():
        app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")
        logger.info(f"Static files mounted at /uploads from {uploads_path}")

    logger.info("FastAPI application created successfully")
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
