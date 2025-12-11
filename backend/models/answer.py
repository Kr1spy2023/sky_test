"""
Модель ответа - хранит ответы пользователя на вопросы теста
"""

import json
from backend.models import db

class Answer(db.Model):
    """Ответ пользователя на конкретный вопрос"""

    __tablename__ = 'answers'
    # Ограничение: один пользователь может дать только один ответ на вопрос в рамках одной попытки
    __table_args__ = (
        db.UniqueConstraint('attempt_id', 'question_id', name='uq_attempt_question'),
    )

    # Основные поля
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('test_attempts.id'), nullable=False, index=True)  # К какой попытке относится
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False, index=True)  # На какой вопрос отвечал
    user_answer = db.Column(db.Text)  # Ответ пользователя в формате JSON (индекс или список индексов)
    is_correct = db.Column(db.Boolean, nullable=True)  # Правильный ответ или нет (вычисляется при проверке)

    def to_dict(self):
        """Преобразует ответ в словарь для JSON"""
        result = {
            'id': self.id,
            'question_id': self.question_id,
            'is_correct': self.is_correct
        }
        # Парсим JSON ответ пользователя
        if self.user_answer:
            try:
                result['user_answer'] = json.loads(self.user_answer)
            except (json.JSONDecodeError, TypeError):
                result['user_answer'] = self.user_answer
        return result
