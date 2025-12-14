"""
Утилиты для формирования стандартизированных ответов API
"""

from flask import jsonify

def success_response(data=None, status_code=200):
    """
    Формирование стандартного успешного ответа API

    Args:
        data: Данные для возврата клиенту (любой JSON-сериализуемый объект)
        status_code: HTTP статус код (по умолчанию 200)

    Returns:
        tuple: (Response, status_code)
            Response: Flask Response объект с JSON данными в формате:
                {
                    'success': True,
                    'data': {...},
                    'error': None
                }
    """
    return jsonify({
        'success': True,
        'data': data,
        'error': None
    }), status_code

def error_response(message, status_code=400):
    """
    Формирование стандартного ответа об ошибке API

    Args:
        message: Текст сообщения об ошибке
        status_code: HTTP статус код (по умолчанию 400)

    Returns:
        tuple: (Response, status_code)
            Response: Flask Response объект с JSON данными в формате:
                {
                    'success': False,
                    'data': None,
                    'error': "error message"
                }
    """
    return jsonify({
        'success': False,
        'data': None,
        'error': message
    }), status_code
