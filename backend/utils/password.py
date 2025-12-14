"""
Утилиты для работы с паролями
"""

from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password):
    """
    Хеширование пароля для безопасного хранения
    """
    return generate_password_hash(password)

def verify_password(password, password_hash):
    """
    Проверка пароля путем сравнения с хешем
    """
    return check_password_hash(password_hash, password)
