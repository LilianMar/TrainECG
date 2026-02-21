#!/usr/bin/env python3
"""Display all badges with their new lucide-react icons."""

import sqlite3

DB_PATH = "ecg_app.db"

# Badge definitions matching the backend
BADGES = {
    # Classification & Analysis
    "first_ecg_classified": ("FileHeart", "Clasificador ECG", "Completaste tu primera clasificación de ECG", "primary"),
    "diagnostic_complete": ("Stethoscope", "Iniciado", "Completaste tu primer test diagnóstico", "primary"),
    "hundred_ecgs": ("Activity", "Analista Experto", "Analizaste 100+ ECGs correctamente", "secondary"),
    
    # Performance & Improvement  
    "improvement_15": ("TrendingUp", "Progresista", "Mejoraste 15%+ vs tu test inicial", "success"),
    "improvement_30": ("Rocket", "Estudiante Dedicado", "Mejoraste 30%+ vs tu test inicial", "success"),
    "score_90": ("Trophy", "Campeón", "Obtuviste 90%+ en un test post-práctica", "warning"),
    "perfect_score": ("Crown", "Perfeccionista", "Obtuviste 100% en un test post-práctica", "warning"),
    
    # Arrhythmia Specialization
    "fa_specialist": ("HeartHandshake", "Especialista FA", "90%+ precisión en Fibrilación Auricular", "danger"),
    "vt_specialist": ("Zap", "Especialista TV", "90%+ precisión en Taquicardia Ventricular", "warning"),
    "av_block_specialist": ("Shield", "Especialista Bloqueos", "90%+ precisión en Bloqueos AV", "secondary"),
    "af_flutter_specialist": ("Heart", "Especialista Flutter", "90%+ precisión en Flutter Auricular", "danger"),
    "normal_rhythm_specialist": ("HeartPulse", "Experto Ritmo Normal", "95%+ precisión en Ritmo Normal Sinusal", "success"),
    
    # Testing & Persistence
    "three_tests": ("CheckCircle", "Persistente", "Completaste 3 tests post-práctica", "primary"),
    "ten_tests": ("Target", "Maestro de Tests", "Completaste 10 tests post-práctica", "success"),
    "practice_streak": ("Flame", "En Racha", "Práctica consecutiva por 7 días", "warning"),
    
    # Practice Mastery
    "hundred_practice": ("Brain", "Maestro Practicante", "Completaste 100+ intentos de práctica", "success"),
    "fifty_correct": ("Lightbulb", "Aprendiz", "50+ respuestas correctas en práctica", "primary"),
}

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("\n" + "="*90)
print("🏆 SISTEMA DE INSIGNIAS - ICONOS LUCIDE-REACT".center(90))
print("="*90 + "\n")

# Get earned badges
cursor.execute("""
    SELECT achievement_type, badge_name, icon, earned_at 
    FROM user_achievements 
    WHERE user_id = 1 
    ORDER BY earned_at DESC
""")
earned_types = {row[0]: row for row in cursor.fetchall()}

print(f"✅ INSIGNIAS DESBLOQUEADAS: {len(earned_types)} / {len(BADGES)}")
print("-" * 90)

for idx, (earned_type, badge_name, icon, earned_at) in enumerate(earned_types.values(), 1):
    badge_info = BADGES.get(earned_type, ("?", badge_name, ""))
    icon_name = badge_info[0]
    print(f"\n  [{idx}] <{icon_name}> {badge_info[1]}")
    print(f"      └─ {badge_info[2]}")

print("\n" + "="*90)
print(f"⏳ INSIGNIAS DISPONIBLES POR DESBLOQUEAR: {len(BADGES) - len(earned_types)}")
print("-" * 90)

available_count = 0
for badge_type, (icon_name, name, desc, color) in BADGES.items():
    if badge_type not in earned_types:
        available_count += 1
        if available_count <= 12:
            print(f"\n  <{icon_name}> {name}")
            print(f"      └─ {desc}")

if len(BADGES) - len(earned_types) > 12:
    print(f"\n  ... y {len(BADGES) - len(earned_types) - 12} insignia(s) más")

print("\n" + "="*90)
print("📚 ICONOS UTILIZADOS - LUCIDE-REACT\n")

icons_used = set()
for badge_type, (icon_name, name, desc, color) in BADGES.items():
    icons_used.add(icon_name)

print("  Iconos Médicos/De Salud:")
medical_icons = ["FileHeart", "Stethoscope", "Heart", "HeartHandshake", "HeartPulse", "Activity", "Zap", "Pill"]
for icon in sorted(medical_icons):
    if icon in icons_used:
        print(f"    • <{icon}>")

print("\n  Iconos de Logro/Progreso:")
achievement_icons = ["Trophy", "Crown", "Award", "TrendingUp", "Rocket", "Target", "Flame", "CheckCircle"]
for icon in sorted(achievement_icons):
    if icon in icons_used:
        print(f"    • <{icon}>")

print("\n  Iconos de Aprendizaje:")
learning_icons = ["Brain", "Lightbulb", "Shield"]
for icon in sorted(learning_icons):
    if icon in icons_used:
        print(f"    • <{icon}>")

print("\n" + "="*90)
print("\n✨ VENTAJAS DE LUCIDE-REACT:\n")
print("  • Iconos modernos y minimalistas")
print("  • Perfecto para diseño médico/tecnológico")
print("  • >400 iconos disponibles")
print("  • Totalmente customizable (tamaño, color, peso de línea)")
print("  • Tree-shakeable (solo se importan los necesarios)")
print("  • Excelente integración con Tailwind CSS")
print("\n" + "="*90 + "\n")

conn.close()
