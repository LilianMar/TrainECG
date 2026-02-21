#!/usr/bin/env python
"""Check accuracy calculation"""
import sys
import os
sys.path.insert(0, '/app')
os.chdir('/app')

from app.database.session import SessionLocal
from app.services.progress_service import ProgressService

db = SessionLocal()
try:
    # Get performance data
    performance = ProgressService.get_arrhythmia_performance(db, 1)
    
    # Calculate like in generate_recommendations
    total_correct = 0
    total_questions = 0
    
    print('=== BREAKDOWN BY ARRHYTHMIA ===')
    for arrhythmia, stats in performance.items():
        practice_total = stats.get('practice_total', 0)
        practice_correct = stats.get('practice_correct', 0)
        test_total = stats.get('test_total', 0)
        test_correct = stats.get('test_correct', 0)
        
        total_correct += practice_correct + test_correct
        total_questions += practice_total + test_total
        
        if practice_total > 0 or test_total > 0:
            print(f'{arrhythmia}:')
            print(f'  Practice: {practice_correct}/{practice_total}')
            print(f'  Test: {test_correct}/{test_total}')
    
    print(f'\n=== TOTALS ===')
    print(f'Total correct: {total_correct}')
    print(f'Total questions: {total_questions}')
    accuracy = (total_correct/total_questions*100) if total_questions > 0 else 0
    print(f'Accuracy: {accuracy:.1f}%')
finally:
    db.close()
