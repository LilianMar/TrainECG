"""
Configuration module for ECG Insight Mentor API.
Handles environment variables, settings and app configuration.
"""

from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # === API CONFIG ===
    API_TITLE: str = "ECG Insight Mentor API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Platform for ECG training with AI support"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # === DATABASE ===
    DATABASE_URL: str = "sqlite:///./ecg_app.db"
    DATABASE_ECHO: bool = False

    # === SECURITY ===
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # === CORS ===
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:9000",
    ]

    # === LLM / OpenAI ===
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS: int = 300
    OPENAI_TEMPERATURE: float = 0.6
    
    # Legacy LLM settings (kept for compatibility)
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-3.5-turbo"
    LLM_TEMPERATURE: float = 0.7

    # === ML MODEL ===
    MODEL_PATH: str = "./models/best_model_Hybrid_CNN_LSTM_Attention.h5"
    IMAGE_SIZE: int = 128
    WINDOW_SIZE: int = 128
    WINDOW_OVERLAP: float = 0.5

    # === UPLOADS ===
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png"]
    UPLOAD_DIR: str = "./uploads"

    # === LOGGING ===
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
