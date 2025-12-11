"""
Маршруты для отображения HTML страниц (views)
Обрабатывает все страницы интерфейса: вход, регистрация, дашборд, создание тестов и т.д.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from sqlalchemy.exc import IntegrityError, OperationalError
from datetime import datetime
from backend.models.user import User
from backend.models.test import Test
from backend.models import db

views_bp = Blueprint('views', __name__)

def login_required(f):
    """
    Декоратор для защиты страниц, требующих авторизации
    Если пользователь не залогинен - перенаправляет на страницу входа
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('views.login'))
        return f(*args, **kwargs)
    return decorated_function

@views_bp.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@views_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['name'] = user.name
            flash('Вы успешно вошли в систему', 'success')
            return redirect(url_for('views.dashboard'))
        else:
            flash('Неверный email или пароль', 'error')

    return render_template('login.html')

@views_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Страница регистрации"""
    if request.method == 'POST':
        name = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return render_template('register.html')

        # Валидация пароля
        from backend.utils.validation import validate_password
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            flash(error_msg, 'error')
            return render_template('register.html')

        # Проверка существования пользователя
        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует', 'error')
            return render_template('register.html')

        if User.query.filter_by(name=name).first():
            flash('Пользователь с таким именем уже существует', 'error')
            return render_template('register.html')

        # Создание нового пользователя
        try:
            user = User(name=name, email=email)
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            flash('Регистрация успешна! Теперь вы можете войти', 'success')
            return redirect(url_for('views.login'))
        except IntegrityError:
            db.session.rollback()
            flash('Ошибка при создании пользователя. Попробуйте другой email или имя.', 'error')
            return render_template('register.html')
        except Exception as e:
            db.session.rollback()
            flash('Произошла ошибка при регистрации', 'error')
            return render_template('register.html')

    return render_template('register.html')

@views_bp.route('/dashboard')
@login_required
def dashboard():
    """Дашборд пользователя"""
    user = User.query.get(session['user_id'])
    if not user:
        flash('Пользователь не найден', 'error')
        return redirect(url_for('views.login'))

    tests = Test.query.filter_by(user_id=user.id).all()

    # Подсчет статистики
    stats = {
        'total': len(tests),
        'published': len([t for t in tests if t.is_published]),
        'attempts': sum([len(t.attempts) for t in tests])
    }

    # Добавление дополнительной информации к тестам
    for test in tests:
        test.questions_count = len(test.questions)
        test.attempts_count = len(test.attempts)

    return render_template('dashboard.html', user=user, tests=tests, stats=stats, active_page='dashboard')

@views_bp.route('/create-test', methods=['GET', 'POST'])
@login_required
def create_test():
    """Страница создания теста"""
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('views.login'))

    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            action = request.form.get('action', 'draft')
            is_published = (action == 'publish')

            if not title:
                flash('Введите название теста', 'error')
                return render_template('create_test.html', user=user, active_page='create_test')

            # Создать тест
            test = Test(
                title=title,
                description=description,
                user_id=user.id,
                is_published=is_published
            )

            if is_published:
                import secrets
                test.link_token = secrets.token_urlsafe(32)

            db.session.add(test)
            db.session.flush()

            # Парсинг вопросов из формы
            # Форма генерируется JavaScript и имеет структуру: questions[0][text], questions[0][options][0][text]
            from backend.models.question import Question
            import json

            # Сначала находим все индексы вопросов (может быть не подряд, если удалялись)
            question_indices = set()
            for key in request.form.keys():
                if key.startswith('questions[') and key.endswith('][text]'):
                    # Извлекаем индекс из строки вида "questions[3][text]"
                    index = key.split('[')[1].split(']')[0]
                    question_indices.add(int(index))

            # Обрабатываем каждый вопрос по порядку
            for idx in sorted(question_indices):
                question_text = request.form.get(f'questions[{idx}][text]', '').strip()
                question_type = request.form.get(f'questions[{idx}][type]', 'single')

                if not question_text:
                    continue

                # Собираем все варианты ответов для этого вопроса
                options = []
                correct_answers = []
                option_idx = 0
                # Идем по индексам пока не закончатся варианты
                while True:
                    option_text = request.form.get(f'questions[{idx}][options][{option_idx}][text]', '').strip()
                    if not option_text:
                        break  # Варианты закончились

                    options.append(option_text)
                    # Если чекбокс "правильный ответ" был отмечен
                    if request.form.get(f'questions[{idx}][options][{option_idx}][correct]'):
                        correct_answers.append(option_idx)

                    option_idx += 1

                # Формат правильных ответов зависит от типа вопроса
                # single: сохраняем как список (для совместимости с логикой проверки)
                # multiple: сохраняем как список
                correct_answer_json = json.dumps(correct_answers) if correct_answers else None

                # Создаем вопрос и сохраняем в БД
                # options и correct_answer сохраняются как JSON строки
                question = Question(
                    test_id=test.id,
                    question_text=question_text,
                    question_type=question_type,
                    options=json.dumps(options) if options else None,
                    correct_answer=correct_answer_json,
                    order_index=idx
                )
                db.session.add(question)

            db.session.commit()
            flash('Тест успешно создан' if is_published else 'Черновик сохранён', 'success')
            return redirect(url_for('views.dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при создании теста: {str(e)}', 'error')
            return render_template('create_test.html', user=user, active_page='create_test')

    return render_template('create_test.html', user=user, active_page='create_test')

@views_bp.route('/edit-test/<int:test_id>', methods=['GET', 'POST'])
@login_required
def edit_test(test_id):
    """Страница редактирования теста"""
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('views.login'))

    test = Test.query.get_or_404(test_id)

    # Проверка прав доступа
    if test.user_id != user.id:
        flash('У вас нет прав для редактирования этого теста', 'error')
        return redirect(url_for('views.dashboard'))

    if request.method == 'POST':
        action = request.form.get('action', 'draft')

        # Удаление теста
        if action == 'delete':
            try:
                db.session.delete(test)
                db.session.commit()
                flash('Тест успешно удалён', 'success')
                return redirect(url_for('views.dashboard'))
            except Exception as e:
                db.session.rollback()
                flash('Ошибка при удалении теста', 'error')
                return redirect(url_for('views.edit_test', test_id=test_id))

        # Обновление теста
        try:
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            is_published = (action == 'publish')

            if not title:
                flash('Введите название теста', 'error')
                return render_template('edit_test.html', user=user, test=test)

            # Обновить основную информацию
            test.title = title
            test.description = description
            test.is_published = is_published

            if is_published and not test.link_token:
                import secrets
                test.link_token = secrets.token_urlsafe(32)

            # Удалить все старые вопросы
            from backend.models.question import Question
            import json

            for question in test.questions:
                db.session.delete(question)

            # Добавить новые вопросы
            question_indices = set()
            for key in request.form.keys():
                if key.startswith('questions[') and key.endswith('][text]'):
                    index = key.split('[')[1].split(']')[0]
                    question_indices.add(int(index))

            for idx in sorted(question_indices):
                question_text = request.form.get(f'questions[{idx}][text]', '').strip()
                question_type = request.form.get(f'questions[{idx}][type]', 'single')

                if not question_text:
                    continue

                # Собрать варианты ответов
                options = []
                correct_answers = []
                option_idx = 0
                while True:
                    option_text = request.form.get(f'questions[{idx}][options][{option_idx}][text]', '').strip()
                    if not option_text:
                        break

                    options.append(option_text)
                    if request.form.get(f'questions[{idx}][options][{option_idx}][correct]'):
                        correct_answers.append(option_idx)

                    option_idx += 1

                # Создать вопрос
                question = Question(
                    test_id=test.id,
                    question_text=question_text,
                    question_type=question_type,
                    options=json.dumps(options) if options else None,
                    correct_answer=json.dumps(correct_answers) if correct_answers else None,
                    order_index=idx
                )
                db.session.add(question)

            db.session.commit()
            flash('Тест успешно обновлён' if is_published else 'Черновик сохранён', 'success')
            return redirect(url_for('views.dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении теста: {str(e)}', 'error')
            return render_template('edit_test.html', user=user, test=test)

    return render_template('edit_test.html', user=user, test=test)

@views_bp.route('/statistics/<int:test_id>')
@login_required
def statistics(test_id):
    """Страница статистики теста"""
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('views.login'))

    test = Test.query.get_or_404(test_id)

    # Проверка прав доступа
    if test.user_id != user.id:
        flash('У вас нет прав для просмотра статистики этого теста', 'error')
        return redirect(url_for('views.dashboard'))

    return render_template('statistics.html', user=user, test=test)

@views_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Страница настроек"""
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('views.login'))

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'change_password':
            # Обработка смены пароля
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            if not user.check_password(current_password):
                flash('Неверный текущий пароль', 'error')
            elif new_password != confirm_password:
                flash('Пароли не совпадают', 'error')
            else:
                try:
                    # Валидация
                    from backend.utils.validation import validate_password
                    is_valid, error_msg = validate_password(new_password)
                    if not is_valid:
                        flash(error_msg, 'error')
                    else:
                        user.set_password(new_password)
                        db.session.commit()
                        flash('Пароль успешно изменён', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash('Ошибка при изменении пароля', 'error')
        else:
            # Обработка изменения профиля
            name = request.form.get('name')
            email = request.form.get('email')

            try:
                if name:
                    user.name = name.strip()
                if email and email != user.email:
                    # Проверка уникальности email
                    existing = User.query.filter_by(email=email).first()
                    if existing:
                        flash('Email уже используется', 'error')
                    else:
                        user.email = email.strip().lower()

                db.session.commit()
                flash('Профиль успешно обновлён', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Ошибка при обновлении профиля', 'error')

        return redirect(url_for('views.settings'))

    return render_template('settings.html', user=user, active_page='settings')

@views_bp.route('/take-test/<string:link_token>', methods=['GET', 'POST'])
def take_test(link_token):
    """Страница прохождения теста"""
    from backend.models.test import Test
    from backend.models.attempt import TestAttempt
    from backend.models.answer import Answer
    from backend.models.question import Question
    import json

    test = Test.query.filter_by(link_token=link_token).first()
    if not test or not test.is_published:
        flash('Тест не найден или не опубликован', 'error')
        return redirect(url_for('views.index'))

    if request.method == 'POST':
        # Только авторизованные пользователи могут сохранять результаты
        if 'user_id' not in session:
            flash('Войдите в систему для сохранения результатов', 'warning')
            return redirect(url_for('views.login'))

        try:
            # Создаем запись о попытке прохождения теста
            attempt = TestAttempt(
                test_id=test.id,
                user_id=session['user_id']
            )
            db.session.add(attempt)
            db.session.flush()  # Получаем attempt.id для связи с ответами

            # Обрабатываем каждый вопрос и подсчитываем правильные ответы
            correct_count = 0
            total_questions = len(test.questions)

            for question in test.questions:
                # Получаем ответ пользователя из формы (поле называется question_{id})
                answer_key = f'question_{question.id}'
                user_answer = request.form.get(answer_key)

                # Для множественного выбора (checkboxes) нужен getlist
                if question.question_type == 'multiple':
                    user_answer = request.form.getlist(answer_key)
                    user_answer = json.dumps([int(a) for a in user_answer]) if user_answer else ''
                elif question.question_type == 'single':
                    # Для single типа сохраняем как число
                    user_answer = user_answer if user_answer else ''

                # Сохраняем ответ в БД
                answer = Answer(
                    attempt_id=attempt.id,
                    question_id=question.id,
                    user_answer=user_answer
                )
                db.session.add(answer)

                # Проверяем правильность ответа
                if question.correct_answer:
                    try:
                        correct = json.loads(question.correct_answer)
                        # Проверка для множественного выбора (порядок не важен, поэтому sorted)
                        if question.question_type == 'multiple':
                            user_ans = json.loads(user_answer) if user_answer else []
                            if isinstance(correct, list) and isinstance(user_ans, list):
                                if sorted(user_ans) == sorted(correct):
                                    correct_count += 1
                        # Проверка для одиночного выбора
                        elif question.question_type == 'single':
                            if user_answer:
                                user_ans_int = int(user_answer)
                                # correct может быть списком [0] или числом 0
                                if isinstance(correct, list):
                                    if len(correct) > 0 and user_ans_int == correct[0]:
                                        correct_count += 1
                                else:
                                    if user_ans_int == correct:
                                        correct_count += 1
                        # Проверка для текстового ответа (без учета регистра)
                        else:  # text
                            if user_answer and user_answer.strip().lower() == str(correct).lower():
                                correct_count += 1
                    except:
                        pass  # Игнорируем ошибки парсинга

            # Подсчитываем итоговый процент правильных ответов
            attempt.score = int((correct_count / total_questions) * 100) if total_questions > 0 else 0
            attempt.completed = True
            attempt.finished_at = datetime.utcnow()  # Фиксируем время завершения

            db.session.commit()

            # Перенаправляем на страницу с результатом
            return redirect(url_for('views.test_result', attempt_id=attempt.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при отправке теста: {str(e)}', 'error')
            return render_template('take_test.html', test=test)

    return render_template('take_test.html', test=test)

@views_bp.route('/test-result/<int:attempt_id>')
def test_result(attempt_id):
    """Страница результата прохождения теста"""
    from backend.models.attempt import TestAttempt

    attempt = TestAttempt.query.get_or_404(attempt_id)
    test = Test.query.get_or_404(attempt.test_id)

    # Проверка прав доступа (может видеть только свой результат или создатель теста)
    if 'user_id' in session:
        if session['user_id'] != attempt.user_id and session['user_id'] != test.user_id:
            flash('У вас нет прав для просмотра этого результата', 'error')
            return redirect(url_for('views.index'))
    else:
        flash('Войдите в систему для просмотра результатов', 'warning')
        return redirect(url_for('views.login'))

    # Подсчет правильных ответов
    total_questions = len(test.questions)
    correct_count = int((attempt.score * total_questions) / 100)

    return render_template('test_result.html',
                         attempt=attempt,
                         test=test,
                         correct_count=correct_count,
                         total_questions=total_questions)

@views_bp.route('/logout')
def logout():
    """Выход из системы"""
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('views.index'))
