from flask import Blueprint, request
from backend.services.test_service import create_question, update_question, delete_question
from backend.utils.responses import success_response, error_response
from backend.utils.jwt_utils import require_auth
from backend.utils.validation import validate_question_type, validate_question_options

questions_bp = Blueprint('questions', __name__, url_prefix='/api/tests')

@questions_bp.route('/<int:test_id>/questions', methods=['POST'])
@require_auth
def create(user_id, test_id):
    """
    Создать вопрос в тесте
    ---
    tags:
      - Questions
    security:
      - Bearer: []
    parameters:
      - name: test_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - question_text
            - question_type
          properties:
            question_text:
              type: string
              example: Что такое Python?
            question_type:
              type: string
              enum: [single, multiple, text]
              example: single
            options:
              type: array
              items:
                type: string
              example: ["Язык программирования", "База данных", "Фреймворк"]
            correct_answer:
              oneOf:
                - type: string
                - type: array
              example: "Язык программирования"
    responses:
      201:
        description: Вопрос создан
      400:
        description: Некорректные данные
    """
    data = request.json
    if not data or 'question_text' not in data or 'question_type' not in data:
        return error_response('Missing required fields', 400)

    # Validate question type
    is_valid_type, type_error = validate_question_type(data['question_type'])
    if not is_valid_type:
        return error_response(type_error, 400)

    # Validate options for choice questions
    is_valid_options, options_error = validate_question_options(
        data['question_type'],
        data.get('options', []),
        data.get('correct_answer')
    )
    if not is_valid_options:
        return error_response(options_error, 400)

    try:
        question = create_question(test_id, user_id, data)
        return success_response(question, 201)
    except ValueError as e:
        return error_response(str(e), 400)

@questions_bp.route('/<int:test_id>/questions/<int:question_id>', methods=['PUT'])
@require_auth
def update(user_id, test_id, question_id):
    """
    Обновить вопрос
    ---
    tags:
      - Questions
    security:
      - Bearer: []
    parameters:
      - name: test_id
        in: path
        type: integer
        required: true
      - name: question_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        schema:
          type: object
          properties:
            question_text:
              type: string
            question_type:
              type: string
            options:
              type: array
            correct_answer:
              oneOf:
                - type: string
                - type: array
    responses:
      200:
        description: Вопрос обновлен
      404:
        description: Вопрос не найден
    """
    data = request.json
    if not data:
        return error_response('No data provided', 400)

    try:
        question = update_question(test_id, question_id, user_id, data)
        return success_response(question)
    except ValueError as e:
        return error_response(str(e), 404)

@questions_bp.route('/<int:test_id>/questions/<int:question_id>', methods=['DELETE'])
@require_auth
def delete(user_id, test_id, question_id):
    """
    Удалить вопрос
    ---
    tags:
      - Questions
    security:
      - Bearer: []
    parameters:
      - name: test_id
        in: path
        type: integer
        required: true
      - name: question_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Вопрос удален
      404:
        description: Вопрос не найден
    """
    try:
        delete_question(test_id, question_id, user_id)
        return success_response({'message': 'Question deleted'})
    except ValueError as e:
        return error_response(str(e), 404)
