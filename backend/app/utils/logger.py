"""
Logging configuration.
"""

import logging
import logging.config
from pathlib import Path
from app.core.config import get_settings

settings = get_settings()

# Ensure logs directory exists
logs_dir = Path("./logs")
logs_dir.mkdir(exist_ok=True, parents=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s %(funcName)s:%(lineno)d - %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "detailed",
            "filename": f"{logs_dir}/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
    },
    "root": {
        "level": settings.LOG_LEVEL,
        "handlers": ["console", "file"],
    },
    "loggers": {
        "app": {
            "level": settings.LOG_LEVEL,
            "handlers": ["console", "file"],
            "propagate": False,
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("app")


def get_logger(name: str = "app") -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)


def ensure_logs_directory():
    """Ensure logs directory exists."""
    logs_dir = Path("./logs")
    logs_dir.mkdir(exist_ok=True, parents=True)
    logger.info(f"Logs directory ensured at {logs_dir.absolute()}")


def ensure_upload_directory():
    """Ensure uploads directory exists."""
    uploads_dir = Path("./uploads")
    uploads_dir.mkdir(exist_ok=True, parents=True)
    logger.info(f"Uploads directory ensured at {uploads_dir.absolute()}")
