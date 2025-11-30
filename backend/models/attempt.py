from datetime import datetime
from backend.models import db

class TestAttempt(db.Model):
    __tablename__ = 'test_attempts'

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Float, nullable=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime, nullable=True)

    answers = db.relationship('Answer', backref='attempt', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_answers=False):
        result = {
            'id': self.id,
            'test_id': self.test_id,
            'user_id': self.user_id,
            'score': self.score,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None
        }
        if include_answers:
            result['answers'] = [a.to_dict() for a in self.answers]
        return result
