"""
Utility functions for the application.
"""

import os
import logging
from typing import List
from pathlib import Path

logger = logging.getLogger(__name__)


def ensure_upload_directory() -> str:
    """
    Ensure upload directory exists.
    
    Returns:
        Path to upload directory
    """
    upload_dir = Path("./uploads")
    upload_dir.mkdir(exist_ok=True, parents=True)
    return str(upload_dir)


def ensure_logs_directory() -> str:
    """
    Ensure logs directory exists.
    
    Returns:
        Path to logs directory
    """
    logs_dir = Path("./logs")
    logs_dir.mkdir(exist_ok=True, parents=True)
    return str(logs_dir)


def is_file_extension_allowed(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Check if file extension is in allowed list.
    
    Args:
        filename: Original filename
        allowed_extensions: List of allowed extensions (without dots)
    
    Returns:
        True if extension is allowed, False otherwise
    """
    if "." not in filename:
        return False
    
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in allowed_extensions


def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in megabytes.
    
    Args:
        file_path: Path to file
    
    Returns:
        File size in MB
    """
    return os.path.getsize(file_path) / (1024 * 1024)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal.
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    # Remove path separators and special characters
    filename = os.path.basename(filename)
    # Keep only alphanumeric, dots, and underscores
    import re
    filename = re.sub(r'[^\w\s.-]', '', filename)
    return filename
