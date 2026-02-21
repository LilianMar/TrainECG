#!/usr/bin/env python3
"""Reset achievements to only earned ones."""

import sqlite3
from datetime import datetime

DB_PATH = "ecg_app.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Delete all achievements for user 1
cursor.execute("DELETE FROM user_achievements WHERE user_id = 1")

# Insert only the 3 core achievements that have been earned
now = datetime.now().isoformat()

achievements = [
    (1, "diagnostic_complete", "Iniciado", "Completaste tu primer test diagnóstico", "■", "primary", now, now),
    (1, "improvement_15", "Progresista", "Mejoraste 15%+ vs tu test inicial", "▶", "success", now, now),
    (1, "score_90", "Campeón", "Obtuviste 90%+ en un test post-práctica", "★", "warning", now, now),
]

for user_id, achievement_type, badge_name, description, icon, color, earned_at, created_at in achievements:
    cursor.execute(
        """
        INSERT INTO user_achievements 
        (user_id, achievement_type, badge_name, description, icon, color, earned_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, achievement_type, badge_name, description, icon, color, earned_at, created_at)
    )

conn.commit()

# Verify
cursor.execute("SELECT COUNT(*) FROM user_achievements WHERE user_id = 1")
count = cursor.fetchone()[0]
print(f"✅ Limpiada tabla: {count} insignias desbloqueadas para usuario 1")

# Show all badges (earned)
cursor.execute("SELECT badge_name, icon, description, earned_at FROM user_achievements WHERE user_id = 1")
rows = cursor.fetchall()
for badge_name, icon, description, earned_at in rows:
    print(f"  {icon} {badge_name} - Desbloqueada")

conn.close()
