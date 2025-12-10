import json
from backend.models import db

class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False, index=True)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), nullable=False)
    options = db.Column(db.Text)
    correct_answer = db.Column(db.Text)
    order_index = db.Column(db.Integer, default=0)

    answers = db.relationship('Answer', backref='question', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_correct_answer=False):
        result = {
            'id': self.id,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'order_index': self.order_index
        }
        if self.options:
            try:
                result['options'] = json.loads(self.options)
            except (json.JSONDecodeError, TypeError):
                result['options'] = []
        if include_correct_answer and self.correct_answer:
            try:
                result['correct_answer'] = json.loads(self.correct_answer)
            except (json.JSONDecodeError, TypeError):
                result['correct_answer'] = self.correct_answer
        return result
