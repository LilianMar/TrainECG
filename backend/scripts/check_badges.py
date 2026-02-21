#!/usr/bin/env python3
"""Check badge definitions and database."""

import sys
sys.path.insert(0, '.')
import sqlite3
from app.models.achievement import BADGE_DEFINITIONS

print("=" * 70)
print("📋 BADGE DEFINITIONS DISPONIBLES:")
print("=" * 70)
print(f"\nTotal de insignias definidas: {len(BADGE_DEFINITIONS)}\n")

for idx, (key, badge) in enumerate(BADGE_DEFINITIONS.items(), 1):
    print(f"{idx:2}. {badge['icon']} {badge['name']}")
    print(f"    └─ {badge['description']}")

print("\n" + "=" * 70)
print("✅ BASE DE DATOS - INSIGNIAS DESBLOQUEADAS PARA USUARIO 1:")
print("=" * 70)

conn = sqlite3.connect('ecg_app.db')
cursor = conn.cursor()
cursor.execute("""
    SELECT achievement_type, badge_name, icon, earned_at 
    FROM user_achievements 
    WHERE user_id = 1 
    ORDER BY earned_at DESC
""")

rows = cursor.fetchall()
print(f"\nTotal desbloqueadas: {len(rows)}\n")
for achievement_type, badge_name, icon, earned_at in rows:
    print(f"  ✓ {icon} {badge_name}")

conn.close()
