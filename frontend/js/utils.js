/**
 * Utility functions and constants
 * Centralized common functions used across the application
 */

// ============================================
// CONSTANTS
// ============================================

const SCORE_GRADES = {
    EXCELLENT: 80,
    GOOD: 60,
    AVERAGE: 0
};

const API_CONFIG = {
    BASE_URL: window.location.hostname === 'localhost'
        ? 'http://localhost:8000/api'
        : '/api',
    TIMEOUT: 30000
};

// ============================================
// VALIDATION FUNCTIONS
// ============================================

/**
 * Validate email format
 * @param {string} email - Email address to validate
 * @returns {boolean} True if valid
 */
function isValidEmail(email) {
    if (!email || typeof email !== 'string') return false;
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailPattern.test(email.trim());
}

/**
 * Validate password strength
 * @param {string} password - Password to validate
 * @returns {boolean} True if valid (minimum 8 characters)
 */
function validatePassword(password) {
    return password && password.length >= 8;
}

/**
 * Validate name
 * @param {string} name - Name to validate
 * @returns {boolean} True if valid (minimum 2 characters)
 */
function validateName(name) {
    return name && name.trim().length >= 2;
}

// ============================================
// NOTIFICATION SYSTEM
// ============================================

/**
 * Show notification to user
 * @param {string} message - Message to display
 * @param {string} type - Type: 'success', 'error', 'warning', 'info'
 */
function showNotification(message, type = 'info') {
    // Remove existing notification if any
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 24px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        z-index: 10000;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        animation: slideIn 0.3s ease;
        max-width: 400px;
    `;

    // Set colors based on type
    switch(type) {
        case 'success':
            notification.style.backgroundColor = '#4caf50';
            notification.style.color = 'white';
            break;
        case 'error':
            notification.style.backgroundColor = '#f44336';
            notification.style.color = 'white';
            break;
        case 'warning':
            notification.style.backgroundColor = '#ff9800';
            notification.style.color = 'white';
            break;
        default: // info
            notification.style.backgroundColor = '#2196f3';
            notification.style.color = 'white';
    }

    // Add animation styles if not already present
    if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(400px);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }

    // Add to document
    document.body.appendChild(notification);

    // Auto-remove after 4 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 4000);
}

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Get user initials from name
 * @param {string} name - Full name
 * @returns {string} Initials (e.g., "ИИ")
 */
function getInitials(name) {
    if (!name) return 'U';
    const parts = name.trim().split(' ');
    if (parts.length >= 2) {
        return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
}

/**
 * Format score as percentage
 * @param {number} score - Current score
 * @param {number} maxScore - Maximum possible score
 * @returns {number} Percentage (0-100)
 */
function calculateScorePercentage(score, maxScore) {
    if (!maxScore || maxScore === 0) return 0;
    return Math.round((score / maxScore) * 100);
}

/**
 * Get score grade based on percentage
 * @param {number} percentage - Score percentage (0-100)
 * @returns {string} Grade: 'excellent', 'good', 'average'
 */
function getScoreGrade(percentage) {
    if (percentage >= SCORE_GRADES.EXCELLENT) return 'excellent';
    if (percentage >= SCORE_GRADES.GOOD) return 'good';
    return 'average';
}

/**
 * Safely set text content (prevents XSS)
 * @param {HTMLElement} element - DOM element
 * @param {string} text - Text to set
 */
function safeSetText(element, text) {
    if (element) {
        element.textContent = text || '';
    }
}

/**
 * Create element with class and text
 * @param {string} tag - HTML tag name
 * @param {string} className - CSS class name
 * @param {string} text - Text content
 * @returns {HTMLElement} Created element
 */
function createElement(tag, className = '', text = '') {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text) element.textContent = text;
    return element;
}

/**
 * Debounce function calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export for use in other modules (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        SCORE_GRADES,
        API_CONFIG,
        isValidEmail,
        validatePassword,
        validateName,
        showNotification,
        getInitials,
        calculateScorePercentage,
        getScoreGrade,
        safeSetText,
        createElement,
        debounce
    };
}
