"""
Модель попытки прохождения теста - хранит информацию о каждой попытке пользователя
"""

from datetime import datetime
from backend.models import db

class TestAttempt(db.Model):
    """Попытка прохождения теста конкретным пользователем"""

    __tablename__ = 'test_attempts'

    # Основные поля
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False, index=True)  # Какой тест проходили
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)  # Кто проходил
    score = db.Column(db.Float, nullable=True)  # Результат в процентах (вычисляется после завершения)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)  # Когда начали
    finished_at = db.Column(db.DateTime, nullable=True, index=True)  # Когда закончили (null если не завершено)

    # Связь с ответами пользователя
    # При удалении попытки удаляются все ответы
    answers = db.relationship('Answer', backref='attempt', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_answers=False):
        """Преобразует попытку в словарь для JSON"""
        result = {
            'id': self.id,
            'test_id': self.test_id,
            'user_id': self.user_id,
            'score': self.score,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None
        }
        # Опционально включаем все ответы (для детального просмотра)
        if include_answers:
            result['answers'] = [a.to_dict() for a in self.answers]
        return result
