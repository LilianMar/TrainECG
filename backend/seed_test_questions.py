"""
Script to seed initial test questions in the database.
Run with: python seed_test_questions.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings
from app.models.ecg import PracticeQuestion, ArrhythmiaClassEnum
from app.database.base import Base

settings = get_settings()

# Create database connection
engine = create_engine(str(settings.DATABASE_URL))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Sample test questions
TEST_QUESTIONS = [
    {
        "image_filename": "sample_ecg_1.jpg",
        "image_path": "/uploads/sample_1.jpg",
        "question_text": "¿Qué tipo de arritmia se observa en este ECG?",
        "option_a": "Ritmo sinusal normal",
        "option_b": "Fibrilación auricular",
        "option_c": "Taquicardia ventricular",
        "option_d": "Bloqueo AV",
        "correct_answer": 1,  # B
        "explanation": "La fibrilación auricular se caracteriza por la ausencia de ondas P y una línea base irregular con ondulaciones de alta frecuencia. Los intervalos RR son irregulares.",
        "correct_class": ArrhythmiaClassEnum.ATRIAL_FIBRILLATION.value,
        "difficulty_level": 1
    },
    {
        "image_filename": "sample_ecg_2.jpg",
        "image_path": "/uploads/sample_2.jpg",
        "question_text": "Identifica la arritmia en este registro de 12 derivaciones:",
        "option_a": "Aleteo auricular",
        "option_b": "Bloqueo AV de segundo grado",
        "option_c": "Taquicardia ventricular sostenida",
        "option_d": "Ritmo idioventricular",
        "correct_answer": 2,  # C
        "explanation": "La taquicardia ventricular sostenida muestra tres o más complejos enlazados sin conducción sinusal. Presenta complejos QRS anchos (>120ms) a una frecuencia rápida (>100 bpm).",
        "correct_class": ArrhythmiaClassEnum.VENTRICULAR_TACHYCARDIA.value,
        "difficulty_level": 2
    },
    {
        "image_filename": "sample_ecg_3.jpg",
        "image_path": "/uploads/sample_3.jpg",
        "question_text": "¿Cuál es el diagnóstico predominante en este ECG?",
        "option_a": "Ritmo sinusal normal",
        "option_b": "Bloqueo auriculoventricular de primer grado",
        "option_c": "Bloqueo auriculoventricular de segundo grado Mobitz I",
        "option_d": "Bloqueo auriculoventricular completo",
        "correct_answer": 3,  # D
        "explanation": "El bloqueo AV completo (BAV de 3er grado) se caracteriza por ausencia total de conducción entre aurículas y ventrículos. Las aurículas y ventrículos laten independientemente con diferentes frecuencias.",
        "correct_class": ArrhythmiaClassEnum.AV_BLOCK.value,
        "difficulty_level": 2
    },
    {
        "image_filename": "sample_ecg_4.jpg",
        "image_path": "/uploads/sample_4.jpg",
        "question_text": "Analiza este trazo y determina el ritmo:",
        "option_a": "Ritmo sinusal normal",
        "option_b": "Aleteo auricular",
        "option_c": "Fibrilación ventricular",
        "option_d": "Asistolia",
        "correct_answer": 0,  # A
        "explanation": "El ritmo sinusal normal presenta: ondas P regulares y positivas en derivaciones estándar, intervalos PR constantes, complejos QRS estrechos regulares (60-100 bpm), y onda T normal.",
        "correct_class": ArrhythmiaClassEnum.NORMAL.value,
        "difficulty_level": 1
    },
    {
        "image_filename": "sample_ecg_5.jpg",
        "image_path": "/uploads/sample_5.jpg",
        "question_text": "¿Qué tipo de flutter se observa aquí?",
        "option_a": "Fibrilación auricular",
        "option_b": "Aleteo auricular típico",
        "option_c": "Taquicardia supraventricular",
        "option_d": "Bloqueo de rama",
        "correct_answer": 1,  # B
        "explanation": "El aleteo auricular típico se caracteriza por ondas F (flutter) de 250-350 bpm con patrón de 'diente de sierra' entre los complejos QRS, respuesta ventricular generalmente regular.",
        "correct_class": ArrhythmiaClassEnum.ATRIAL_FLUTTER.value,
        "difficulty_level": 2
    }
]


def seed_questions():
    """Seed test questions into the database."""
    db = SessionLocal()
    
    try:
        print("🌱 Iniciando inserción de preguntas de prueba...")
        
        # Check if questions already exist
        existing_count = db.query(PracticeQuestion).count()
        if existing_count > 0:
            print(f"ℹ️  Ya hay {existing_count} preguntas en la base de datos")
        
        # Insert test questions
        for question_data in TEST_QUESTIONS:
            # Check if this question already exists
            existing = db.query(PracticeQuestion).filter(
                PracticeQuestion.image_path == question_data["image_path"]
            ).first()
            
            if existing:
                print(f"⏭️  Pregunta ya existe: {question_data['image_filename']}")
                continue
            
            question = PracticeQuestion(**question_data)
            db.add(question)
            print(f"✅ Agregada pregunta: {question_data['question_text'][:50]}...")
        
        db.commit()
        print(f"\n✨ Se insertar {len(TEST_QUESTIONS)} preguntas de prueba exitosamente")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error durante la inserción: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Database Seeder - Test Questions")
    print("=" * 60)
    seed_questions()
    print("=" * 60)
