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

test_questions = [
    {'image_filename': 'test_1.jpg', 'image_path': '/uploads/test_1.jpg', 'question_text': 'Pregunta 1: arritmia', 'option_a': 'Normal', 'option_b': 'FA', 'option_c': 'TV', 'option_d': 'AV Block', 'correct_answer': 1, 'explanation': 'FA.', 'correct_class': 'atrial_fibrillation', 'difficulty_level': 1},
    {'image_filename': 'test_2.jpg', 'image_path': '/uploads/test_2.jpg', 'question_text': 'Pregunta 2: ritmo', 'option_a': 'Flutter', 'option_b': 'TV', 'option_c': 'Normal', 'option_d': 'Bradi', 'correct_answer': 2, 'explanation': 'Normal.', 'correct_class': 'normal', 'difficulty_level': 1},
    {'image_filename': 'test_3.jpg', 'image_path': '/uploads/test_3.jpg', 'question_text': 'Pregunta 3: diagnostico', 'option_a': 'Normal', 'option_b': 'AV Block', 'option_c': 'TV', 'option_d': 'FA rapida', 'correct_answer': 2, 'explanation': 'TV.', 'correct_class': 'ventricular_tachycardia', 'difficulty_level': 2},
    {'image_filename': 'test_4.jpg', 'image_path': '/uploads/test_4.jpg', 'question_text': 'Pregunta 4: analiza', 'option_a': 'AV Block', 'option_b': 'FA', 'option_c': 'Normal', 'option_d': 'Paro', 'correct_answer': 0, 'explanation': 'AV Block.', 'correct_class': 'av_block', 'difficulty_level': 2},
    {'image_filename': 'test_5.jpg', 'image_path': '/uploads/test_5.jpg', 'question_text': 'Pregunta 5: observa', 'option_a': 'TV', 'option_b': 'Flutter', 'option_c': 'Normal', 'option_d': 'Bradicardia', 'correct_answer': 1, 'explanation': 'Flutter.', 'correct_class': 'atrial_flutter', 'difficulty_level': 1},
]

added = 0
for q in test_questions:
    existing = db.query(PracticeQuestion).filter_by(image_path=q['image_path']).first()
    if not existing:
        db.add(PracticeQuestion(**q))
        added += 1

db.commit()
total = db.query(PracticeQuestion).count()
print(f'Success: {added} added, Total: {total}')
