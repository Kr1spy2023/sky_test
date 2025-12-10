// Create and Edit Test Dynamic Form Handler
let questionCount = 0;

function addQuestion() {
    questionCount++;
    const questionsList = document.getElementById('questions-list');

    const questionCard = document.createElement('div');
    questionCard.className = 'question-card';
    questionCard.dataset.questionIndex = questionCount;

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

        <input type="hidden" name="questions[${questionCount}][type]" value="single">

        <div class="form-group">
            <label>Варианты ответов (отметьте правильный)</label>
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
    updateQuestionNumbers();
}

function removeQuestion(questionIndex) {
    if (confirm('Удалить этот вопрос?')) {
        const questionCard = document.querySelector(`[data-question-index="${questionIndex}"]`);
        if (questionCard) {
            questionCard.remove();
            updateQuestionNumbers();
        }
    }
}

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

function removeAnswer(button) {
    const answerItem = button.parentElement;
    const answersList = answerItem.parentElement;

    if (answersList.querySelectorAll('.answer-item').length > 2) {
        answerItem.remove();
        updateAnswerIndices(answersList);
    } else {
        alert('Должно быть минимум 2 варианта ответа');
    }
}

function updateQuestionNumbers() {
    const questions = document.querySelectorAll('.question-card');
    questions.forEach((card, index) => {
        const questionNumber = card.querySelector('.question-number');
        questionNumber.textContent = `Вопрос ${index + 1}`;
    });
}

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

// Initialize question count from existing questions
document.addEventListener('DOMContentLoaded', function() {
    const existingQuestions = document.querySelectorAll('.question-card');
    existingQuestions.forEach((card, index) => {
        card.dataset.questionIndex = index;
        const answersList = card.querySelector('.answers-list');
        if (answersList) {
            answersList.dataset.question = index;
        }
    });
    questionCount = existingQuestions.length;
});
