import os
from flask import Flask, render_template
from flask_cors import CORS
from flasgger import Swagger
from config import Config
from backend.models import db
from backend.routes.auth import auth_bp
from backend.routes.tests import tests_bp
from backend.routes.questions import questions_bp
from backend.routes.attempts import attempts_bp
from backend.routes.statistics import statistics_bp
from backend.routes.views import views_bp

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
app.config.from_object(Config)

db_folder = os.path.join(os.path.dirname(__file__), 'database')
os.makedirs(db_folder, exist_ok=True)

db.init_app(app)
CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}})

# Ограничение размера запроса (защита от DoS)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

swagger_config = {
    "headers": [],
    "specs": [{"endpoint": 'apispec', "route": '/apispec.json'}],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/swagger"
}

swagger_template = {
    "info": {
        "title": "Quiz Platform API",
        "description": "API для платформы тестирования",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT token. Формат: Bearer {token}"
        }
    }
}

Swagger(app, config=swagger_config, template=swagger_template)

# Добавить custom фильтр для парсинга JSON в Jinja2
import json
@app.template_filter('from_json')
def from_json_filter(value):
    """Парсит JSON строку в Python объект"""
    if not value:
        return []
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return []

# Регистрация blueprints для API
app.register_blueprint(auth_bp)
app.register_blueprint(tests_bp)
app.register_blueprint(questions_bp)
app.register_blueprint(attempts_bp)
app.register_blueprint(statistics_bp)

# Регистрация blueprints для views (шаблонов)
app.register_blueprint(views_bp)

# Обработчики ошибок
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404,
                         error_message='Страница не найдена'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', error_code=500,
                         error_message='Внутренняя ошибка сервера'), 500

with app.app_context():
    from backend.models.user import User
    from backend.models.test import Test
    from backend.models.question import Question
    from backend.models.attempt import TestAttempt
    from backend.models.answer import Answer
    db.create_all()

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False') == 'True'
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 8000))
    app.run(host=host, port=port, debug=debug_mode)
