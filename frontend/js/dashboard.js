/**
 * Dashboard page logic
 * Fixed: XSS vulnerabilities, hardcoded user info, duplicate functions
 */

document.addEventListener('DOMContentLoaded', () => {
    requireAuth();

    // Load tests
    loadTests();

    // Load statistics
    loadStatistics();

    // Filter tabs
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            document.querySelectorAll('.filter-tab').forEach(t => {
                t.classList.remove('active');
            });
            this.classList.add('active');
            filterTests(this.textContent);
        });
    });
});

/**
 * Load statistics
 */
async function loadStatistics() {
    try {
        const tests = await API.tests.list();
        const publishedTests = tests.filter(t => t.is_published);
        const totalAttempts = tests.reduce((sum, test) => sum + (test.attempts_count || 0), 0);

        const statValues = document.querySelectorAll('.stat-value');
        if (statValues.length >= 3) {
            safeSetText(statValues[0], tests.length.toString());
            safeSetText(statValues[1], publishedTests.length.toString());
            safeSetText(statValues[2], totalAttempts.toString());
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
        showNotification('Ошибка при загрузке статистики', 'error');
    }
}

let allTests = [];

/**
 * Filter tests by status
 */
function filterTests(filterType) {
    const testsGrid = document.querySelector('.tests-grid');
    let filteredTests = allTests;

    if (filterType === 'Опубликованные') {
        filteredTests = allTests.filter(t => t.is_published);
    } else if (filterType === 'Черновики') {
        filteredTests = allTests.filter(t => !t.is_published);
    }

    if (filteredTests.length > 0) {
        testsGrid.innerHTML = '';
        filteredTests.forEach(test => {
            const testCard = createTestCard(test);
            testsGrid.appendChild(testCard);
        });
    } else {
        testsGrid.innerHTML = '';
        const emptyState = createEmptyState(
            '📚',
            'Нет тестов',
            'Тесты не найдены для этого фильтра'
        );
        testsGrid.appendChild(emptyState);
    }
}

/**
 * Load all tests
 */
async function loadTests() {
    try {
        allTests = await API.tests.list();
        const testsGrid = document.querySelector('.tests-grid');

        if (allTests && allTests.length > 0) {
            testsGrid.innerHTML = '';
            allTests.forEach(test => {
                const testCard = createTestCard(test);
                testsGrid.appendChild(testCard);
            });
        } else {
            testsGrid.innerHTML = '';
            const emptyState = createEmptyState(
                '📚',
                'Нет тестов',
                'Создайте свой первый тест, чтобы начать',
                'create-test.html',
                'Создать тест'
            );
            testsGrid.appendChild(emptyState);
        }
    } catch (error) {
        console.error('Error loading tests:', error);
        showNotification('Ошибка при загрузке тестов: ' + error.message, 'error');
    }
}

/**
 * Create empty state element
 * @param {string} icon - Icon emoji
 * @param {string} title - Title text
 * @param {string} description - Description text
 * @param {string} linkHref - Optional link href
 * @param {string} linkText - Optional link text
 * @returns {HTMLElement} Empty state element
 */
function createEmptyState(icon, title, description, linkHref = null, linkText = null) {
    const emptyState = createElement('div', 'empty-state');
    emptyState.style.gridColumn = '1 / -1';

    const iconDiv = createElement('div', 'empty-state-icon', icon);
    const titleH3 = createElement('h3', '', title);
    const descP = createElement('p', '', description);

    emptyState.appendChild(iconDiv);
    emptyState.appendChild(titleH3);
    emptyState.appendChild(descP);

    if (linkHref && linkText) {
        const link = createElement('a', 'btn-primary', linkText);
        link.href = linkHref;
        emptyState.appendChild(link);
    }

    return emptyState;
}

/**
 * Create test card element (XSS-safe)
 * @param {Object} test - Test data
 * @returns {HTMLElement} Test card element
 */
function createTestCard(test) {
    const card = createElement('div', 'test-card');

    // Title
    const title = createElement('div', 'test-title');
    safeSetText(title, test.title);

    // Meta info
    const meta = createElement('div', 'test-meta');
    const questionsSpan = createElement('span', 'test-meta-item');
    safeSetText(questionsSpan, `📝 ${test.questions_count || 0} вопросов`);
    const attemptsSpan = createElement('span', 'test-meta-item');
    safeSetText(attemptsSpan, `👥 ${test.attempts_count || 0} прохождений`);
    meta.appendChild(questionsSpan);
    meta.appendChild(attemptsSpan);

    // Footer
    const footer = createElement('div', 'test-footer');

    // Status
    const status = test.is_published ? 'published' : 'draft';
    const statusText = test.is_published ? 'Опубликован' : 'Черновик';
    const statusSpan = createElement('span', `test-status ${status}`, statusText);

    // Actions
    const actions = createElement('div', 'test-actions');

    // Statistics link
    const statsLink = createElement('a', 'icon-btn', '📊');
    statsLink.href = `statistics.html?id=${encodeURIComponent(test.id)}`;
    statsLink.title = 'Статистика';

    // Edit button
    const editBtn = createElement('button', 'icon-btn edit-btn', '✏️');
    editBtn.dataset.id = test.id;
    editBtn.title = 'Редактировать';
    editBtn.addEventListener('click', () => {
        window.location.href = `create-test.html?id=${encodeURIComponent(test.id)}`;
    });

    // Delete button
    const deleteBtn = createElement('button', 'icon-btn delete delete-btn', '🗑️');
    deleteBtn.dataset.id = test.id;
    deleteBtn.title = 'Удалить';
    deleteBtn.addEventListener('click', () => {
        if (confirm('Вы уверены, что хотите удалить этот тест?')) {
            deleteTest(test.id);
        }
    });

    actions.appendChild(statsLink);
    actions.appendChild(editBtn);
    actions.appendChild(deleteBtn);

    footer.appendChild(statusSpan);
    footer.appendChild(actions);

    // Assemble card
    card.appendChild(title);
    card.appendChild(meta);
    card.appendChild(footer);

    return card;
}

/**
 * Delete test
 * @param {string} testId - Test ID to delete
 */
async function deleteTest(testId) {
    try {
        await API.tests.delete(testId);
        showNotification('Тест успешно удален', 'success');
        loadTests();
    } catch (error) {
        console.error('Error deleting test:', error);
        showNotification('Ошибка при удалении теста: ' + error.message, 'error');
    }
}
