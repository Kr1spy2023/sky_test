"""
API маршруты для прохождения тестов
"""

from flask import Blueprint, request
from backend.services.attempt_service import (
    start_attempt, submit_answer, finish_attempt, get_attempt_results
)
from backend.utils.responses import success_response, error_response
from backend.utils.jwt_utils import require_auth

attempts_bp = Blueprint('attempts', __name__, url_prefix='/api')

@attempts_bp.route('/tests/<int:test_id>/attempts', methods=['POST'])
@require_auth
def start(user_id, test_id):
    """
    Начать попытку прохождения теста
    ---
    tags:
      - Attempts
    security:
      - Bearer: []
    parameters:
      - name: test_id
        in: path
        type: integer
        required: true
    responses:
      201:
        description: Попытка создана
      404:
        description: Тест не найден
    """
    try:
        attempt = start_attempt(test_id, user_id)
        return success_response(attempt, 201)
    except ValueError as e:
        return error_response(str(e), 404)

@attempts_bp.route('/attempts/<int:attempt_id>/answers', methods=['POST'])
@require_auth
def submit(user_id, attempt_id):
    """
    Отправить ответ на вопрос
    ---
    tags:
      - Attempts
    security:
      - Bearer: []
    parameters:
      - name: attempt_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - question_id
            - answer
          properties:
            question_id:
              type: integer
              example: 1
            answer:
              oneOf:
                - type: string
                - type: array
              example: "Ответ на вопрос"
    responses:
      200:
        description: Ответ сохранен
      400:
        description: Некорректные данные
    """
    data = request.json
    if not data or 'question_id' not in data or 'answer' not in data:
        return error_response('Missing required fields', 400)

    try:
        result = submit_answer(
            attempt_id,
            data['question_id'],
            data['answer'],
            user_id
        )
        return success_response(result)
    except ValueError as e:
        return error_response(str(e), 400)

@attempts_bp.route('/attempts/<int:attempt_id>/finish', methods=['POST'])
@require_auth
def finish(user_id, attempt_id):
    """
    Завершить попытку
    ---
    tags:
      - Attempts
    security:
      - Bearer: []
    parameters:
      - name: attempt_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Попытка завершена
      400:
        description: Ошибка
    """
    try:
        result = finish_attempt(attempt_id, user_id)
        return success_response(result)
    except ValueError as e:
        return error_response(str(e), 400)

@attempts_bp.route('/attempts/<int:attempt_id>/results', methods=['GET'])
@require_auth
def results(user_id, attempt_id):
    """
    Получить результаты попытки
    ---
    tags:
      - Attempts
    security:
      - Bearer: []
    parameters:
      - name: attempt_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Результаты получены
      404:
        description: Попытка не найдена
    """
    try:
        result = get_attempt_results(attempt_id, user_id)
        return success_response(result)
    except ValueError as e:
        return error_response(str(e), 404)
