#!/usr/bin/env python3
"""
Script standalone para resetear la BD sin depender del app
"""

import os
import json
import sys
from pathlib import Path

# Cambiar a directorio de backend
os.chdir(Path(__file__).parent)

# Crear la BD directamente con SQLite
import sqlite3

DB_PATH = "ecg_app.db"

print("=" * 50)
print("🔄 Reseteando Base de Datos (Standalone)")
print("=" * 50)
print()

# 1. Borrar BD vieja
print("1️⃣ Borrando base de datos antigua...")
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("   ✅ Borrado")
else:
    print("   ℹ️ BD no existía")

# 2. Crear tablas
print()
print("2️⃣ Creando tablas nuevas...")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Crear tabla users
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    user_type VARCHAR(50) DEFAULT 'student',
    institution VARCHAR(255),
    is_active BOOLEAN DEFAULT 1,
    is_verified BOOLEAN DEFAULT 0,
    skill_level INTEGER,
    initial_test_completed BOOLEAN DEFAULT 0,
    initial_test_score INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
)
''')

# Crear tabla practice_questions
cursor.execute('''
CREATE TABLE IF NOT EXISTS practice_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_filename VARCHAR(255),
    image_path VARCHAR(255),
    question_text TEXT,
    option_a TEXT,
    option_b TEXT,
    option_c TEXT,
    option_d TEXT,
    correct_answer INTEGER,
    explanation TEXT,
    correct_class VARCHAR(100),
    difficulty_level INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Crear tabla practice_attempts
cursor.execute('''
CREATE TABLE IF NOT EXISTS practice_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    selected_answer INTEGER,
    is_correct VARCHAR(10),
    time_spent_seconds INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(question_id) REFERENCES practice_questions(id)
)
''')

# Crear tabla user_progress
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    total_ecgs_analyzed INTEGER DEFAULT 0,
    classification_accuracy FLOAT DEFAULT 0.0,
    total_practice_attempts INTEGER DEFAULT 0,
    practice_accuracy FLOAT DEFAULT 0.0,
    total_practice_correct INTEGER DEFAULT 0,
    post_practice_tests_taken INTEGER DEFAULT 0,
    post_practice_score FLOAT,
    post_practice_level_achieved INTEGER,
    current_streak_days INTEGER DEFAULT 0,
    longest_streak_days INTEGER DEFAULT 0,
    last_activity_date TIMESTAMP,
    total_achievements INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

conn.commit()
print("   ✅ Tablas creadas")

# 3. Cargar preguntas desde JSON
print()
print("3️⃣ Cargando preguntas de entrenamiento...")

json_path = Path("train/ecg_questions.json")
if json_path.exists():
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    questions = data.get("questions", [])
    added = 0
    
    for q in questions:
        try:
            image_filename = q.get("image_filename", "")
            image_path = q.get("image_path")
            
            if not image_path:
                image_path = f"/uploads/practice_ecgs/{image_filename}"
            
            cursor.execute('''
            INSERT INTO practice_questions 
            (image_filename, image_path, question_text, option_a, option_b, 
             option_c, option_d, correct_answer, explanation, correct_class, difficulty_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                image_filename,
                image_path,
                q.get("question_text", ""),
                q.get("option_a", ""),
                q.get("option_b", ""),
                q.get("option_c", ""),
                q.get("option_d", ""),
                q.get("correct_answer", 0),
                q.get("explanation", ""),
                q.get("arrhythmia_type", "normal"),
                q.get("difficulty_level", 1)
            ))
            added += 1
        except Exception as e:
            print(f"   ⚠️ Error en pregunta: {e}")
            pass
    
    conn.commit()
    print(f"   ✅ {added} preguntas cargadas")
else:
    print(f"   ⚠️ JSON no encontrado: {json_path}")

# Verificar total
cursor.execute("SELECT COUNT(*) FROM practice_questions")
total = cursor.fetchone()[0]

conn.close()

print()
print("=" * 50)
print("✅ Base de datos lista!")
print("=" * 50)
print(f"  📊 Total de preguntas: {total}")
print(f"  💾 BD ubicada en: {DB_PATH}")
print()
