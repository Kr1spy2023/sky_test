/**
 * Results page logic
 * Fixed: XSS vulnerabilities, inline CSS, improved UX
 */

document.addEventListener('DOMContentLoaded', () => {
    requireAuth();

    // Get attempt ID from URL
    const params = new URLSearchParams(window.location.search);
    const attemptId = params.get('attemptId');

    if (!attemptId) {
        showNotification('Результаты не найдены', 'error');
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 2000);
        return;
    }

    loadResults(attemptId);
});

/**
 * Load and display test results
 * @param {string} attemptId - Attempt ID
 */
async function loadResults(attemptId) {
    try {
        const results = await API.attempts.getResults(attemptId);

        // Calculate stats
        const totalQuestions = results.answers ? results.answers.length : 0;
        let correctCount = 0;

        if (results.answers) {
            correctCount = results.answers.filter(a => a.is_correct).length;
        }

        const incorrectCount = totalQuestions - correctCount;
        const scorePercent = totalQuestions > 0 ? Math.round((correctCount / totalQuestions) * 100) : 0;

        // Update main stats (XSS-safe)
        safeSetText(document.getElementById('scoreDisplay'), scorePercent + '%');
        safeSetText(document.getElementById('correctCount'), correctCount.toString());
        safeSetText(document.getElementById('incorrectCount'), incorrectCount.toString());
        safeSetText(document.getElementById('totalCount'), totalQuestions.toString());
        safeSetText(document.getElementById('testName'), results.test_title);

        // Format date
        const date = new Date(results.started_at);
        const dateStr = date.toLocaleDateString('ru-RU', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
        });

        safeSetText(document.getElementById('resultDate'), `📅 ${dateStr}`);
        safeSetText(document.getElementById('resultTime'), `⏱️ Набрано баллов: ${results.score || 0} из ${results.max_score || 0}`);

        // Display detailed results
        const detailedResults = document.getElementById('detailedResults');
        detailedResults.innerHTML = '';

        if (results.answers && results.answers.length > 0) {
            results.answers.forEach((answer, index) => {
                const resultCard = createResultCard(answer, index);
                detailedResults.appendChild(resultCard);
            });
        } else {
            const emptyState = createElement('p', 'empty-results');
            emptyState.style.cssText = 'text-align: center; color: #666; padding: 40px;';
            safeSetText(emptyState, 'Нет данных об ответах');
            detailedResults.appendChild(emptyState);
        }
    } catch (error) {
        console.error('Error loading results:', error);
        showNotification('Ошибка при загрузке результатов: ' + error.message, 'error');
    }
}

/**
 * Create result card element (XSS-safe, no inline CSS)
 * @param {Object} answer - Answer data
 * @param {number} index - Question index
 * @returns {HTMLElement} Result card element
 */
function createResultCard(answer, index) {
    const isCorrect = answer.is_correct;
    const badge = isCorrect ? '✓ Правильно' : '✗ Неправильно';

    // Main container
    const resultDiv = createElement('div', 'question-result');
    resultDiv.classList.add(isCorrect ? 'correct' : 'incorrect');

    // Header with question number and badge
    const header = createElement('div', 'result-header');

    const questionNum = createElement('span', 'question-number');
    safeSetText(questionNum, `Вопрос ${index + 1}`);

    const badgeSpan = createElement('span', `result-badge ${isCorrect ? 'badge-correct' : 'badge-incorrect'}`);
    safeSetText(badgeSpan, badge);

    header.appendChild(questionNum);
    header.appendChild(badgeSpan);

    // Question text
    const questionText = createElement('div', 'question-text');
    safeSetText(questionText, answer.question_text);

    // Answers section
    const answersSection = createElement('div', 'answers-section');

    // User answer
    const userAnswerP = createElement('p', 'answer-item');
    const userLabel = createElement('strong', '', 'Ваш ответ: ');
    const userValue = createElement('span', isCorrect ? 'answer-correct' : 'answer-incorrect');
    safeSetText(userValue, answer.user_answer);
    userAnswerP.appendChild(userLabel);
    userAnswerP.appendChild(userValue);
    answersSection.appendChild(userAnswerP);

    // Correct answer (only if incorrect)
    if (!isCorrect) {
        const correctAnswerP = createElement('p', 'answer-item');
        const correctLabel = createElement('strong', '', 'Правильный ответ: ');
        const correctValue = createElement('span', 'answer-correct');
        safeSetText(correctValue, answer.correct_answer);
        correctAnswerP.appendChild(correctLabel);
        correctAnswerP.appendChild(correctValue);
        answersSection.appendChild(correctAnswerP);
    }

    // Points earned
    const pointsDiv = createElement('div', 'points-info');
    safeSetText(pointsDiv, `Баллы: ${answer.points_earned} из ${answer.max_points}`);

    // Assemble card
    resultDiv.appendChild(header);
    resultDiv.appendChild(questionText);
    resultDiv.appendChild(answersSection);
    resultDiv.appendChild(pointsDiv);

    return resultDiv;
}
