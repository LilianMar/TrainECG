"""
Script para cargar preguntas desde backend/train/ecg_questions.json
Ejecutar con: python load_train_questions.py
"""

import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings
from app.models.ecg import PracticeQuestion
from app.database.base import Base

settings = get_settings()
engine = create_engine(str(settings.DATABASE_URL))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables first
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Load questions from JSON
json_path = Path(__file__).parent / "train" / "ecg_questions.json"

print(f"📖 Cargando preguntas desde: {json_path}")

if not json_path.exists():
    print(f"❌ Archivo no encontrado: {json_path}")
    sys.exit(1)

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

questions_data = data.get("questions", [])
print(f"📊 Total de preguntas en JSON: {len(questions_data)}")

# Check existing questions
existing_count = db.query(PracticeQuestion).count()
print(f"📊 Preguntas ya en BD: {existing_count}")

added = 0
skipped = 0

for q in questions_data:
    try:
        # Check if already exists (by image_path + question_text)
        existing = db.query(PracticeQuestion).filter_by(
            image_path=q.get("image_path"),
            question_text=q.get("question_text")
        ).first()

        if existing:
            skipped += 1
            continue

        # Create image path from filename if not provided
        image_filename = q.get("image_filename", "")
        image_path = q.get("image_path")
        
        if not image_path:
            # Construct path based on filename
            if image_filename.startswith("ecg_case"):
                image_path = f"/uploads/practice_ecgs/{image_filename}"
            else:
                image_path = f"/uploads/practice_ecgs/{image_filename}"

        # Create question object
        question = PracticeQuestion(
            image_filename=image_filename,
            image_path=image_path,
            question_text=q.get("question_text", ""),
            option_a=q.get("option_a", ""),
            option_b=q.get("option_b", ""),
            option_c=q.get("option_c", ""),
            option_d=q.get("option_d", ""),
            correct_answer=q.get("correct_answer", 0),
            explanation=q.get("explanation", ""),
            correct_class=q.get("arrhythmia_type", "normal"),
            difficulty_level=q.get("difficulty_level", 1),
        )

        db.add(question)
        added += 1

    except Exception as e:
        print(f"⚠️ Error procesando pregunta: {e}")
        continue

try:
    db.commit()
    total_now = db.query(PracticeQuestion).count()
    
    print(f"\n{'='*50}")
    print(f"✅ Carga completada")
    print(f"{'='*50}")
    print(f"  ✓ Preguntas añadidas: {added}")
    print(f"  ⊘ Preguntas omitidas (duplicadas): {skipped}")
    print(f"  📊 Total en BD ahora: {total_now}")
    print(f"{'='*50}")
    
except Exception as e:
    db.rollback()
    print(f"❌ Error al guardar: {e}")
    sys.exit(1)
finally:
    db.close()
