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
    icon = Column(String(50), default="◆")                 # Emoji or icon name
    color = Column(String(50), default="success")            # Tailwind color class
    
    # Reference to test that earned it
    test_attempt_id = Column(Integer, nullable=True)
    
    # Timestamps - earned_at is nullable for achievements not yet unlocked
    earned_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<UserAchievement(user_id={self.user_id}, badge={self.badge_name})>"


# Badge definitions
BADGE_DEFINITIONS = {
    # Classification & Analysis
    "first_ecg_classified": {
        "name": "Clasificador ECG",
        "description": "Completaste tu primera clasificación de ECG",
        "icon": "FileHeart",
        "color": "primary"
    },
    "diagnostic_complete": {
        "name": "Iniciado",
        "description": "Completaste tu primer test diagnóstico",
        "icon": "Stethoscope",
        "color": "primary"
    },
    "hundred_ecgs": {
        "name": "Analista Experto",
        "description": "Analizaste 100+ ECGs correctamente",
        "icon": "Activity",
        "color": "secondary"
    },
    
    # Performance & Improvement
    "improvement_15": {
        "name": "Progresista",
        "description": "Mejoraste 15%+ vs tu test inicial",
        "icon": "TrendingUp",
        "color": "success"
    },
    "improvement_30": {
        "name": "Estudiante Dedicado",
        "description": "Mejoraste 30%+ vs tu test inicial",
        "icon": "Rocket",
        "color": "success"
    },
    "score_90": {
        "name": "Campeón",
        "description": "Obtuviste 90%+ en un test post-práctica",
        "icon": "Trophy",
        "color": "warning"
    },
    "perfect_score": {
        "name": "Perfeccionista",
        "description": "Obtuviste 100% en un test post-práctica",
        "icon": "Crown",
        "color": "warning"
    },
    
    # Arrhythmia Specialization
    "fa_specialist": {
        "name": "Especialista FA",
        "description": "90%+ precisión en Fibrilación Auricular",
        "icon": "HeartHandshake",
        "color": "danger"
    },
    "vt_specialist": {
        "name": "Especialista TV",
        "description": "90%+ precisión en Taquicardia Ventricular",
        "icon": "Zap",
        "color": "warning"
    },
    "av_block_specialist": {
        "name": "Especialista Bloqueos",
        "description": "90%+ precisión en Bloqueos AV",
        "icon": "Shield",
        "color": "secondary"
    },
    "af_flutter_specialist": {
        "name": "Especialista Flutter",
        "description": "90%+ precisión en Flutter Auricular",
        "icon": "Heart",
        "color": "danger"
    },
    "normal_rhythm_specialist": {
        "name": "Experto Ritmo Normal",
        "description": "95%+ precisión en Ritmo Normal Sinusal",
        "icon": "HeartPulse",
        "color": "success"
    },
    
    # Testing & Persistence
    "three_tests": {
        "name": "Persistente",
        "description": "Completaste 3 tests post-práctica",
        "icon": "CheckCircle",
        "color": "primary"
    },
    "ten_tests": {
        "name": "Maestro de Tests",
        "description": "Completaste 10 tests post-práctica",
        "icon": "Target",
        "color": "success"
    },
    "practice_streak": {
        "name": "En Racha",
        "description": "Práctica consecutiva por 7 días",
        "icon": "Flame",
        "color": "warning"
    },
    
    # Practice Mastery
    "hundred_practice": {
        "name": "Maestro Practicante",
        "description": "Completaste 100+ intentos de práctica",
        "icon": "Brain",
        "color": "success"
    },
    "fifty_correct": {
        "name": "Aprendiz",
        "description": "50+ respuestas correctas en práctica",
        "icon": "Lightbulb",
        "color": "primary"
    },
}
