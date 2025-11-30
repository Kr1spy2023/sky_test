/**
 * API Client for Sky Test Backend
 * This file handles all communication with the Flask backend
 */

const API_BASE_URL = 'http://localhost:8000/api';

/**
 * Fetch with error handling
 * @param {string} endpoint - API endpoint
 * @param {object} options - Fetch options
 * @returns {Promise} Response data
 */
async function apiCall(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const token = localStorage.getItem('token');

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(url, {
            ...options,
            headers,
        });

        // Check for 401 Unauthorized - token expired
        if (response.status === 401) {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = '../html/login.html';
            throw new Error('Сессия истекла. Войдите снова');
        }

        const result = await response.json();

        if (!response.ok || !result.success) {
            throw new Error(result.error || 'API Error');
        }

        return result.data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * Authentication API
 */
const auth = {
    login: async (email, password) => {
        return apiCall('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });
    },

    register: async (name, email, password) => {
        return apiCall('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ name, email, password }),
        });
    },

    logout: () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    },

    getProfile: async () => {
        return apiCall('/auth/profile');
    },

    updateProfile: async (data) => {
        return apiCall('/auth/profile', {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },
};

/**
 * Tests API
 */
const tests = {
    list: async (skip = 0, limit = 20) => {
        return apiCall(`/tests?skip=${skip}&limit=${limit}`);
    },

    get: async (testId) => {
        return apiCall(`/tests/${testId}`);
    },

    create: async (data) => {
        return apiCall('/tests', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    update: async (testId, data) => {
        return apiCall(`/tests/${testId}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },

    delete: async (testId) => {
        return apiCall(`/tests/${testId}`, {
            method: 'DELETE',
        });
    },

    publish: async (testId) => {
        return apiCall(`/tests/${testId}/publish`, {
            method: 'POST',
        });
    },

    getByLink: async (linkToken) => {
        return apiCall(`/tests/link/${linkToken}`);
    },
};

/**
 * Questions API
 */
const questions = {
    create: async (testId, data) => {
        return apiCall(`/tests/${testId}/questions`, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    update: async (testId, questionId, data) => {
        return apiCall(`/tests/${testId}/questions/${questionId}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },

    delete: async (testId, questionId) => {
        return apiCall(`/tests/${testId}/questions/${questionId}`, {
            method: 'DELETE',
        });
    },
};

/**
 * Attempts API (Test Taking)
 */
const attempts = {
    start: async (testId) => {
        return apiCall(`/tests/${testId}/attempts`, {
            method: 'POST',
        });
    },

    submitAnswer: async (attemptId, questionId, answer) => {
        return apiCall(`/attempts/${attemptId}/answers`, {
            method: 'POST',
            body: JSON.stringify({ question_id: questionId, answer }),
        });
    },

    finish: async (attemptId) => {
        return apiCall(`/attempts/${attemptId}/finish`, {
            method: 'POST',
        });
    },

    getResults: async (attemptId) => {
        return apiCall(`/attempts/${attemptId}/results`);
    },
};

/**
 * Statistics API
 */
const statistics = {
    getTestStats: async (testId) => {
        return apiCall(`/tests/${testId}/statistics`);
    },

    getAttempts: async (testId, skip = 0, limit = 20) => {
        return apiCall(`/tests/${testId}/attempts?skip=${skip}&limit=${limit}`);
    },

    getUserStats: async () => {
        return apiCall('/statistics/user');
    },
};

// Export API client
window.API = {
    auth,
    tests,
    questions,
    attempts,
    statistics,
};
