/**
 * Динамическое управление формой создания/редактирования теста
 * Позволяет добавлять/удалять вопросы и варианты ответов
 */

// Счетчик вопросов для генерации уникальных индексов в именах полей формы
let questionCount = 0;

/**
 * Добавление нового вопроса в форму
 * Генерирует HTML карточки вопроса с двумя вариантами ответов по умолчанию
 * Имена полей формируются как questions[N][text], questions[N][options][M][text]
 */
function addQuestion() {
    questionCount++;
    const questionsList = document.getElementById('questions-list');

    const questionCard = document.createElement('div');
    questionCard.className = 'question-card';
    questionCard.dataset.questionIndex = questionCount;  // Для идентификации карточки при удалении/перемещении

    questionCard.innerHTML = `
        <div class="question-header">
            <span class="question-number">Вопрос ${questionCount + 1}</span>
            <div class="question-actions">
                <button type="button" class="icon-btn" onclick="moveQuestion(${questionCount}, 'up')" title="Переместить вверх">↑</button>
                <button type="button" class="icon-btn" onclick="moveQuestion(${questionCount}, 'down')" title="Переместить вниз">↓</button>
                <button type="button" class="icon-btn delete" onclick="removeQuestion(${questionCount})" title="Удалить">🗑️</button>
            </div>
        </div>

        <div class="form-group">
            <label>Текст вопроса</label>
            <input type="text" name="questions[${questionCount}][text]" placeholder="Введите текст вопроса" required>
        </div>

        <div class="form-group">
            <label>Тип вопроса</label>
            <select name="questions[${questionCount}][type]" class="question-type-select">
                <option value="single">Один правильный ответ</option>
                <option value="multiple">Несколько правильных ответов</option>
            </select>
        </div>

        <div class="form-group">
            <label>Варианты ответов (отметьте правильные)</label>
            <div class="answers-list" data-question="${questionCount}">
                <div class="answer-item">
                    <input type="checkbox" class="answer-checkbox" name="questions[${questionCount}][options][0][correct]" value="1">
                    <input type="text" class="answer-input" name="questions[${questionCount}][options][0][text]" placeholder="Вариант ответа 1" required>
                    <button type="button" class="answer-delete" onclick="removeAnswer(this)">✕</button>
                </div>
                <div class="answer-item">
                    <input type="checkbox" class="answer-checkbox" name="questions[${questionCount}][options][1][correct]" value="1">
                    <input type="text" class="answer-input" name="questions[${questionCount}][options][1][text]" placeholder="Вариант ответа 2" required>
                    <button type="button" class="answer-delete" onclick="removeAnswer(this)">✕</button>
                </div>
            </div>
            <button type="button" class="btn-secondary" style="margin-top: 12px;" onclick="addAnswer(${questionCount})">
                ➕ Добавить вариант
            </button>
        </div>
    `;

    questionsList.appendChild(questionCard);
    updateQuestionNumbers();  // Обновляем нумерацию после добавления
    
    // Добавляем обработчик изменения типа вопроса для нового вопроса
    const typeSelect = questionCard.querySelector('.question-type-select');
    if (typeSelect) {
        typeSelect.addEventListener('change', function() {
            handleQuestionTypeChange(this);
        });
    }
    
    // Добавляем обработчики для чекбоксов нового вопроса
    const checkboxes = questionCard.querySelectorAll('.answer-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const questionCard = this.closest('.question-card');
            const typeSelect = questionCard.querySelector('.question-type-select');
            if (typeSelect && typeSelect.value === 'single' && this.checked) {
                // Для single - снимаем все остальные
                checkboxes.forEach(cb => {
                    if (cb !== this) {
                        cb.checked = false;
                    }
                });
            }
        });
    });
}

/**
 * Удаление вопроса с подтверждением
 */
function removeQuestion(questionIndex) {
    if (confirm('Удалить этот вопрос?')) {
        const questionCard = document.querySelector(`[data-question-index="${questionIndex}"]`);
        if (questionCard) {
            questionCard.remove();
            updateQuestionNumbers();  // Пересчитываем номера оставшихся вопросов
        }
    }
}

/**
 * Перемещение вопроса вверх или вниз
 * Меняет порядок DOM элементов
 */
function moveQuestion(questionIndex, direction) {
    const questionCard = document.querySelector(`[data-question-index="${questionIndex}"]`);
    if (!questionCard) return;

    if (direction === 'up') {
        const prev = questionCard.previousElementSibling;
        if (prev) {
            questionCard.parentNode.insertBefore(questionCard, prev);
        }
    } else {
        const next = questionCard.nextElementSibling;
        if (next) {
            questionCard.parentNode.insertBefore(next, questionCard);
        }
    }

    updateQuestionNumbers();
}

/**
 * Добавление нового варианта ответа к вопросу
 */
function addAnswer(questionIndex) {
    const answersList = document.querySelector(`[data-question="${questionIndex}"]`);
    const currentAnswers = answersList.querySelectorAll('.answer-item').length;

    const answerItem = document.createElement('div');
    answerItem.className = 'answer-item';
    answerItem.innerHTML = `
        <input type="checkbox" class="answer-checkbox" name="questions[${questionIndex}][options][${currentAnswers}][correct]" value="1">
        <input type="text" class="answer-input" name="questions[${questionIndex}][options][${currentAnswers}][text]" placeholder="Вариант ответа ${currentAnswers + 1}" required>
        <button type="button" class="answer-delete" onclick="removeAnswer(this)">✕</button>
    `;

    answersList.appendChild(answerItem);
}

/**
 * Удаление варианта ответа (минимум 2 должны остаться)
 */
