#!/usr/bin/env python3
"""
Insert additional achievements/badges into the database.
"""

import sqlite3
from datetime import datetime

DB_PATH = "ecg_app.db"

# Define badges to insert
NEW_ACHIEVEMENTS = [
    {
        "user_id": 1,
        "achievement_type": "arrhythmia_master",
        "badge_name": "Maestro de Ritmos",
        "description": "Domina 3+ tipos de arritmia con 85%+ precisión",
        "icon": "🎼",
        "color": "warning"
    },
    {
        "user_id": 1,
        "achievement_type": "af_specialist",
        "badge_name": "Especialista FA",
        "description": "Alcanzaste 90%+ en análisis de Fibrilación Auricular",
        "icon": "💓",
        "color": "danger"
    },
    {
        "user_id": 1,
        "achievement_type": "vt_analyzer",
        "badge_name": "Analista VT",
        "description": "Experto en identificación de Taquicardia Ventricular",
        "icon": "⚡",
        "color": "danger"
    },
    {
        "user_id": 1,
        "achievement_type": "rapid_learner",
        "badge_name": "Aprendiz Rápido",
        "description": "Mejoraste 25%+ en tu primer mes",
        "icon": "🚀",
        "color": "success"
    },
    {
        "user_id": 1,
        "achievement_type": "consistency_streak",
        "badge_name": "Consistente",
        "description": "Mantuviste una racha de 7 días de práctica",
        "icon": "🔥",
        "color": "warning"
    },
    {
        "user_id": 1,
        "achievement_type": "ecg_analyst",
        "badge_name": "Analista ECG Pro",
        "description": "Analizaste 100+ ECGs correctamente",
        "icon": "📊",
        "color": "info"
    },
    {
        "user_id": 1,
        "achievement_type": "test_master",
        "badge_name": "Maestro de Tests",
        "description": "Completaste 10+ tests post-práctica",
        "icon": "✅",
        "color": "success"
    },
    {
        "user_id": 1,
        "achievement_type": "normal_rhythm_expert",
        "badge_name": "Experto en Ritmo Normal",
        "description": "Alcanzaste 95%+ en identificación de ritmo normal sinusal",
        "icon": "💚",
        "color": "success"
    },
]

def insert_achievements():
    """Insert new achievements into the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        for achievement in NEW_ACHIEVEMENTS:
            cursor.execute(
                """
                INSERT INTO user_achievements 
                (user_id, achievement_type, badge_name, description, icon, color, earned_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    achievement["user_id"],
                    achievement["achievement_type"],
                    achievement["badge_name"],
                    achievement["description"],
                    achievement["icon"],
                    achievement["color"],
                    now,
                    now
                )
            )
        
        conn.commit()
        print(f"✅ Insertados {len(NEW_ACHIEVEMENTS)} insignias adicionales")
        
        # Show all achievements for user 1
        cursor.execute("SELECT badge_name, icon, description FROM user_achievements WHERE user_id = 1 ORDER BY earned_at DESC")
        rows = cursor.fetchall()
        print(f"\n📦 Total de insignias para usuario 1: {len(rows)}")
        for badge_name, icon, description in rows:
            print(f"  {icon} {badge_name}: {description}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    insert_achievements()
