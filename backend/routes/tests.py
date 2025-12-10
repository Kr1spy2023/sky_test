from flask import Blueprint, request
from backend.services.test_service import (
    create_test, get_user_tests, get_test, update_test,
    delete_test, publish_test, get_test_by_link
)
from backend.utils.responses import success_response, error_response
from backend.utils.jwt_utils import require_auth

tests_bp = Blueprint('tests', __name__, url_prefix='/api/tests')

@tests_bp.route('', methods=['GET'])
@require_auth
def list_tests(user_id):
    """
    Получить список тестов пользователя
    ---
    tags:
      - Tests
    security:
      - Bearer: []
    parameters:
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
        description: Список тестов
    """
    skip = request.args.get('skip', 0, type=int)
    limit = request.args.get('limit', 20, type=int)

    # Валидация пагинации
    if skip < 0:
        return error_response('skip должен быть >= 0', 400)
    if limit < 1 or limit > 100:
        return error_response('limit должен быть от 1 до 100', 400)

    try:
        tests = get_user_tests(user_id, skip, limit)
        return success_response(tests)
    except Exception as e:
        return error_response(str(e), 500)

@tests_bp.route('/<int:test_id>', methods=['GET'])
@require_auth
def get_test_detail(user_id, test_id):
    """
    Получить тест по ID
    ---
    tags:
      - Tests
    security:
      - Bearer: []
    parameters:
      - name: test_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Данные теста
      404:
        description: Тест не найден
    """
    try:
        test = get_test(test_id, user_id)
        return success_response(test)
    except ValueError as e:
        return error_response(str(e), 404)

@tests_bp.route('', methods=['POST'])
@require_auth
def create(user_id):
    """
    Создать новый тест
    ---
    tags:
      - Tests
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - title
          properties:
            title:
              type: string
              example: Python Quiz
            description:
              type: string
              example: Тест на знание Python
    responses:
      201:
        description: Тест создан
      400:
        description: Некорректные данные
    """
    data = request.json
    if not data or 'title' not in data:
        return error_response('Title is required', 400)

    try:
        test = create_test(user_id, data.get('title'), data.get('description', ''))
        return success_response(test, 201)
    except ValueError as e:
        return error_response(str(e), 400)

@tests_bp.route('/<int:test_id>', methods=['PUT'])
@require_auth
def update(user_id, test_id):
    """
    Обновить тест
    ---
    tags:
      - Tests
    security:
      - Bearer: []
    parameters:
      - name: test_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        schema:
          type: object
          properties:
            title:
              type: string
            description:
              type: string
    responses:
      200:
        description: Тест обновлен
      404:
        description: Тест не найден
    """
    data = request.json
    if not data:
        return error_response('No data provided', 400)

    try:
        test = update_test(test_id, user_id, data)
        return success_response(test)
    except ValueError as e:
        return error_response(str(e), 404)

@tests_bp.route('/<int:test_id>', methods=['DELETE'])
@require_auth
def delete(user_id, test_id):
    """
    Удалить тест
    ---
    tags:
      - Tests
    security:
      - Bearer: []
    parameters:
      - name: test_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Тест удален
      404:
        description: Тест не найден
    """
    try:
        delete_test(test_id, user_id)
        return success_response({'message': 'Test deleted'})
    except ValueError as e:
        return error_response(str(e), 404)

@tests_bp.route('/<int:test_id>/publish', methods=['POST'])
@require_auth
def publish(user_id, test_id):
    """
    Опубликовать тест
    ---
    tags:
      - Tests
    security:
      - Bearer: []
    parameters:
      - name: test_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Тест опубликован
      404:
        description: Тест не найден
    """
    try:
        test = publish_test(test_id, user_id)
        return success_response(test)
    except ValueError as e:
        return error_response(str(e), 404)

@tests_bp.route('/link/<string:link_token>', methods=['GET'])
def get_by_link(link_token):
    """
    Получить тест по ссылке
    ---
    tags:
      - Tests
    parameters:
      - name: link_token
        in: path
        type: string
        required: true
    responses:
      200:
        description: Данные теста
      404:
        description: Тест не найден
    """
    try:
        test = get_test_by_link(link_token)
        return success_response(test)
    except ValueError as e:
        return error_response(str(e), 404)
