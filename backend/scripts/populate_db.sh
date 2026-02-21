#!/bin/bash
# Populate the database with test questions

docker exec trainecg-backend bash << 'EOF'
cd /app

python3 << 'PYEOF'
import sys
sys.path.insert(0, '/app')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings
from app.models.ecg import PracticeQuestion

settings = get_settings()
engine = create_engine(str(settings.DATABASE_URL))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db = SessionLocal()

# Check how many questions exist
count = db.query(PracticeQuestion).count()
print(f"Current questions in DB: {count}")

# Sample questions
test_questions = [
    {'image_filename': 'test_1.jpg', 'image_path': '/uploads/test_1.jpg', 'question_text': 'Pregunta 1: ¿Qué tipo de arritmia es esta?', 'option_a': 'Normal', 'option_b': 'FA', 'option_c': 'TV', 'option_d': 'AV Block', 'correct_answer': 1, 'explanation': 'Es fibrilación auricular.', 'correct_class': 'atrial_fibrillation', 'difficulty_level': 1},
    {'image_filename': 'test_2.jpg', 'image_path': '/uploads/test_2.jpg', 'question_text': 'Pregunta 2: Identifica esta arritmia', 'option_a': 'Flutter', 'option_b': 'TV', 'option_c': 'Normal', 'option_d': 'Bradicardia', 'correct_answer': 2, 'explanation': 'Es un ritmo sinusal normal.', 'correct_class': 'normal', 'difficulty_level': 1},
    {'image_filename': 'test_3.jpg', 'image_path': '/uploads/test_3.jpg', 'question_text': 'Pregunta 3: ¿Cuál es el diagnóstico?', 'option_a': 'Normal', 'option_b': 'AV Block C', 'option_c': 'TV sostenida', 'option_d': 'FA rápida', 'correct_answer': 2, 'explanation': 'Taquicardia ventricular sostenida.', 'correct_class': 'ventricular_tachycardia', 'difficulty_level': 2},
    {'image_filename': 'test_4.jpg', 'image_path': '/uploads/test_4.jpg', 'question_text': 'Pregunta 4: Analiza el ritmo', 'option_a': 'AV Block', 'option_b': 'FA', 'option_c': 'Normal', 'option_d': 'Paro', 'correct_answer': 0, 'explanation': 'Bloqueo AV de tercer grado.', 'correct_class': 'av_block', 'difficulty_level': 2},
    {'image_filename': 'test_5.jpg', 'image_path': '/uploads/test_5.jpg', 'question_text': 'Pregunta 5: ¿Qué arritmia observas?', 'option_a': 'TV', 'option_b': 'Flutter', 'option_c': 'Normal', 'option_d': 'Bradicardia', 'correct_answer': 1, 'explanation': 'Aleteo auricular.', 'correct_class': 'atrial_flutter', 'difficulty_level': 1},
]

added = 0
for q in test_questions:
    existing = db.query(PracticeQuestion).filter_by(image_path=q['image_path']).first()
    if not existing:
        question = PracticeQuestion(**q)
        db.add(question)
        added += 1
        print(f"Added: {q['question_text']}")
    else:
        print(f"Already exists: {q['image_path']}")

db.commit()
print(f"\n✅ Successfully added {added} test questions")
print(f"Total questions now: {db.query(PracticeQuestion).count()}")
PYEOF

EOF
