/**
 * Take test page logic
 * Supports both token-based and ID-based test loading
 * Fixed: Page refresh loop, added proper timer
 */

let currentAttemptId = null;
let currentQuestionIndex = 0;
let testData = null;
let answers = {};
let isSubmittingAnswer = false; // Prevent double submissions
let questionTimer = null; // Timer for current question
let timeRemaining = 60; // 60 seconds = 1 minute per question

/**
 * Show page loader
 */
function showPageLoader() {
    const loader = document.getElementById('pageLoader');
    if (loader) {
        loader.classList.remove('hidden');
    }
}

/**
 * Hide page loader and show content with fade-in
 */
function hidePageLoader() {
    const loader = document.getElementById('pageLoader');
    const body = document.body;

    if (loader) {
        loader.classList.add('hidden');
    }

    if (body) {
        body.classList.add('loaded');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    requireAuth();

    // Get test ID or token from URL
    const params = new URLSearchParams(window.location.search);
    const testId = params.get('id');
    const token = params.get('token');

    if (!testId && !token) {
        showNotification('Тест не найден', 'error');
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 2000);
        return;
    }

    // Start test using either ID or token
    if (token) {
        startTestByToken(token);
    } else {
        startTest(testId);
    }

    // Event listeners with preventDefault to avoid page refresh
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const exitBtn = document.getElementById('exitBtn');

    if (prevBtn) {
        prevBtn.addEventListener('click', (e) => {
            e.preventDefault();
            previousQuestion();
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', (e) => {
            e.preventDefault();
            nextQuestion();
        });
    }

    if (exitBtn) {
        exitBtn.addEventListener('click', (e) => {
            e.preventDefault();
            if (confirm('Вы уверены? Прогресс будет потерян.')) {
                stopTimer();
                window.location.href = 'dashboard.html';
            }
        });
    }
});

/**
 * Start test by token (for public links)
 */
async function startTestByToken(token) {
    try {
        // Show loader
        showPageLoader();

        // Load test data using token
        testData = await API.tests.getByLink(token);

        if (!testData) {
            throw new Error('Тест не найден или не опубликован');
        }

        safeSetText(document.getElementById('testTitle'), testData.title);
        safeSetText(document.getElementById('totalQuestions'), testData.questions.length.toString());

        // Start attempt using test ID from loaded data
        const attempt = await API.attempts.start(testData.id);
        currentAttemptId = attempt.id;

        // Hide loader and show content
        hidePageLoader();

        // Display first question
        displayQuestion(0);
    } catch (error) {
        hidePageLoader(); // Hide loader even on error
        console.error('Error starting test by token:', error);
        showNotification('Ошибка при загрузке теста: ' + error.message, 'error');
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 2000);
    }
}

/**
 * Start test by ID (for direct access)
 */
async function startTest(testId) {
    try {
        // Show loader
        showPageLoader();

        // Load test data
        testData = await API.tests.get(testId);
        safeSetText(document.getElementById('testTitle'), testData.title);
        safeSetText(document.getElementById('totalQuestions'), testData.questions.length.toString());

        // Start attempt
        const attempt = await API.attempts.start(testId);
        currentAttemptId = attempt.id;

        // Hide loader and show content
        hidePageLoader();

        // Display first question
        displayQuestion(0);
    } catch (error) {
        hidePageLoader(); // Hide loader even on error
        console.error('Error starting test:', error);
        showNotification('Ошибка при загрузке теста: ' + error.message, 'error');
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 2000);
    }
}

/**
 * Start timer for current question (1 minute per question)
 */
function startTimer() {
    // Stop any existing timer
    stopTimer();

    // Reset time to 1 minute
    timeRemaining = 60;
    updateTimerDisplay();

    // Start new timer
    questionTimer = setInterval(() => {
        timeRemaining--;
        updateTimerDisplay();

        // Time's up!
        if (timeRemaining <= 0) {
            stopTimer();
            handleTimeUp();
        }
    }, 1000); // Update every second
}

/**
 * Stop the timer
 */
function stopTimer() {
    if (questionTimer) {
        clearInterval(questionTimer);
        questionTimer = null;
    }
}

/**
 * Update timer display (only updates text, no reload!)
 */
function updateTimerDisplay() {
    const timerElement = document.getElementById('timeRemaining');
    if (timerElement) {
        const minutes = Math.floor(timeRemaining / 60);
        const seconds = timeRemaining % 60;
        const timeString = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        safeSetText(timerElement, timeString);

        // Change color when time is running out
        if (timeRemaining <= 10) {
            timerElement.style.color = '#ef4444'; // Red
        } else if (timeRemaining <= 30) {
            timerElement.style.color = '#f59e0b'; // Orange
        } else {
            timerElement.style.color = ''; // Default
        }
    }
}

/**
 * Handle when time runs out
 */
async function handleTimeUp() {
    showNotification('Время вышло! Переход к следующему вопросу', 'warning');

    // Auto-move to next question or finish test
    if (currentQuestionIndex < testData.questions.length - 1) {
        // Move to next question
        await nextQuestion();
    } else {
        // Last question - finish test
        showNotification('Тест завершён (время истекло)', 'info');
        await finishTest();
    }
}

/**
 * Display question at given index
 */
