"""
Модель вопроса - хранит вопросы теста с вариантами ответов
"""

import json
from backend.models import db

class Question(db.Model):
    """Вопрос в тесте"""

    __tablename__ = 'questions'

    # Основные поля
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False, index=True)
    question_text = db.Column(db.Text, nullable=False)  # Текст вопроса
    question_type = db.Column(db.String(20), nullable=False)  # Тип: 'single' или 'multiple'
    options = db.Column(db.Text)  # Варианты ответов в формате JSON списка ['вариант1', 'вариант2', ...]
    correct_answer = db.Column(db.Text)  # Правильные ответы в формате JSON (список индексов [0, 2] или одно число)
    order_index = db.Column(db.Integer, default=0)  # Порядок вопроса в тесте (для сортировки)

    # Связь с ответами пользователей
    answers = db.relationship('Answer', backref='question', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_correct_answer=False):
        """Преобразует вопрос в словарь для JSON ответов"""
        result = {
            'id': self.id,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'order_index': self.order_index
        }
        # Парсим JSON варианты ответов в список
        if self.options:
            try:
                result['options'] = json.loads(self.options)
            except (json.JSONDecodeError, TypeError):
                result['options'] = []
        # Правильные ответы отдаем только при необходимости (например, при проверке или редактировании)
        # НЕ отдаем при прохождении теста студентом!
        if include_correct_answer and self.correct_answer:
            try:
                result['correct_answer'] = json.loads(self.correct_answer)
            except (json.JSONDecodeError, TypeError):
                result['correct_answer'] = self.correct_answer
        return result
