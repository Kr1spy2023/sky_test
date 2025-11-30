from backend.models import db
from backend.models.user import User
from backend.utils.password import hash_password, verify_password
from backend.utils.jwt_utils import create_token

def register_user(name, email, password):
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        raise ValueError('Email already registered')

    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password)
    )
    db.session.add(user)
    db.session.commit()

    token = create_token(user.id)
    return {'token': token, 'user': user.to_dict()}

def login_user(email, password):
    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(password, user.password_hash):
        raise ValueError('Invalid email or password')

    token = create_token(user.id)
    return {'token': token, 'user': user.to_dict()}

def get_user_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        raise ValueError('User not found')
    return user.to_dict()

def update_user_profile(user_id, data):
    user = User.query.get(user_id)
    if not user:
        raise ValueError('User not found')

    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            raise ValueError('Email already in use')
        user.email = data['email']
    if 'password' in data:
        user.password_hash = hash_password(data['password'])

    db.session.commit()
    return user.to_dict()
