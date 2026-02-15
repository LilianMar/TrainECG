"""
Core module for ECG Insight Mentor API.
Exposes configuration and main setup functions.
"""

from app.core.config import Settings, get_settings

__all__ = ["Settings", "get_settings"]
