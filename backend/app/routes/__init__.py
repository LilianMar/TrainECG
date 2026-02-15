"""
Routes module - Exports all API route modules.
"""

from app.routes import auth, users, health

__all__ = ["auth", "users", "health"]
