"""
API маршруты для получения статистики
"""

from flask import Blueprint, request
from backend.services.stats_service import (
    get_test_statistics, get_test_attempts, get_user_statistics
)
from backend.utils.responses import success_response, error_response
from backend.utils.jwt_utils import require_auth

statistics_bp = Blueprint('statistics', __name__, url_prefix='/api')

@statistics_bp.route('/tests/<int:test_id>/statistics', methods=['GET'])
@require_auth
def test_stats(user_id, test_id):
    """
    Получить статистику теста
    ---
    tags:
      - Statistics
    security:
      - Bearer: []
    parameters:
      - name: test_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Статистика теста
      404:
        description: Тест не найден
    """
    try:
        stats = get_test_statistics(test_id, user_id)
        return success_response(stats)
    except ValueError as e:
        return error_response(str(e), 404)

@statistics_bp.route('/tests/<int:test_id>/attempts', methods=['GET'])
@require_auth
def test_attempts(user_id, test_id):
    """
    Получить попытки прохождения теста
    ---
    tags:
      - Statistics
    security:
      - Bearer: []
    parameters:
      - name: test_id
        in: path
        type: integer
        required: true
      - name: skip
        in: query
        type: integer
        default: 0
      - name: limit
        in: query
        type: integer
        default: 20
    responses:
      200:
        description: Список попыток
      404:
        description: Тест не найден
    """
    skip = request.args.get('skip', 0, type=int)
    limit = request.args.get('limit', 20, type=int)

    # Валидация пагинации
    if skip < 0:
        return error_response('skip должен быть >= 0', 400)
    if limit < 1 or limit > 100:
        return error_response('limit должен быть от 1 до 100', 400)

    try:
        attempts = get_test_attempts(test_id, user_id, skip, limit)
        return success_response(attempts)
    except ValueError as e:
        return error_response(str(e), 404)

@statistics_bp.route('/statistics/user', methods=['GET'])
@require_auth
def user_stats(user_id):
    """
    Получить статистику пользователя
    ---
    tags:
      - Statistics
    security:
      - Bearer: []
    responses:
      200:
        description: Статистика пользователя
    """
    try:
        stats = get_user_statistics(user_id)
        return success_response(stats)
    except Exception as e:
        return error_response(str(e), 500)
