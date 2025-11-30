from flask import jsonify

def success_response(data=None, status_code=200):
    """
    Стандартный формат успешного ответа API

    Returns:
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
    Стандартный формат ошибки API

    Returns:
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
