#!/usr/bin/env python3
"""Display all available badges with their status."""

import sqlite3

DB_PATH = "ecg_app.db"

# Badge definitions matching the backend
BADGES = {
    # Classification & Analysis
    "first_ecg_classified": ("◆", "Clasificador ECG", "Completaste tu primera clasificación de ECG", "primary"),
    "diagnostic_complete": ("■", "Iniciado", "Completaste tu primer test diagnóstico", "primary"),
    "hundred_ecgs": ("▲", "Analista Experto", "Analizaste 100+ ECGs correctamente", "secondary"),
    
    # Performance & Improvement  
    "improvement_15": ("▶", "Progresista", "Mejoraste 15%+ vs tu test inicial", "success"),
    "improvement_30": ("◀", "Estudiante Dedicado", "Mejoraste 30%+ vs tu test inicial", "success"),
    "score_90": ("★", "Campeón", "Obtuviste 90%+ en un test post-práctica", "warning"),
    "perfect_score": ("◆★", "Perfeccionista", "Obtuviste 100% en un test post-práctica", "warning"),
    
    # Arrhythmia Specialization
    "fa_specialist": ("●", "Especialista FA", "90%+ precisión en Fibrilación Auricular", "danger"),
    "vt_specialist": ("◇", "Especialista TV", "90%+ precisión en Taquicardia Ventricular", "warning"),
    "av_block_specialist": ("◈", "Especialista Bloqueos", "90%+ precisión en Bloqueos AV", "secondary"),
    "af_flutter_specialist": ("≈", "Especialista Flutter", "90%+ precisión en Flutter Auricular", "danger"),
    "normal_rhythm_specialist": ("◯", "Experto Ritmo Normal", "95%+ precisión en Ritmo Normal Sinusal", "success"),
    
    # Testing & Persistence
    "three_tests": ("◬", "Persistente", "Completaste 3 tests post-práctica", "primary"),
    "ten_tests": ("◭", "Maestro de Tests", "Completaste 10 tests post-práctica", "success"),
    "practice_streak": ("¶", "En Racha", "Práctica consecutiva por 7 días", "warning"),
    
    # Practice Mastery
    "hundred_practice": ("§", "Maestro Practicante", "Completaste 100+ intentos de práctica", "success"),
    "fifty_correct": ("◊", "Aprendiz", "50+ respuestas correctas en práctica", "primary"),
}

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("\n" + "="*80)
print("📋 SISTEMA DE INSIGNIAS - TrainECG App".center(80))
print("="*80 + "\n")

# Get earned badges
cursor.execute("""
    SELECT achievement_type, badge_name, icon, earned_at 
    FROM user_achievements 
    WHERE user_id = 1 
    ORDER BY earned_at DESC
""")
earned_types = {row[0]: row for row in cursor.fetchall()}

print(f"INSIGNIAS DESBLOQUEADAS: {len(earned_types)} / {len(BADGES)}")
print("-" * 80)

for idx, (earned_type, badge_name, icon, earned_at) in enumerate(earned_types.values(), 1):
    badge_info = BADGES.get(earned_type, ("?", badge_name, ""))
    print(f"\n  ✅ [{idx}] {badge_info[0]} {badge_info[1]}")
    print(f"      └─ {badge_info[2]}")

print("\n" + "="*80)
print(f"INSIGNIAS DISPONIBLES: {len(BADGES) - len(earned_types)}")
print("-" * 80)

available_count = 0
for badge_type, (icon, name, desc, color) in BADGES.items():
    if badge_type not in earned_types:
        available_count += 1
        if available_count <= 10:  # Show first 10 available
            print(f"\n  ⏳ [{badge_type}] {icon} {name}")
            print(f"      └─ {desc}")

if len(BADGES) - len(earned_types) > 10:
    print(f"\n  ... y {len(BADGES) - len(earned_types) - 10} insignia(s) más")

print("\n" + "="*80)
print("\n✨ CATEGORÍAS DE INSIGNIAS:\n")
print("  📊 CLASIFICACIÓN & ANÁLISIS: 3 insignias")
print("     • Primera clasificación ECG, Iniciado, Analista Experto\n")

print("  📈 RENDIMIENTO & MEJORA: 4 insignias") 
print("     • Progresista, Estudiante Dedicado, Campeón, Perfeccionista\n")

print("  🏥 ESPECIALIZACIÓN ARRITMIAS: 5 insignias")
print("     • FA, TV, Bloqueos AV, Flutter, Ritmo Normal\n")

print("  🎯 TESTS & PERSISTENCIA: 3 insignias")
print("     • Persistente, Maestro de Tests, En Racha\n")

print("  💪 DOMINIO PRÁCTICA: 2 insignias")
print("     • Maestro Practicante, Aprendiz\n")

print("="*80 + "\n")

conn.close()
