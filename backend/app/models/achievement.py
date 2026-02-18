"""
SQLAlchemy models for user achievements and badges.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.database.base import Base


class UserAchievement(Base):
    """Model for tracking user achievements and badges."""

    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Achievement details
    achievement_type = Column(String(100), nullable=False)  # e.g., "improve_15_percent"
    badge_name = Column(String(100), nullable=False)        # e.g., "Progresista"
    description = Column(Text, nullable=False)
    icon = Column(String(50), default="🏆")                 # Emoji or icon name
    color = Column(String(50), default="success")            # Tailwind color class
    
    # Reference to test that earned it
    test_attempt_id = Column(Integer, nullable=True)
    
    # Timestamps
    earned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<UserAchievement(user_id={self.user_id}, badge={self.badge_name})>"


# Badge definitions
BADGE_DEFINITIONS = {
    "diagnostic_complete": {
        "name": "Iniciado",
        "description": "Completaste tu primer test diagnóstico",
        "icon": "🎯",
        "color": "primary"
    },
    "improvement_15": {
        "name": "Progresista",
        "description": "Mejoraste 15%+ vs tu test inicial",
        "icon": "📈",
        "color": "success"
    },
    "score_90": {
        "name": "Campeón",
        "description": "Obtuviste 90%+ en un test post-práctica",
        "icon": "👑",
        "color": "warning"
    },
    "master_fa": {
        "name": "Especialista en FA",
        "description": "90%+ precisión en Fibrilación Auricular",
        "icon": "❤️",
        "color": "destructive"
    },
    "master_vt": {
        "name": "Especialista en TV",
        "description": "90%+ precisión en Taquicardia Ventricular",
        "icon": "⚡",
        "color": "warning"
    },
    "master_av_block": {
        "name": "Especialista en Bloqueos",
        "description": "90%+ precisión en Bloqueos AV",
        "icon": "🔒",
        "color": "secondary"
    },
    "three_tests": {
        "name": "Maestro Diagnosticador",
        "description": "Completaste 3 tests post-práctica",
        "icon": "🧠",
        "color": "primary"
    },
    "hundred_correct": {
        "name": "Estudiante Dedicado",
        "description": "100+ respuestas correctas en práctica",
        "icon": "📚",
        "color": "success"
    }
}
