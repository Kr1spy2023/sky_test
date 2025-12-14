"""
Утилиты валидации входных данных пользователя
"""

import re


def validate_email(email):
    """
    Валидация формата email адреса

    Args:
        email: Email адрес для проверки

    Returns:
        tuple: (is_valid, error_message)
            is_valid: True если email корректен, False в противном случае
            error_message: Сообщение об ошибке или None если валидация прошла успешно
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
    Валидация надежности пароля

    Args:
        password: Пароль для проверки

    Returns:
        tuple: (is_valid, error_message)
            is_valid: True если пароль соответствует требованиям, False в противном случае
            error_message: Сообщение об ошибке или None если валидация прошла успешно
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
    Валидация типа вопроса

    Разрешенные типы вопросов:
    - 'single': выбор одного варианта ответа (radio buttons)
    - 'multiple': выбор нескольких вариантов ответа (checkboxes)


    Args:
        question_type: Тип вопроса для проверки

    Returns:
        tuple: (is_valid, error_message)
            is_valid: True если тип вопроса допустим, False в противном случае
            error_message: Сообщение об ошибке или None если валидация прошла успешно
    """
    allowed_types = ['single', 'multiple', 'text']

    if not question_type:
        return False, "Тип вопроса обязателен"

    if question_type not in allowed_types:
        return False, f"Неверный тип вопроса. Разрешены: {', '.join(allowed_types)}"

    return True, None


def validate_question_options(question_type, options, correct_answer):
    """
    Валидация вариантов ответов и правильного ответа для вопроса

    Правила валидации:
    - Для типов 'single' и 'multiple' варианты ответов обязательны (минимум 2)
    - Правильный ответ должен соответствовать типу вопроса:
      * 'single': одно число (индекс варианта) или список с одним элементом
      * 'multiple': список индексов вариантов (минимум один)
    - Индексы правильных ответов должны быть в допустимом диапазоне

    Args:
        question_type: Тип вопроса ('single', 'multiple')
        options: Список вариантов ответов
        correct_answer: Правильный ответ (число, список или строка в зависимости от типа)

    Returns:
        tuple: (is_valid, error_message)
            is_valid: True если варианты и правильный ответ корректны, False в противном случае
            error_message: Сообщение об ошибке или None если валидация прошла успешно
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
                # correct_answer может быть числом или списком с одним элементом
                if isinstance(correct_answer, list):
                    if len(correct_answer) != 1:
                        return False, "Для типа 'single' должен быть выбран один правильный ответ"
                    answer_index = int(correct_answer[0])
                else:
                    answer_index = int(correct_answer)
                
                if answer_index < 0 or answer_index >= len(options):
                    return False, "Правильный ответ вне диапазона вариантов"
            except (ValueError, TypeError, IndexError):
                return False, "Правильный ответ должен быть номером варианта"
        elif question_type == 'multiple':
            if not isinstance(correct_answer, list):
                return False, "Для типа 'multiple' правильный ответ должен быть списком"
            if len(correct_answer) == 0:
                return False, "Для типа 'multiple' должен быть выбран хотя бы один правильный ответ"
            try:
                # Проверяем, что все индексы валидны
                for idx in correct_answer:
                    answer_index = int(idx)
                    if answer_index < 0 or answer_index >= len(options):
                        return False, f"Правильный ответ {answer_index} вне диапазона вариантов"
            except (ValueError, TypeError):
                return False, "Правильный ответ должен содержать номера вариантов"

    return True, None
