import json
from datetime import datetime
from backend.models import db
from backend.models.test import Test
from backend.models.question import Question
from backend.models.attempt import TestAttempt
from backend.models.answer import Answer

def start_attempt(test_id, user_id):
    test = Test.query.get(test_id)
    if not test:
        raise ValueError('Test not found')

    attempt = TestAttempt(
        test_id=test_id,
        user_id=user_id
    )
    db.session.add(attempt)
    db.session.commit()
    return attempt.to_dict()

def submit_answer(attempt_id, question_id, answer_data, user_id):
    attempt = TestAttempt.query.get(attempt_id)
    if not attempt:
        raise ValueError('Attempt not found')
    if attempt.user_id != user_id:
        raise ValueError('Access denied')
    if attempt.finished_at:
        raise ValueError('Attempt already finished')

    question = Question.query.get(question_id)
    if not question or question.test_id != attempt.test_id:
        raise ValueError('Question not found')

    from sqlalchemy.exc import IntegrityError

    existing_answer = Answer.query.filter_by(
        attempt_id=attempt_id,
        question_id=question_id
    ).first()

    try:
        if existing_answer:
            existing_answer.user_answer = json.dumps(answer_data)
            existing_answer.is_correct = check_answer(question, answer_data)
        else:
            answer = Answer(
                attempt_id=attempt_id,
                question_id=question_id,
                user_answer=json.dumps(answer_data),
                is_correct=check_answer(question, answer_data)
            )
            db.session.add(answer)

        db.session.commit()
        return {'message': 'Answer submitted'}
    except IntegrityError:
        db.session.rollback()
        raise ValueError('Answer already exists for this question')
    except Exception as e:
        db.session.rollback()
        raise ValueError(f'Error submitting answer: {str(e)}')

def check_answer(question, user_answer):
    if not question.correct_answer:
        return None

    try:
        correct = json.loads(question.correct_answer)
    except (json.JSONDecodeError, TypeError):
        return None

    if question.question_type == 'single':
        return user_answer == correct
    elif question.question_type == 'multiple':
        # Проверка что user_answer это список
        if not isinstance(user_answer, list):
            return False
        if not isinstance(correct, list):
            return None
        return sorted(user_answer) == sorted(correct)
    elif question.question_type == 'text':
        return str(user_answer).strip().lower() == str(correct).strip().lower()

    return None

def finish_attempt(attempt_id, user_id):
    attempt = TestAttempt.query.get(attempt_id)
    if not attempt:
        raise ValueError('Attempt not found')
    if attempt.user_id != user_id:
        raise ValueError('Access denied')
    if attempt.finished_at:
        raise ValueError('Attempt already finished')

    score = calculate_score(attempt_id)
    attempt.score = score
    attempt.finished_at = datetime.utcnow()
    db.session.commit()

    return {
        'score': score,
        'finished_at': attempt.finished_at.isoformat()
    }

def calculate_score(attempt_id):
    attempt = TestAttempt.query.get(attempt_id)
    if not attempt:
        return 0

    # Получить все вопросы теста
    test = Test.query.get(attempt.test_id)
    if not test or not test.questions:
        return 0

    total_questions = len(test.questions)

    # Получить ответы пользователя
    answers = Answer.query.filter_by(attempt_id=attempt_id).all()

    # Подсчет правильных ответов (только True, игнорируем None)
    correct_count = sum(1 for a in answers if a.is_correct is True)

    # Score от общего количества вопросов в тесте
    return round((correct_count / total_questions) * 100, 2)

def get_attempt_results(attempt_id, user_id):
    attempt = TestAttempt.query.get(attempt_id)
    if not attempt:
        raise ValueError('Attempt not found')
    if attempt.user_id != user_id:
        raise ValueError('Access denied')

    return attempt.to_dict(include_answers=True)
