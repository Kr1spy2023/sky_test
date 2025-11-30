/**
 * Create/Edit test page logic
 * Fixed: question duplication, inline CSS, XSS vulnerabilities, event listeners
 */

let currentTestId = null;
let loadedQuestions = []; // Store original question IDs for updates

document.addEventListener('DOMContentLoaded', () => {
    requireAuth();

    // Check if we're editing an existing test
    const urlParams = new URLSearchParams(window.location.search);
    const testId = urlParams.get('id');
    if (testId) {
        currentTestId = testId;
        loadTestData(testId);
    }

    // Event listeners (using event delegation for better performance)
    document.getElementById('addQuestionBtn').addEventListener('click', () => addQuestion());
    document.getElementById('publishBtn').addEventListener('click', () => saveTest(true));
    document.getElementById('draftBtn').addEventListener('click', () => saveTest(false));
    document.getElementById('cancelBtn').addEventListener('click', () => {
        window.location.href = 'dashboard.html';
    });

    // Use event delegation for dynamic question elements
    document.getElementById('questionsList').addEventListener('click', handleQuestionListClick);
    document.getElementById('questionsList').addEventListener('change', handleQuestionListChange);
});

/**
 * Load existing test data for editing
 */
async function loadTestData(testId) {
    try {
        const test = await API.tests.get(testId);

        // Set test info
        safeSetText(document.getElementById('test-title'), test.title);
        document.getElementById('test-title').value = test.title;
        document.getElementById('test-description').value = test.description || '';

        // Load questions
        if (test.questions && test.questions.length > 0) {
            test.questions.forEach((question) => {
                addQuestion(question);
                // Store original question ID for updates
                loadedQuestions.push({
                    id: question.id,
                    order_index: question.order_index
                });
            });
        }
    } catch (error) {
        console.error('Error loading test:', error);
        showNotification('Ошибка при загрузке теста: ' + error.message, 'error');
    }
}

/**
 * Add a new question card
 * @param {Object} questionData - Optional question data for editing
 */
function addQuestion(questionData = null) {
    const questionsList = document.getElementById('questionsList');
    const questionIndex = questionsList.children.length;

    // Create question card using safe methods
    const questionCard = createElement('div', 'question-card');
    questionCard.dataset.questionId = questionData?.id || ''; // Store question ID if editing

    // Question header
    const header = createElement('div', 'question-header');
    const questionNumber = createElement('span', 'question-number', `Вопрос ${questionIndex + 1}`);
    const deleteBtn = createElement('button', 'btn-icon delete', '✕');
    deleteBtn.type = 'button';
    deleteBtn.title = 'Удалить вопрос';
    header.appendChild(questionNumber);
    header.appendChild(deleteBtn);

    // Question text input
    const textGroup = createElement('div', 'form-group');
    const textLabel = createElement('label', '', 'Текст вопроса');
    const textInput = createElement('input');
    textInput.type = 'text';
    textInput.className = 'question-text';
    textInput.placeholder = 'Введите текст вопроса';
    textInput.value = questionData?.question_text || '';
    textGroup.appendChild(textLabel);
    textGroup.appendChild(textInput);

    // Question type selector
    const typeGroup = createElement('div', 'form-group');
    const typeLabel = createElement('label', '', 'Тип вопроса');
    const typeSelect = createElement('select', 'question-type');
    const types = [
        { value: 'single', label: 'Одиночный выбор' },
        { value: 'multiple', label: 'Множественный выбор' },
        { value: 'text', label: 'Текстовый ответ' }
    ];
    types.forEach(type => {
        const option = createElement('option', '', type.label);
        option.value = type.value;
        if (questionData?.question_type === type.value) {
            option.selected = true;
        }
        typeSelect.appendChild(option);
    });
    typeGroup.appendChild(typeLabel);
    typeGroup.appendChild(typeSelect);

    // Options container
    const optionsGroup = createElement('div', 'form-group options-group');
    if (questionData?.question_type === 'text') {
        optionsGroup.style.display = 'none';
    }
    const optionsLabel = createElement('label', '', 'Варианты ответов');
    const answersList = createElement('div', 'answers-list');

    // Add existing options or default empty ones
    const options = questionData?.options || ['', '', '', ''];
    options.forEach((option) => {
        answersList.appendChild(createAnswerOption(option));
    });

    const addOptionBtn = createElement('button', 'btn-add-option', '➕ Добавить вариант');
    addOptionBtn.type = 'button';

    optionsGroup.appendChild(optionsLabel);
    optionsGroup.appendChild(answersList);
    optionsGroup.appendChild(addOptionBtn);

    // Correct answer input
    const answerGroup = createElement('div', 'form-group');
    const answerLabel = createElement('label', '', 'Правильный ответ');
    const answerInput = createElement('input');
    answerInput.type = 'text';
    answerInput.className = 'correct-answer';
    answerInput.placeholder = 'Введите правильный ответ';
    answerInput.value = questionData?.correct_answer || '';
    const answerHint = createElement('p', 'helper-text', 'Для выбора варианта укажите его номер (например: 1 или 1,2,3)');
    answerGroup.appendChild(answerLabel);
    answerGroup.appendChild(answerInput);
    answerGroup.appendChild(answerHint);

    // Assemble question card
    questionCard.appendChild(header);
    questionCard.appendChild(textGroup);
    questionCard.appendChild(typeGroup);
    questionCard.appendChild(optionsGroup);
    questionCard.appendChild(answerGroup);

    questionsList.appendChild(questionCard);
}

