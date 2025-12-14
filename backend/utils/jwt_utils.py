"""
Утилиты для работы с JWT токенами
"""

import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request
from config import Config
from .responses import error_response

def create_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')

def decode_token(token):
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return error_response('Authentication required', 401)

        # Поддержка разных форматов токена в заголовке Authorization:
        # 1. "Bearer {token}" - стандартный формат OAuth 2.0
        # 2. "{token}" - упрощенный формат (используется Swagger UI)
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1]  # Берем все после "Bearer "
        else:
            # Если нет префикса "Bearer ", считаем что весь заголовок - это токен
            token = auth_header.strip()

        if not token:
            return error_response('Authentication required', 401)

        user_id = decode_token(token)

        if not user_id:
            return error_response('Invalid or expired token', 401)

        return f(user_id, *args, **kwargs)

    return decorated_function
