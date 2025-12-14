"""
API маршруты для аутентификации и управления профилем пользователя
"""

from flask import Blueprint, request
from backend.services.auth_service import register_user, login_user, get_user_profile, update_user_profile
from backend.utils.responses import success_response, error_response
from backend.utils.jwt_utils import require_auth
from backend.utils.validation import validate_email, validate_password

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Регистрация нового пользователя
    ---
    tags:
      - Auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
            - email
            - password
          properties:
            name:
              type: string
              example: John Doe
            email:
              type: string
              example: user@example.com
            password:
              type: string
              example: password123
    responses:
      201:
        description: Пользователь зарегистрирован
      400:
        description: Некорректные данные
    """
    data = request.json
    if not data or not all(k in data for k in ('name', 'email', 'password')):
        return error_response('Missing required fields', 400)

    # Валидация email
    is_valid_email, email_error = validate_email(data['email'])
    if not is_valid_email:
        return error_response(email_error, 400)

    # Валидация пароля
    is_valid_password, password_error = validate_password(data['password'])
    if not is_valid_password:
        return error_response(password_error, 400)

    try:
        result = register_user(data['name'], data['email'], data['password'])
        return success_response(result, 201)
    except ValueError as e:
        return error_response(str(e), 400)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Вход пользователя
    ---
    tags:
      - Auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: user@example.com
            password:
              type: string
              example: password123
    responses:
      200:
        description: Вход выполнен
      401:
        description: Неверные данные
    """
    data = request.json
    if not data or not all(k in data for k in ('email', 'password')):
        return error_response('Missing required fields', 400)

    try:
        result = login_user(data['email'], data['password'])
        return success_response(result)
    except ValueError as e:
        return error_response(str(e), 401)

@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile(user_id):
    """
    Получить профиль пользователя
    ---
    tags:
      - Auth
    security:
      - Bearer: []
    responses:
      200:
        description: Профиль получен
      401:
        description: Не авторизован
    """
    try:
        result = get_user_profile(user_id)
        return success_response(result)
    except ValueError as e:
        return error_response(str(e), 404)

@auth_bp.route('/profile', methods=['PUT'])
@require_auth
def update_profile(user_id):
    """
    Обновить профиль пользователя
    ---
    tags:
      - Auth
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        schema:
          type: object
          properties:
            name:
              type: string
            email:
              type: string
            password:
              type: string
    responses:
      200:
        description: Профиль обновлен
      401:
        description: Не авторизован
    """
    data = request.json
    if not data:
        return error_response('No data provided', 400)

    try:
        result = update_user_profile(user_id, data)
        return success_response(result)
    except ValueError as e:
        return error_response(str(e), 400)