/**
 * Create a single answer option element
 * @param {string} value - Option text
 * @returns {HTMLElement} Answer option element
 */
function createAnswerOption(value = '') {
    const answerItem = createElement('div', 'option-item');

    const input = createElement('input');
    input.type = 'text';
    input.className = 'option-input';
    input.placeholder = 'Вариант ответа';
    input.value = value;

    const deleteBtn = createElement('button', 'btn-remove-option', '✕');
    deleteBtn.type = 'button';
    deleteBtn.title = 'Удалить вариант';

    answerItem.appendChild(input);
    answerItem.appendChild(deleteBtn);

    return answerItem;
}

/**
 * Handle clicks within questions list (event delegation)
 */
function handleQuestionListClick(e) {
    const target = e.target;

    // Delete question
    if (target.classList.contains('delete') || target.closest('.btn-icon.delete')) {
        const questionCard = target.closest('.question-card');
        if (questionCard && confirm('Удалить этот вопрос?')) {
            questionCard.remove();
            updateQuestionNumbers();
        }
    }

    // Add answer option
    if (target.classList.contains('btn-add-option')) {
        const answersList = target.previousElementSibling;
        if (answersList && answersList.classList.contains('answers-list')) {
            answersList.appendChild(createAnswerOption());
        }
    }

    // Remove answer option
    if (target.classList.contains('btn-remove-option')) {
        const optionItem = target.closest('.option-item');
        if (optionItem) {
            optionItem.remove();
        }
    }
}

/**
 * Handle changes within questions list (event delegation)
 */
function handleQuestionListChange(e) {
    const target = e.target;

    // Toggle options visibility based on question type
    if (target.classList.contains('question-type')) {
        const questionCard = target.closest('.question-card');
        const optionsGroup = questionCard.querySelector('.options-group');
        if (target.value === 'text') {
            optionsGroup.style.display = 'none';
        } else {
            optionsGroup.style.display = 'block';
        }
    }
}

/**
 * Update question numbers after deletion
 */
function updateQuestionNumbers() {
    const questionCards = document.querySelectorAll('.question-card');
    questionCards.forEach((card, index) => {
        safeSetText(card.querySelector('.question-number'), `Вопрос ${index + 1}`);
    });
}

/**
 * Save test (create/update) and questions
 * @param {boolean} publish - Whether to publish immediately
 */
