"""
Модель теста - хранит информацию о созданных тестах
"""

from datetime import datetime
from backend.models import db

class Test(db.Model):
    """Тест, созданный преподавателем"""

    __tablename__ = 'tests'

    # Основные поля
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)  # Название теста
    description = db.Column(db.Text)  # Описание (необязательное)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)  # Автор теста
    is_published = db.Column(db.Boolean, default=False, index=True)  # Опубликован (True) или черновик (False)
    link_token = db.Column(db.String(100), unique=True, nullable=True, index=True)  # Уникальная ссылка для прохождения
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Автообновление при изменении

    # Связи с другими таблицами
    # При удалении теста удаляются все его вопросы и попытки прохождения
    questions = db.relationship('Question', backref='test', lazy=True, cascade='all, delete-orphan')
    attempts = db.relationship('TestAttempt', backref='test', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_questions=False):
        """Преобразует тест в словарь для JSON ответов"""
        result = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'user_id': self.user_id,
            'is_published': self.is_published,
            'link_token': self.link_token,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'attempts_count': len(self.attempts)
        }
        # Опционально включаем вопросы (для детального просмотра теста)
        if include_questions:
            # Сортируем вопросы по order_index для правильного порядка отображения
            result['questions'] = [q.to_dict() for q in sorted(self.questions, key=lambda x: x.order_index)]
        return result
