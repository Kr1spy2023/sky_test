from sqlalchemy.exc import IntegrityError
from backend.models import db
from backend.models.user import User
from backend.utils.password import hash_password, verify_password
from backend.utils.jwt_utils import create_token
from backend.utils.validation import validate_email, validate_password

def register_user(name, email, password):
    # Валидация email
    is_valid, error_msg = validate_email(email)
    if not is_valid:
        raise ValueError(error_msg)

    # Валидация пароля
    is_valid, error_msg = validate_password(password)
    if not is_valid:
        raise ValueError(error_msg)

    # Валидация имени
    if not name or len(name.strip()) < 2:
        raise ValueError('Имя должно содержать минимум 2 символа')
    if len(name) > 100:
        raise ValueError('Имя слишком длинное (максимум 100 символов)')

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        raise ValueError('Email already registered')

    try:
        user = User(
            name=name.strip(),
            email=email.strip().lower(),
            password_hash=hash_password(password)
        )
        db.session.add(user)
        db.session.commit()

        token = create_token(user.id)
        return {'token': token, 'user': user.to_dict()}
    except IntegrityError:
        db.session.rollback()
        raise ValueError('Email already registered')
    except Exception as e:
        db.session.rollback()
        raise ValueError(f'Error creating user: {str(e)}')

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

    try:
        if 'name' in data:
            name = data['name']
            if not name or len(name.strip()) < 2:
                raise ValueError('Имя должно содержать минимум 2 символа')
            if len(name) > 100:
                raise ValueError('Имя слишком длинное (максимум 100 символов)')
            user.name = name.strip()

        if 'email' in data:
            # Валидация email
            is_valid, error_msg = validate_email(data['email'])
            if not is_valid:
                raise ValueError(error_msg)

            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != user_id:
                raise ValueError('Email already in use')
            user.email = data['email'].strip().lower()

        if 'password' in data:
            # Валидация пароля
            is_valid, error_msg = validate_password(data['password'])
            if not is_valid:
                raise ValueError(error_msg)
            user.password_hash = hash_password(data['password'])

        db.session.commit()
        return user.to_dict()
    except IntegrityError:
        db.session.rollback()
        raise ValueError('Email already in use')
    except Exception as e:
        db.session.rollback()
        raise
