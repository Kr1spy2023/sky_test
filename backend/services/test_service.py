"""
Сервис для работы с тестами и вопросами
"""

import json
import uuid
from backend.models import db
from backend.models.test import Test
from backend.models.question import Question

def create_test(user_id, title, description):
    test = Test(
        title=title,
        description=description,
        user_id=user_id
    )
    db.session.add(test)
    db.session.commit()
    return test.to_dict()

def get_user_tests(user_id, skip=0, limit=20):
    tests = Test.query.filter_by(user_id=user_id).offset(skip).limit(limit).all()
    return [t.to_dict() for t in tests]

def get_test(test_id, user_id=None):
    test = Test.query.get(test_id)
    if not test:
        raise ValueError('Test not found')
    if user_id and test.user_id != user_id:
        raise ValueError('Access denied')
    return test.to_dict(include_questions=True)

def update_test(test_id, user_id, data):
    test = Test.query.get(test_id)
    if not test:
        raise ValueError('Test not found')
    if test.user_id != user_id:
        raise ValueError('Access denied')

    if 'title' in data:
        test.title = data['title']
    if 'description' in data:
        test.description = data['description']

    db.session.commit()
    return test.to_dict()

def delete_test(test_id, user_id):
    test = Test.query.get(test_id)
    if not test:
        raise ValueError('Test not found')
    if test.user_id != user_id:
        raise ValueError('Access denied')

    db.session.delete(test)
    db.session.commit()
    return True

def publish_test(test_id, user_id):
    test = Test.query.get(test_id)
    if not test:
        raise ValueError('Test not found')
    if test.user_id != user_id:
        raise ValueError('Access denied')

    question_count = Question.query.filter_by(test_id=test_id).count()
    if question_count == 0:
        raise ValueError('Cannot publish test without questions. Add at least one question.')

    test.is_published = True
    test.link_token = str(uuid.uuid4())
    db.session.commit()
    return test.to_dict()

def get_test_by_link(link_token):
    test = Test.query.filter_by(link_token=link_token).first()
    if not test:
        raise ValueError('Test not found')
    if not test.is_published:
        raise ValueError('Test is not published')
    return test.to_dict(include_questions=True)

def create_question(test_id, user_id, data):
    test = Test.query.get(test_id)
    if not test:
        raise ValueError('Test not found')
    if test.user_id != user_id:
        raise ValueError('Access denied')

    # Валидация обязательных полей
    question_text = data.get('question_text', '').strip()
    if not question_text:
        raise ValueError('question_text is required')
    
    question_type = data.get('question_type')
    if not question_type:
        raise ValueError('question_type is required')

    # Обработка correct_answer: для single типа сохраняем как список [index]
    correct_answer = data.get('correct_answer')
    if correct_answer is not None:
        if question_type == 'single':
            # Для single типа: если число, преобразуем в список
            if isinstance(correct_answer, (int, float)):
                correct_answer = [int(correct_answer)]
            elif isinstance(correct_answer, list) and len(correct_answer) > 0:
                # Уже список, берем первый элемент
                correct_answer = [int(correct_answer[0])]
            else:
                correct_answer = None
        # Для multiple типа оставляем как список
        elif question_type == 'multiple':
            if not isinstance(correct_answer, list):
                raise ValueError('For multiple type, correct_answer must be a list')
        correct_answer_json = json.dumps(correct_answer) if correct_answer is not None else None
    else:
        correct_answer_json = None
    
    try:
        question = Question(
            test_id=test_id,
            question_text=question_text,
            question_type=question_type,
            options=json.dumps(data.get('options', [])) if data.get('options') else None,
            correct_answer=correct_answer_json,
            order_index=data.get('order_index', 0)
        )
        db.session.add(question)
        db.session.commit()
        return question.to_dict(include_correct_answer=True)
    except Exception as e:
        db.session.rollback()
        raise ValueError(f'Error creating question: {str(e)}')

def update_question(test_id, question_id, user_id, data):
    test = Test.query.get(test_id)
    if not test or test.user_id != user_id:
        raise ValueError('Access denied')

    question = Question.query.filter_by(id=question_id, test_id=test_id).first()
    if not question:
        raise ValueError('Question not found')

    if 'question_text' in data:
        question.question_text = data['question_text']
    if 'question_type' in data:
        question.question_type = data['question_type']
    if 'options' in data:
        question.options = json.dumps(data['options'])
    if 'correct_answer' in data:
        question.correct_answer = json.dumps(data['correct_answer'])
    if 'order_index' in data:
        question.order_index = data['order_index']

    db.session.commit()
    return question.to_dict(include_correct_answer=True)

def delete_question(test_id, question_id, user_id):
    test = Test.query.get(test_id)
    if not test or test.user_id != user_id:
        raise ValueError('Access denied')

    question = Question.query.filter_by(id=question_id, test_id=test_id).first()
    if not question:
        raise ValueError('Question not found')

    db.session.delete(question)
    db.session.commit()
    return True
