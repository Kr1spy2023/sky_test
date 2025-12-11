"""
Конфигурация приложения - настройки БД, секретного ключа, CORS
Значения берутся из .env файла или используются значения по умолчанию
"""

import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Базовая директория проекта (для путей к БД и другим файлам)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Секретный ключ для подписи сессий и токенов (ВАЖНО: изменить в production!)
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Путь к базе данных SQLite (по умолчанию в папке database/)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(BASE_DIR, "database", "tests.db")}')

    # Отключаем отслеживание модификаций (не нужно, экономит память)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Разрешенные источники для CORS (для API запросов с фронтенда)
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:8080').split(',')

    # Срок действия JWT токенов в часах
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))