async function saveTest(publish) {
    const title = document.getElementById('test-title').value.trim();
    const description = document.getElementById('test-description').value.trim();

    // Validation
    if (!title) {
        showNotification('Введите название теста', 'error');
        return;
    }

    const questionsList = document.querySelectorAll('.question-card');
    if (questionsList.length === 0) {
        showNotification('Добавьте хотя бы один вопрос', 'error');
        return;
    }

    // Get buttons and show loading state
    const publishBtn = document.getElementById('publishBtn');
    const draftBtn = document.getElementById('draftBtn');
    const cancelBtn = document.getElementById('cancelBtn');

    const activeBtn = publish ? publishBtn : draftBtn;
    const originalText = activeBtn.textContent;

    // Disable all buttons
    publishBtn.disabled = true;
    draftBtn.disabled = true;
    cancelBtn.disabled = true;

    // Show loading text
    activeBtn.textContent = publish ? 'Публикация...' : 'Сохранение...';

    try {
        let testId;

        // Create or update test
        if (currentTestId) {
            // Update existing test
            await API.tests.update(currentTestId, {
                title: title,
                description: description
            });
            testId = currentTestId;

            // CRITICAL FIX: Delete old questions before creating new ones
            for (const oldQuestion of loadedQuestions) {
                try {
                    await API.questions.delete(testId, oldQuestion.id);
                } catch (error) {
                    console.warn('Error deleting old question:', error);
                }
            }
            loadedQuestions = []; // Clear loaded questions
        } else {
            // Create new test
            const test = await API.tests.create({
                title: title,
                description: description
            });
            testId = test.id;
            currentTestId = testId; // Store for future saves
        }

        // Validate and save all questions
        for (let i = 0; i < questionsList.length; i++) {
            const card = questionsList[i];
            const questionText = card.querySelector('.question-text').value.trim();
            const questionType = card.querySelector('.question-type').value;
            const correctAnswer = card.querySelector('.correct-answer').value.trim();

            // Validation
            if (!questionText) {
                showNotification(`Заполните текст вопроса ${i + 1}`, 'error');
                return; // CRITICAL FIX: return from function, not just loop
            }

            if (!correctAnswer) {
                showNotification(`Укажите правильный ответ для вопроса ${i + 1}`, 'error');
                return; // CRITICAL FIX: return from function, not just loop
            }

            // Get options for choice questions
            let options = [];
            if (questionType !== 'text') {
                const answerInputs = card.querySelectorAll('.option-input');
                options = Array.from(answerInputs)
                    .map(input => input.value.trim())
                    .filter(val => val);

                if (options.length === 0) {
                    showNotification(`Добавьте варианты ответов для вопроса ${i + 1}`, 'error');
                    return; // CRITICAL FIX: return from function, not just loop
                }
            }

            const questionData = {
                question_text: questionText,
                question_type: questionType,
                options: options,
                correct_answer: correctAnswer,
                order_index: i
            };

            // CRITICAL FIX: Always CREATE (old questions already deleted)
            await API.questions.create(testId, questionData);
        }

        // Publish if requested
        if (publish) {
            await API.tests.publish(testId);
            showNotification('Тест успешно опубликован!', 'success');
        } else {
            showNotification('Тест успешно сохранен!', 'success');
        }

        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1000);
    } catch (error) {
        console.error('Error saving test:', error);
        showNotification('Ошибка при сохранении: ' + error.message, 'error');

        // Re-enable buttons on error
        publishBtn.disabled = false;
        draftBtn.disabled = false;
        cancelBtn.disabled = false;
        activeBtn.textContent = originalText;
    }
}

// Warn before leaving page with unsaved changes
window.addEventListener('beforeunload', (e) => {
    const title = document.getElementById('test-title')?.value.trim();
    const questionsList = document.querySelectorAll('.question-card');

    // Only warn if there's unsaved content
    if (title || questionsList.length > 0) {
        e.preventDefault();
        e.returnValue = '';
        return '';
    }
});
