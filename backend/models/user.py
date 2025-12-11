"""
Модель пользователя - хранит данные о зарегистрированных пользователях
"""

from datetime import datetime
from backend.models import db

class User(db.Model):
    """Пользователь системы (студент или преподаватель)"""

    __tablename__ = 'users'

    # Основные поля
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Имя для отображения
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)  # Email (логин)
    password_hash = db.Column(db.String(255), nullable=False)  # Хеш пароля (не сам пароль!)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Связи с другими таблицами
    # cascade='all, delete-orphan' означает: при удалении пользователя удалить все его тесты и попытки
    tests = db.relationship('Test', backref='author', lazy=True, cascade='all, delete-orphan')
    attempts = db.relationship('TestAttempt', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Хеширует и сохраняет пароль (используется при регистрации и смене пароля)"""
        from backend.utils.password import hash_password
        self.password_hash = hash_password(password)

    def check_password(self, password):
        """Проверяет правильность пароля (используется при входе)"""
        from backend.utils.password import verify_password
        return verify_password(password, self.password_hash)

    def to_dict(self):
        """Преобразует объект в словарь (для JSON ответов API)"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email
            # password_hash НЕ включаем в ответ (безопасность!)
        }
