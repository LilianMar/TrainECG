"""
Script to load practice questions from JSON file into the database.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.session import SessionLocal
from app.models.ecg import PracticeQuestion, ArrhythmiaClassEnum


# Mapping from JSON arrhythmia types to database enum
ARRHYTHMIA_TYPE_MAPPING = {
    "atrial_fibrillation": ArrhythmiaClassEnum.ATRIAL_FIBRILLATION,
    "ventricular_tachycardia": ArrhythmiaClassEnum.VENTRICULAR_TACHYCARDIA,
    "av_block": ArrhythmiaClassEnum.AV_BLOCK,
    "atrial_flutter": ArrhythmiaClassEnum.ATRIAL_FLUTTER,
    "svt_paroxysmal": ArrhythmiaClassEnum.NORMAL,  # Map to NORMAL for now
    "wandering_atrial_pacemaker": ArrhythmiaClassEnum.NORMAL,
    "premature_atrial_complex": ArrhythmiaClassEnum.NORMAL,
    "ventricular_fibrillation": ArrhythmiaClassEnum.VENTRICULAR_TACHYCARDIA,
    "asystole": ArrhythmiaClassEnum.NORMAL,
    "pvc_quadrigeminy": ArrhythmiaClassEnum.NORMAL,
    "torsade_de_pointes": ArrhythmiaClassEnum.VENTRICULAR_TACHYCARDIA,
    "sinus_tachycardia": ArrhythmiaClassEnum.NORMAL,
    "sinus_bradycardia": ArrhythmiaClassEnum.NORMAL,
}


def load_questions_from_json(json_path: str):
    """Load practice questions from JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['questions']


def seed_database(questions: list, image_base_path: str = "/app/uploads/practice_ecgs/"):
    """Insert questions into the database."""
    db = SessionLocal()
    
    try:
        # Clear existing questions
        print("\nClearing existing practice questions...")
        deleted_count = db.query(PracticeQuestion).delete()
        db.commit()
        print(f"✓ Deleted {deleted_count} existing questions")
        
        print(f"\nInserting {len(questions)} questions into database...")
        
        inserted_count = 0
        for q in questions:
            # Map arrhythmia type
            arrhythmia_type = ARRHYTHMIA_TYPE_MAPPING.get(
                q['arrhythmia_type'], 
                ArrhythmiaClassEnum.NORMAL
            )
            
            # Create question object
            question_obj = PracticeQuestion(
                image_filename=q['image_filename'],
                image_path=f"{image_base_path}{q['image_filename']}",
                question_text=q['question_text'],
                correct_answer=q['correct_answer'],
                option_a=q['option_a'],
                option_b=q['option_b'],
                option_c=q['option_c'],
                option_d=q['option_d'],
                explanation=q['explanation'],
                correct_class=arrhythmia_type,
                difficulty_level=q.get('difficulty_level', 2)
            )
            
            db.add(question_obj)
            inserted_count += 1
            print(f"  ✓ [{inserted_count:2d}/{len(questions)}] Caso {q['case_number']}, Pregunta {q['question_number']}: {q['question_text'][:50]}...")
        
        db.commit()
        print(f"\n✅ Successfully inserted {inserted_count} questions!")
        
        # Verify insertion
        total = db.query(PracticeQuestion).count()
        print(f"✓ Database now contains {total} practice questions")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


def main():
    # Paths
    base_dir = Path(__file__).parent
    json_path = base_dir / "train" / "ecg_questions.json"
    
    if not json_path.exists():
        print(f"❌ Error: JSON file not found at {json_path}")
        print(f"   Base dir: {base_dir}")
        print(f"   Script location: {Path(__file__).absolute()}")
        return
    
    print("="*70)
    print("ECG Practice Questions Seeding Script")
    print("="*70)
    
    # Load questions from JSON
    print(f"\n📝 Loading questions from JSON...")
    questions = load_questions_from_json(str(json_path))
    print(f"✓ Loaded {len(questions)} questions from JSON")
    
    # Seed database
    print("\n💾 Seeding database...")
    seed_database(questions)
    
    print("\n" + "="*70)
    print("✅ Seeding completed successfully!")
    print("="*70)


if __name__ == "__main__":
    main()
