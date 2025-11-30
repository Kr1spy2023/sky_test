/**
 * Statistics page logic
 * Fixed: XSS vulnerabilities, inline CSS, improved error handling
 */

document.addEventListener('DOMContentLoaded', () => {
    requireAuth();

    // Get test ID from URL
    const params = new URLSearchParams(window.location.search);
    const testId = params.get('id');

    if (!testId) {
        showNotification('Тест не найден', 'error');
        window.location.href = 'dashboard.html';
        return;
    }

    loadStatistics(testId);

    // Share button
    document.getElementById('shareBtn')?.addEventListener('click', async () => {
        const shareBtn = document.getElementById('shareBtn');
        const originalText = shareBtn.textContent;

        try {
            // Disable button during operation
            shareBtn.disabled = true;
            shareBtn.textContent = 'Создание ссылки...';

            const test = await API.tests.get(testId);

            // Check if test is published
            if (!test.is_published) {
                showNotification('Тест должен быть опубликован для создания ссылки', 'warning');
                return;
            }

            // Generate proper share link
            let shareLink;
            if (test.link_token) {
                // Use token-based link (more secure)
                shareLink = `${window.location.protocol}//${window.location.host}/frontend/html/take-test.html?token=${test.link_token}`;
            } else {
                // Fallback to ID-based link
                shareLink = `${window.location.protocol}//${window.location.host}/frontend/html/take-test.html?id=${testId}`;
            }

            // Copy to clipboard
            if (navigator.clipboard) {
                await navigator.clipboard.writeText(shareLink);
                showNotification('Ссылка скопирована! ' + shareLink, 'success');
            } else {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = shareLink;
                textArea.style.position = 'fixed';
                textArea.style.left = '-9999px';
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                showNotification('Ссылка скопирована! ' + shareLink, 'success');
            }
        } catch (error) {
            console.error('Error generating share link:', error);
            showNotification('Ошибка при создании ссылки: ' + error.message, 'error');
        } finally {
            // Re-enable button
            shareBtn.disabled = false;
            shareBtn.textContent = originalText;
        }
    });
});

/**
 * Load test statistics
 * @param {string} testId - Test ID
 */
async function loadStatistics(testId) {
    try {
        // Load test info
        const test = await API.tests.get(testId);
        safeSetText(document.getElementById('statisticsTitle'), test.title);

        // Update edit button link
        const editBtn = document.querySelector('a.btn-secondary[href*="create-test"]');
        if (editBtn) {
            editBtn.href = `create-test.html?id=${encodeURIComponent(testId)}`;
        }

        // Load test stats
        const stats = await API.statistics.getTestStats(testId);
        safeSetText(document.getElementById('totalAttempts'), (stats.total_attempts || 0).toString());

        // Calculate average score as percentage
        const avgScorePercent = calculateAverageScorePercent(stats, test);
        safeSetText(document.getElementById('averageScore'), avgScorePercent + '%');
        safeSetText(document.getElementById('bestScore'), '0%'); // Not provided by API yet
        safeSetText(document.getElementById('averageTime'), '-'); // Not provided by API yet

        // Load attempts
        const attempts = await API.statistics.getAttempts(testId);
        renderAttemptsTable(attempts);
    } catch (error) {
        console.error('Error loading statistics:', error);
        showNotification('Ошибка при загрузке статистики: ' + error.message, 'error');
    }
}

/**
 * Calculate average score percentage
 * @param {Object} stats - Statistics data
 * @param {Object} test - Test data
 * @returns {number} Average score percentage
 */
function calculateAverageScorePercent(stats, test) {
    if (!stats.average_score || !test.questions || test.questions.length === 0) {
        return 0;
    }

    const maxScore = test.questions.reduce((sum, q) => sum + (q.points || 1), 0);
    return Math.round((stats.average_score / maxScore) * 100);
}

/**
 * Render attempts table (XSS-safe)
 * @param {Array} attempts - Array of attempt objects
 */
function renderAttemptsTable(attempts) {
    const tbody = document.getElementById('resultsTableBody');
    tbody.innerHTML = '';

    if (attempts && attempts.length > 0) {
        attempts.forEach((attempt) => {
            const row = createAttemptRow(attempt);
            tbody.appendChild(row);
        });
    } else {
        const emptyRow = createEmptyStateRow();
        tbody.appendChild(emptyRow);
    }
}

/**
 * Create attempt table row (XSS-safe)
 * @param {Object} attempt - Attempt data
 * @returns {HTMLElement} Table row element
 */
function createAttemptRow(attempt) {
    const row = createElement('tr');

    // User cell
    const userCell = createElement('td');
    const userContainer = createElement('div');
    userContainer.style.cssText = 'display: flex; align-items: center; gap: 12px;';

    const avatar = createElement('div', 'user-avatar-small');
    safeSetText(avatar, getInitials(attempt.user_name));

    const userInfo = createElement('div');
    const userName = createElement('div', 'user-name-cell');
    safeSetText(userName, attempt.user_name);
    userInfo.appendChild(userName);

    userContainer.appendChild(avatar);
    userContainer.appendChild(userInfo);
    userCell.appendChild(userContainer);

    // Score percentage cell
    const scorePercent = calculateScorePercentage(attempt.score, attempt.max_score);
    const scoreGrade = getScoreGrade(scorePercent);

    const scorePercentCell = createElement('td');
    const scoreSpan = createElement('span', `score-badge score-${scoreGrade}`, `${scorePercent}%`);
    scorePercentCell.appendChild(scoreSpan);

    // Score points cell
    const pointsCell = createElement('td');
    safeSetText(pointsCell, `${attempt.score || 0} / ${attempt.max_score || 0} баллов`);

    // Time cell (placeholder)
    const timeCell = createElement('td', '', '-');

    // Date cell
    const dateCell = createElement('td');
    if (attempt.started_at) {
        const date = new Date(attempt.started_at);
        const dateDiv = createElement('div');
        safeSetText(dateDiv, date.toLocaleDateString('ru-RU'));

        const timeDiv = createElement('div', 'time-text');
        safeSetText(timeDiv, date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }));

        dateCell.appendChild(dateDiv);
        dateCell.appendChild(timeDiv);
    } else {
        safeSetText(dateCell, '-');
    }

    // Actions cell
    const actionsCell = createElement('td');
    if (attempt.finished_at) {
        const link = createElement('a', 'btn-small btn-primary', 'Подробнее');
        link.href = `results.html?attemptId=${encodeURIComponent(attempt.id)}`;
        actionsCell.appendChild(link);
    } else {
        const statusSpan = createElement('span', 'status-in-progress', 'В процессе');
        actionsCell.appendChild(statusSpan);
    }

    // Assemble row
    row.appendChild(userCell);
    row.appendChild(scorePercentCell);
    row.appendChild(pointsCell);
    row.appendChild(timeCell);
    row.appendChild(dateCell);
    row.appendChild(actionsCell);

    return row;
}

/**
 * Create empty state table row
 * @returns {HTMLElement} Table row element
 */
function createEmptyStateRow() {
    const row = createElement('tr');
    const cell = createElement('td');
    cell.colSpan = 6;
    cell.style.cssText = 'text-align: center; padding: 40px;';

    const icon = createElement('div', 'empty-state-icon', '📊');
    const title = createElement('div', 'empty-state-title', 'Пока нет результатов');
    const desc = createElement('div', 'empty-state-desc', 'Когда студенты начнут проходить тест, здесь появится статистика');

    cell.appendChild(icon);
    cell.appendChild(title);
    cell.appendChild(desc);
    row.appendChild(cell);

    return row;
}
