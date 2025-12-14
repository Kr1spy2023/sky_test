"""
Сервис для получения статистики
"""

from sqlalchemy import func
from backend.models import db
from backend.models.test import Test
from backend.models.attempt import TestAttempt

def get_test_statistics(test_id, user_id):
    test = Test.query.get(test_id)
    if not test:
        raise ValueError('Test not found')
    if test.user_id != user_id:
        raise ValueError('Access denied')

    attempts = TestAttempt.query.filter_by(test_id=test_id).filter(
        TestAttempt.finished_at.isnot(None)
    ).all()

    total_attempts = len(attempts)
    if total_attempts == 0:
        return {
            'test_id': test_id,
            'total_attempts': 0,
            'average_score': 0,
            'highest_score': 0,
            'lowest_score': 0
        }

    scores = [a.score for a in attempts if a.score is not None]
    avg_score = sum(scores) / len(scores) if scores else 0

    return {
        'test_id': test_id,
        'total_attempts': total_attempts,
        'average_score': round(avg_score, 2),
        'highest_score': max(scores) if scores else 0,
        'lowest_score': min(scores) if scores else 0
    }

def get_test_attempts(test_id, user_id, skip=0, limit=20):
    test = Test.query.get(test_id)
    if not test:
        raise ValueError('Test not found')
    if test.user_id != user_id:
        raise ValueError('Access denied')

    attempts = TestAttempt.query.filter_by(test_id=test_id)\
        .order_by(TestAttempt.started_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

    return [a.to_dict() for a in attempts]

def get_user_statistics(user_id):
    total_attempts = TestAttempt.query.filter_by(user_id=user_id).filter(
        TestAttempt.finished_at.isnot(None)
    ).count()

    tests_created = Test.query.filter_by(user_id=user_id).count()

    completed_attempts = TestAttempt.query.filter_by(user_id=user_id).filter(
        TestAttempt.finished_at.isnot(None)
    ).all()

    scores = [a.score for a in completed_attempts if a.score is not None]
    avg_score = sum(scores) / len(scores) if scores else 0

    return {
        'total_attempts': total_attempts,
        'tests_created': tests_created,
        'average_score': round(avg_score, 2)
    }
