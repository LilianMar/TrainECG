"""
Routes module - Exports all API route modules.
"""

from app.routes import auth, users, health, ecg, practice, progress

__all__ = ["auth", "users", "health", "ecg", "practice", "progress"]
