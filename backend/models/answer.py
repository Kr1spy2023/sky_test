import json
from backend.models import db

class Answer(db.Model):
    __tablename__ = 'answers'

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('test_attempts.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    user_answer = db.Column(db.Text)
    is_correct = db.Column(db.Boolean, nullable=True)

    def to_dict(self):
        result = {
            'id': self.id,
            'question_id': self.question_id,
            'is_correct': self.is_correct
        }
        if self.user_answer:
            result['user_answer'] = json.loads(self.user_answer)
        return result
