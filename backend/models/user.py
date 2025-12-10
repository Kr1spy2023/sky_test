from datetime import datetime
from backend.models import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tests = db.relationship('Test', backref='author', lazy=True, cascade='all, delete-orphan')
    attempts = db.relationship('TestAttempt', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        from backend.utils.password import hash_password
        self.password_hash = hash_password(password)

    def check_password(self, password):
        from backend.utils.password import verify_password
        return verify_password(password, self.password_hash)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email
        }
