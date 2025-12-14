"""
Сервис прохождения тестов - создание попытки, сохранение ответов, подсчет результата
"""

import json
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from backend.models import db
from backend.models.test import Test
from backend.models.question import Question
from backend.models.attempt import TestAttempt
from backend.models.answer import Answer
def start_attempt(test_id, user_id):
    """Создание новой попытки прохождения теста"""
    test = Test.query.get(test_id)
    if not test:
        raise ValueError('Test not found')

    # Создаем запись о начале прохождения (started_at устанавливается автоматически)
    attempt = TestAttempt(
        test_id=test_id,
        user_id=user_id
    )
    db.session.add(attempt)
    db.session.commit()
    return attempt.to_dict()

def submit_answer(attempt_id, question_id, answer_data, user_id):
    """Сохранение ответа пользователя на вопрос с проверкой правильности"""
    attempt = TestAttempt.query.get(attempt_id)
    if not attempt:
        raise ValueError('Attempt not found')
    # Проверка что пользователь может изменять эту попытку
    if attempt.user_id != user_id:
        raise ValueError('Access denied')
    # Нельзя изменить ответы после завершения теста
    if attempt.finished_at:
        raise ValueError('Attempt already finished')

    question = Question.query.get(question_id)
    if not question or question.test_id != attempt.test_id:
        raise ValueError('Question not found')

    # Проверяем существует ли уже ответ на этот вопрос (для обновления)
    existing_answer = Answer.query.filter_by(
        attempt_id=attempt_id,
        question_id=question_id
    ).first()

    try:
        if existing_answer:
            # Обновляем существующий ответ (пользователь изменил ответ)
            existing_answer.user_answer = json.dumps(answer_data)
            existing_answer.is_correct = check_answer(question, answer_data)
        else:
            # Создаем новый ответ
            answer = Answer(
                attempt_id=attempt_id,
                question_id=question_id,
                user_answer=json.dumps(answer_data),
                is_correct=check_answer(question, answer_data)  # Сразу проверяем правильность
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
    """Проверка правильности ответа в зависимости от типа вопроса"""
    if not question.correct_answer:
        return None

    try:
        correct = json.loads(question.correct_answer)
    except (json.JSONDecodeError, TypeError):
        return None

    # Один правильный вариант (radio button) - сравниваем числа
    if question.question_type == 'single':
        # user_answer может быть строкой "0", числом 0, или JSON строкой
        # correct может быть списком [0] или числом 0
        try:
            # Пытаемся распарсить, если это JSON строка
            if isinstance(user_answer, str):
                try:
                    user_ans_parsed = json.loads(user_answer)
                    user_ans_int = int(user_ans_parsed)
                except (json.JSONDecodeError, ValueError, TypeError):
                    # Если не JSON, пытаемся преобразовать напрямую
                    user_ans_int = int(user_answer)
            else:
                user_ans_int = int(user_answer)
        except (ValueError, TypeError):
            return False
        
        if isinstance(correct, list):
            if len(correct) > 0:
                return user_ans_int == correct[0]
            return False
        else:
            return user_ans_int == correct
    # Несколько правильных вариантов (checkboxes) - сравниваем отсортированные списки
    elif question.question_type == 'multiple':
        # user_answer может быть списком или JSON строкой
        if isinstance(user_answer, str):
            try:
                user_ans = json.loads(user_answer)
            except (json.JSONDecodeError, TypeError):
                return False
        else:
            user_ans = user_answer
            
        if not isinstance(user_ans, list):
            return False
        if not isinstance(correct, list):
            return None
        return sorted(user_ans) == sorted(correct)
    # Текстовый ответ - сравниваем строки без учета регистра и пробелов
    elif question.question_type == 'text':
        return str(user_answer).strip().lower() == str(correct).strip().lower()

    return None

def finish_attempt(attempt_id, user_id):
    """Завершение попытки - подсчет итогового результата"""
    attempt = TestAttempt.query.get(attempt_id)
    if not attempt:
        raise ValueError('Attempt not found')
    if attempt.user_id != user_id:
        raise ValueError('Access denied')
    if attempt.finished_at:
        raise ValueError('Attempt already finished')

    # Подсчитываем процент правильных ответов
    score = calculate_score(attempt_id)
    attempt.score = score
    attempt.finished_at = datetime.utcnow()  # Фиксируем время завершения
    db.session.commit()

    return {
        'score': score,
        'finished_at': attempt.finished_at.isoformat()
    }

def calculate_score(attempt_id):
    """Вычисление процента правильных ответов от общего количества вопросов"""
    attempt = TestAttempt.query.get(attempt_id)
    if not attempt:
        return 0

    # Получаем все вопросы теста (важно считать от общего количества, а не от отвеченных)
    test = Test.query.get(attempt.test_id)
    if not test or not test.questions:
        return 0

    total_questions = len(test.questions)

    # Получаем ответы пользователя
    answers = Answer.query.filter_by(attempt_id=attempt_id).all()

    # Считаем только правильные ответы (is_correct=True)
    # None игнорируем (вопросы без правильного ответа)
    correct_count = sum(1 for a in answers if a.is_correct is True)

    # Результат в процентах, округленный до 2 знаков
    return round((correct_count / total_questions) * 100, 2)

def get_attempt_results(attempt_id, user_id):
    """Получение результатов попытки с детализацией по ответам"""
    attempt = TestAttempt.query.get(attempt_id)
    if not attempt:
        raise ValueError('Attempt not found')
    if attempt.user_id != user_id:
        raise ValueError('Access denied')

    return attempt.to_dict(include_answers=True)