function removeAnswer(button) {
    const answerItem = button.parentElement;
    const answersList = answerItem.parentElement;

    if (answersList.querySelectorAll('.answer-item').length > 2) {
        answerItem.remove();
        updateAnswerIndices(answersList);  // Переиндексируем оставшиеся варианты
    } else {
        alert('Должно быть минимум 2 варианта ответа');
    }
}

/**
 * Обновление нумерации вопросов (после добавления/удаления/перемещения)
 */
function updateQuestionNumbers() {
    const questions = document.querySelectorAll('.question-card');
    questions.forEach((card, index) => {
        const questionNumber = card.querySelector('.question-number');
        questionNumber.textContent = `Вопрос ${index + 1}`;
    });
}

/**
 * Переиндексация вариантов ответов после удаления
 * Обновляет name атрибуты чтобы индексы шли подряд: [0], [1], [2]...
 */
function updateAnswerIndices(answersList) {
    const questionIndex = answersList.dataset.question;
    const answers = answersList.querySelectorAll('.answer-item');

    answers.forEach((answer, index) => {
        const checkbox = answer.querySelector('.answer-checkbox');
        const input = answer.querySelector('.answer-input');

        checkbox.name = `questions[${questionIndex}][options][${index}][correct]`;
        input.name = `questions[${questionIndex}][options][${index}][text]`;
        input.placeholder = `Вариант ответа ${index + 1}`;
    });
}

/**
 * Обработка изменения типа вопроса
 * Для single - автоматически снимает лишние чекбоксы, оставляя только один
 */
function handleQuestionTypeChange(selectElement) {
    const questionCard = selectElement.closest('.question-card');
    const questionIndex = questionCard.dataset.questionIndex;
    const questionType = selectElement.value;
    const answersList = questionCard.querySelector('.answers-list');
    
    if (!answersList) return;
    
    const checkboxes = answersList.querySelectorAll('.answer-checkbox');
    
    if (questionType === 'single') {
        // Для single - если выбрано больше одного, оставляем только первый выбранный
        const checked = Array.from(checkboxes).filter(cb => cb.checked);
        if (checked.length > 1) {
            // Оставляем только первый выбранный
            checked.slice(1).forEach(cb => {
                cb.checked = false;
            });
        }
        
        // Добавляем обработчик для автоматического снятия других при выборе нового
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                if (this.checked) {
                    // Снимаем все остальные
                    checkboxes.forEach(cb => {
                        if (cb !== this) {
                            cb.checked = false;
                        }
                    });
                }
            });
        });
    } else {
        // Для multiple - убираем ограничения (можно выбирать несколько)
        checkboxes.forEach(checkbox => {
            // Клонируем элемент, чтобы удалить все обработчики
            const newCheckbox = checkbox.cloneNode(true);
            checkbox.parentNode.replaceChild(newCheckbox, checkbox);
        });
    }
}

/**
 * Валидация формы перед отправкой
 * Проверяет, что для каждого вопроса выбрано правильное количество правильных ответов
 */
function validateForm() {
    const questionCards = document.querySelectorAll('.question-card');
    let isValid = true;
    const errors = [];
    
    questionCards.forEach((card, index) => {
        const questionType = card.querySelector('.question-type-select')?.value;
        const answersList = card.querySelector('.answers-list');
        if (!answersList) return;
        
        const checkboxes = answersList.querySelectorAll('.answer-checkbox');
        const checkedCount = Array.from(checkboxes).filter(cb => cb.checked).length;
        
        if (questionType === 'single') {
            if (checkedCount === 0) {
                isValid = false;
                errors.push(`Вопрос ${index + 1}: выберите один правильный ответ`);
            } else if (checkedCount > 1) {
                isValid = false;
                errors.push(`Вопрос ${index + 1}: для типа "Один правильный ответ" можно выбрать только один вариант`);
            }
        } else if (questionType === 'multiple') {
            if (checkedCount === 0) {
                isValid = false;
                errors.push(`Вопрос ${index + 1}: выберите хотя бы один правильный ответ`);
            }
        }
    });
    
    if (!isValid) {
        alert('Ошибки в форме:\n\n' + errors.join('\n'));
    }
    
    return isValid;
}

/**
 * Инициализация при загрузке страницы
 * Важно для страницы редактирования, где уже есть вопросы из БД
 */
document.addEventListener('DOMContentLoaded', function() {
    const existingQuestions = document.querySelectorAll('.question-card');
    existingQuestions.forEach((card, index) => {
        card.dataset.questionIndex = index;
        const answersList = card.querySelector('.answers-list');
        if (answersList) {
            answersList.dataset.question = index;
        }
        
        // Добавляем обработчик изменения типа вопроса
        const typeSelect = card.querySelector('.question-type-select');
        if (typeSelect) {
            typeSelect.addEventListener('change', function() {
                handleQuestionTypeChange(this);
            });
            // Инициализируем обработку для текущего типа
            handleQuestionTypeChange(typeSelect);
        }
        
        // Добавляем обработчики для чекбоксов существующих вопросов
        const checkboxes = card.querySelectorAll('.answer-checkbox');
        const questionType = typeSelect?.value || 'single';
        
        if (questionType === 'single') {
            checkboxes.forEach(checkbox => {
                checkbox.addEventListener('change', function() {
                    if (this.checked) {
                        checkboxes.forEach(cb => {
                            if (cb !== this) {
                                cb.checked = false;
                            }
                        });
                    }
                });
            });
        }
    });
    questionCount = existingQuestions.length;  // Устанавливаем счетчик по количеству существующих вопросов
    
    // Добавляем валидацию перед отправкой формы
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            if (!validateForm()) {
                e.preventDefault();
                return false;
            }
        });
    }
});