function displayQuestion(index) {
    currentQuestionIndex = index;
    const question = testData.questions[index];

    // Start timer for this question
    startTimer();

    // Update counters
    safeSetText(document.getElementById('currentQuestion'), (index + 1).toString());

    // Update progress bar
    const progress = ((index + 1) / testData.questions.length) * 100;
    document.getElementById('progressFill').style.width = progress + '%';

    // Update question text
    safeSetText(document.getElementById('questionText'), question.question_text);

    // Update answers
    const answersList = document.getElementById('answersList');
    answersList.innerHTML = '';

    if (question.question_type === 'text') {
        // Text input for text questions
        const textInput = createElement('textarea');
        textInput.id = 'textAnswer';
        textInput.placeholder = 'Введите ваш ответ...';
        textInput.className = 'text-answer-input';
        textInput.value = answers[question.id] || '';

        textInput.addEventListener('input', () => {
            answers[question.id] = textInput.value;
        });

        answersList.appendChild(textInput);
    } else if (question.options && question.options.length > 0) {
        // Multiple choice questions
        question.options.forEach((option, idx) => {
            const label = createElement('label', 'answer-option');

            const isSelected = answers[question.id] === (idx + 1).toString();
            if (isSelected) {
                label.classList.add('selected');
            }

            const radioCircle = createElement('div', 'radio-circle');
            if (isSelected) {
                const innerCircle = createElement('div', 'radio-inner');
                radioCircle.appendChild(innerCircle);
            }

            const answerText = createElement('span', 'answer-text');
            safeSetText(answerText, option);

            label.appendChild(radioCircle);
            label.appendChild(answerText);

            label.addEventListener('click', async (e) => {
                e.preventDefault();
                e.stopPropagation();

                // Prevent multiple submissions
                if (isSubmittingAnswer) {
                    return;
                }

                const answerValue = (idx + 1).toString();

                // Save answer locally
                answers[question.id] = answerValue;

                // Update UI immediately WITHOUT reloading page
                updateAnswerSelection(answersList, idx);

                // Submit answer to backend in background
                isSubmittingAnswer = true;
                try {
                    await API.attempts.submitAnswer(currentAttemptId, question.id, answerValue);
                } catch (error) {
                    console.error('Error submitting answer:', error);
                    showNotification('Ошибка при сохранении ответа', 'error');
                } finally {
                    isSubmittingAnswer = false;
                }

                // Update navigation dots only
                updateNavigation();
            });

            answersList.appendChild(label);
        });
    }

    // Update navigation
    updateNavigation();

    // Update buttons
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');

    if (prevBtn) {
        prevBtn.disabled = index === 0;
    }

    if (nextBtn) {
        if (index === testData.questions.length - 1) {
            nextBtn.textContent = 'Завершить тест';
        } else {
            nextBtn.textContent = 'Далее →';
        }
    }
}

/**
 * Update answer selection UI without full page reload
 * @param {HTMLElement} answersList - Container with answers
 * @param {number} selectedIndex - Index of selected answer
 */
function updateAnswerSelection(answersList, selectedIndex) {
    const allOptions = answersList.querySelectorAll('.answer-option');

    allOptions.forEach((option, idx) => {
        const radioCircle = option.querySelector('.radio-circle');

        if (idx === selectedIndex) {
            // Mark as selected
            option.classList.add('selected');

            // Add inner circle if not exists
            if (!radioCircle.querySelector('.radio-inner')) {
                const innerCircle = createElement('div', 'radio-inner');
                radioCircle.appendChild(innerCircle);
            }
        } else {
            // Unmark others
            option.classList.remove('selected');

            // Remove inner circle
            const innerCircle = radioCircle.querySelector('.radio-inner');
            if (innerCircle) {
                innerCircle.remove();
            }
        }
    });
}

/**
 * Update question navigation dots
 */
function updateNavigation() {
    const nav = document.getElementById('questionNav');
    nav.innerHTML = '';
    nav.className = 'question-nav';

    testData.questions.forEach((question, index) => {
        const dot = createElement('span', 'nav-dot');

        if (index === currentQuestionIndex) {
            dot.classList.add('active');
        } else if (answers[question.id]) {
            dot.classList.add('answered');
        }

        dot.addEventListener('click', (e) => {
            e.preventDefault();
            displayQuestion(index);
        });
        nav.appendChild(dot);
    });
}

/**
 * Go to previous question
 */
function previousQuestion() {
    if (currentQuestionIndex > 0) {
        displayQuestion(currentQuestionIndex - 1);
    }
}

/**
 * Go to next question or finish test
 */
async function nextQuestion() {
    const question = testData.questions[currentQuestionIndex];

    // Save text answer before moving
    if (question.question_type === 'text') {
        const textAnswer = document.getElementById('textAnswer');
        if (textAnswer && textAnswer.value.trim()) {
            answers[question.id] = textAnswer.value;

            // Submit answer if not already submitting
            if (!isSubmittingAnswer) {
                isSubmittingAnswer = true;
                try {
                    await API.attempts.submitAnswer(currentAttemptId, question.id, textAnswer.value);
                } catch (error) {
                    console.error('Error submitting answer:', error);
                    showNotification('Ошибка при сохранении ответа', 'error');
                } finally {
                    isSubmittingAnswer = false;
                }
            }
        }
    }

    if (currentQuestionIndex < testData.questions.length - 1) {
        displayQuestion(currentQuestionIndex + 1);
    } else {
        finishTest();
    }
}

/**
 * Finish the test and show results
 */
async function finishTest() {
    // Stop timer
    stopTimer();

    if (!confirm('Завершить тест? Вы не сможете изменить ответы после завершения.')) {
        // If user cancels and not last question, restart timer
        if (currentQuestionIndex < testData.questions.length - 1) {
            startTimer();
        }
        return;
    }

    try {
        await API.attempts.finish(currentAttemptId);
        showNotification('Тест завершён!', 'success');
        setTimeout(() => {
            window.location.href = `results.html?attemptId=${currentAttemptId}`;
        }, 1000);
    } catch (error) {
        console.error('Error finishing test:', error);
        showNotification('Ошибка при завершении теста: ' + error.message, 'error');
    }
}
