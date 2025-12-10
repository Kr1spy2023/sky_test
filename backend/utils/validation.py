"""
Validation utilities for user input
"""
import re


def validate_email(email):
    """
    Validate email format

    Args:
        email: Email address to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    if not email or not isinstance(email, str):
        return False, "Email обязателен"

    email = email.strip()

    if len(email) > 120:
        return False, "Email слишком длинный (максимум 120 символов)"

    # Улучшенная валидация email
    email_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9._-]*@[a-zA-Z0-9][a-zA-Z0-9.-]*\.[a-zA-Z]{2,}$'

    if not re.match(email_pattern, email):
        return False, "Неверный формат email"

    return True, None


def validate_password(password):
    """
    Validate password strength

    Args:
        password: Password to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    if not password or not isinstance(password, str):
        return False, "Пароль обязателен"

    if len(password) < 8:
        return False, "Пароль должен быть минимум 8 символов"

    if len(password) > 128:
        return False, "Пароль слишком длинный (максимум 128 символов)"

    # Проверка на наличие цифр
    if not re.search(r'\d', password):
        return False, "Пароль должен содержать хотя бы одну цифру"

    # Проверка на наличие заглавных букв
    if not re.search(r'[A-Z]', password):
        return False, "Пароль должен содержать хотя бы одну заглавную букву"

    # Проверка на наличие строчных букв
    if not re.search(r'[a-z]', password):
        return False, "Пароль должен содержать хотя бы одну строчную букву"

    return True, None


def validate_question_type(question_type):
    """
    Validate question type

    Args:
        question_type: Type of question

    Returns:
        tuple: (is_valid, error_message)
    """
    allowed_types = ['single', 'multiple', 'text']

    if not question_type:
        return False, "Тип вопроса обязателен"

    if question_type not in allowed_types:
        return False, f"Неверный тип вопроса. Разрешены: {', '.join(allowed_types)}"

    return True, None


def validate_question_options(question_type, options, correct_answer):
    """
    Validate question options and correct answer

    Args:
        question_type: Type of question
        options: List of answer options
        correct_answer: Correct answer value

    Returns:
        tuple: (is_valid, error_message)
    """

    if question_type == 'text':
        return True, None

    if not options or not isinstance(options, list):
        return False, "Варианты ответов обязательны для вопросов с выбором"

    if len(options) < 2:
        return False, "Должно быть минимум 2 варианта ответа"

    if correct_answer:
        if question_type == 'single':
            try:
                answer_index = int(correct_answer)
                if answer_index < 0 or answer_index >= len(options):
                    return False, "Правильный ответ вне диапазона вариантов"
            except ValueError:
                return False, "Правильный ответ должен быть номером варианта"

    return True, None
