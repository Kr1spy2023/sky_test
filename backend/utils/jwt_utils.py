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
        if not auth_header or not auth_header.startswith('Bearer '):
            return error_response('Authentication required', 401)

        token = auth_header.split(' ')[1]
        user_id = decode_token(token)

        if not user_id:
            return error_response('Invalid or expired token', 401)

        return f(user_id, *args, **kwargs)

    return decorated_function
