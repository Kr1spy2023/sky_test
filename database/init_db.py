import os
from backend.models import db
from backend.models.user import User
from backend.models.test import Test
from backend.models.question import Question
from backend.models.attempt import TestAttempt
from backend.models.answer import Answer

def init_database(app):
    with app.app_context():
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
        os.makedirs(db_path, exist_ok=True)
        db.create_all()
