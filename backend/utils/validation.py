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

    if len(email) > 255:
        return False, "Email слишком длинный (максимум 255 символов)"

    # Simple email regex pattern
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

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
    # For text questions, options are not required
    if question_type == 'text':
        return True, None

    # For single/multiple choice, options are required
    if not options or not isinstance(options, list):
        return False, "Варианты ответов обязательны для вопросов с выбором"

    if len(options) < 2:
        return False, "Должно быть минимум 2 варианта ответа"

    # Check that correct answer exists in options
    if correct_answer:
        # For single choice, correct_answer is an index (string)
        if question_type == 'single':
            try:
                answer_index = int(correct_answer)
                if answer_index < 0 or answer_index >= len(options):
                    return False, "Правильный ответ вне диапазона вариантов"
            except ValueError:
                return False, "Правильный ответ должен быть номером варианта"

    return True, None
