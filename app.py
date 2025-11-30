import os
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from config import Config
from backend.models import db
from backend.routes.auth import auth_bp
from backend.routes.tests import tests_bp
from backend.routes.questions import questions_bp
from backend.routes.attempts import attempts_bp
from backend.routes.statistics import statistics_bp

app = Flask(__name__)
app.config.from_object(Config)

db_folder = os.path.join(os.path.dirname(__file__), 'database')
os.makedirs(db_folder, exist_ok=True)

db.init_app(app)
# CORS configuration - allow all origins during development
CORS(app, resources={r"/api/*": {"origins": "*"}})

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

app.register_blueprint(auth_bp)
app.register_blueprint(tests_bp)
app.register_blueprint(questions_bp)
app.register_blueprint(attempts_bp)
app.register_blueprint(statistics_bp)

with app.app_context():
    from backend.models.user import User  # noqa: F401
    from backend.models.test import Test  # noqa: F401
    from backend.models.question import Question  # noqa: F401
    from backend.models.attempt import TestAttempt  # noqa: F401
    from backend.models.answer import Answer  # noqa: F401
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
