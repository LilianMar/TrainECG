"""
Routes module - Exports all API route modules.
"""

from app.routes import auth, users, health, ecg, practice, progress, achievements, chatbot

__all__ = ["auth", "users", "health", "ecg", "practice", "progress", "achievements", "chatbot"]
