"""
Sky Test - Веб-приложение для создания и прохождения тестов
Главный файл приложения - точка входа
"""

import os
import json
from flask import Flask, render_template
from flasgger import Swagger
from flask_cors import CORS
from config import Config
from backend.models import db
from backend.models.user import User
from backend.models.test import Test
from backend.models.question import Question
from backend.models.attempt import TestAttempt
from backend.models.answer import Answer
from backend.routes.auth import auth_bp
from backend.routes.tests import tests_bp
from backend.routes.questions import questions_bp
from backend.routes.attempts import attempts_bp
from backend.routes.statistics import statistics_bp
from backend.routes.views import views_bp

# Создание экземпляра Flask приложения
app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
app.config.from_object(Config)

# Создание папки для базы данных если её нет
db_folder = os.path.join(os.path.dirname(__file__), 'database')
os.makedirs(db_folder, exist_ok=True)

# Инициализация SQLAlchemy (ORM для работы с БД)
db.init_app(app)

# Настройка CORS - разрешает API принимать запросы с других доменов
CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}})

# Ограничение размера запроса (защита от DoS-атак)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Конфигурация Swagger (автодокументация API)
swagger_config = {
    "headers": [],
    "specs": [{"endpoint": 'apispec', "route": '/apispec.json'}],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/swagger"
}

swagger_template = {
    "info": {
        "title": "Sky Test API",
        "description": "API для платформы тестирования",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT token. Вставьте токен БЕЗ слова 'Bearer' - просто сам токен. Или используйте формат: Bearer {token}"
        }
    }
}

Swagger(app, config=swagger_config, template=swagger_template)

# Кастомный фильтр Jinja2 для парсинга JSON в шаблонах
# Используется для преобразования JSON строк (например, вариантов ответов) в список
@app.template_filter('from_json')
def from_json_filter(value):
    """Парсит JSON строку в Python объект (список/словарь)"""
    if not value:
        return []
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return []

# Регистрация маршрутов (blueprints)
# API endpoints для JSON запросов
app.register_blueprint(auth_bp)        # /api/auth/*
app.register_blueprint(tests_bp)       # /api/tests/*
app.register_blueprint(questions_bp)   # /api/questions/*
app.register_blueprint(attempts_bp)    # /api/attempts/*
app.register_blueprint(statistics_bp)  # /api/statistics/*

# HTML views для браузера
app.register_blueprint(views_bp)

# Обработчики ошибок - показывают красивые страницы вместо стандартных ошибок
@app.errorhandler(404)
def page_not_found(e):
    """Страница не найдена"""
    return render_template('error.html', error_code=404,
                         error_message='Страница не найдена'), 404

@app.errorhandler(500)
def internal_error(e):
    """Внутренняя ошибка сервера"""
    return render_template('error.html', error_code=500,
                         error_message='Внутренняя ошибка сервера'), 500

# Создание таблиц в базе данных при первом запуске
with app.app_context():
    db.create_all()  # Создает таблицы если их ещё нет

# Точка входа - запуск сервера
if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False') == 'True'
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 8000))
    app.run(host=host, port=port, debug=debug_mode)
