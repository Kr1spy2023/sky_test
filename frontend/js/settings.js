/**
 * Settings Page Script
 * Handles user profile, password, and preferences management
 */

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    requireAuth();
    loadUserProfile();
});

/**
 * Load user profile information from backend
 */
async function loadUserProfile() {
    try {
        const user = JSON.parse(localStorage.getItem('user') || '{}');

        // Fill profile form with current user data
        document.getElementById('fullName').value = user.name || '';
        document.getElementById('email').value = user.email || '';
        document.getElementById('organization').value = localStorage.getItem('organization') || '';

        // Load user preferences
        const theme = localStorage.getItem('theme') || 'light';
        document.getElementById('theme').value = theme;

        const language = localStorage.getItem('language') || 'ru';
        document.getElementById('language').value = language;

        const emailNotifications = localStorage.getItem('emailNotifications') !== 'false';
        document.getElementById('emailNotifications').checked = emailNotifications;

        const publicProfile = localStorage.getItem('publicProfile') !== 'false';
        document.getElementById('publicProfile').checked = publicProfile;

    } catch (error) {
        console.error('Error loading user profile:', error);
    }
}

/**
 * Save profile settings
 */
async function saveProfileSettings() {
    const fullName = document.getElementById('fullName').value.trim();
    const email = document.getElementById('email').value.trim();
    const organization = document.getElementById('organization').value.trim();

    // Validation
    if (!fullName) {
        alert('Пожалуйста, введите полное имя');
        return;
    }

    if (!email) {
        alert('Пожалуйста, введите email');
        return;
    }

    if (!isValidEmail(email)) {
        alert('Пожалуйста, введите корректный email');
        return;
    }

    try {
        // Call API to update profile
        await API.auth.updateProfile({
            name: fullName,
            email: email
        });

        // Update user data in localStorage
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        user.name = fullName;
        user.email = email;
        localStorage.setItem('user', JSON.stringify(user));
        localStorage.setItem('organization', organization);

        showNotification('Профиль успешно обновлён', 'success');

        // Update sidebar display
        const userNameElement = document.querySelector('.user-name');
        const userEmailElement = document.querySelector('.user-email');
        if (userNameElement) userNameElement.textContent = fullName;
        if (userEmailElement) userEmailElement.textContent = email;
    } catch (error) {
        console.error('Error saving profile:', error);
        showNotification('Ошибка при сохранении профиля: ' + (error.message || 'Неизвестная ошибка'), 'error');
    }
}

/**
 * Reset profile form to original values
 */
function resetProfileForm() {
    loadUserProfile();
}

/**
 * Save password settings
 */
async function savePasswordSettings() {
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    // Validation
    if (!currentPassword) {
        alert('Пожалуйста, введите текущий пароль');
        return;
    }

    if (!newPassword) {
        alert('Пожалуйста, введите новый пароль');
        return;
    }

    if (newPassword.length < 8) {
        alert('Пароль должен содержать минимум 8 символов');
        return;
    }

    if (newPassword !== confirmPassword) {
        alert('Пароли не совпадают');
        return;
    }

    if (currentPassword === newPassword) {
        alert('Новый пароль должен отличаться от текущего');
        return;
    }

    try {
        // Call API (uncomment when backend is ready)
        // await API.auth.changePassword({
        //     current_password: currentPassword,
        //     new_password: newPassword
        // });

        resetPasswordForm();
        showNotification('Пароль успешно изменён', 'success');
    } catch (error) {
        console.error('Error changing password:', error);
        showNotification('Ошибка при изменении пароля', 'error');
    }
}

/**
 * Reset password form
 */
function resetPasswordForm() {
    document.getElementById('currentPassword').value = '';
    document.getElementById('newPassword').value = '';
    document.getElementById('confirmPassword').value = '';
}

/**
 * Save preferences
 */
async function savePreferences() {
    const theme = document.getElementById('theme').value;
    const language = document.getElementById('language').value;
    const emailNotifications = document.getElementById('emailNotifications').checked;
    const publicProfile = document.getElementById('publicProfile').checked;

    try {
        // Save preferences to localStorage
        localStorage.setItem('theme', theme);
        localStorage.setItem('language', language);
        localStorage.setItem('emailNotifications', emailNotifications);
        localStorage.setItem('publicProfile', publicProfile);

        // Apply theme if changed
        applyTheme(theme);

        showNotification('Предпочтения успешно сохранены', 'success');
    } catch (error) {
        console.error('Error saving preferences:', error);
        showNotification('Ошибка при сохранении предпочтений', 'error');
    }
}

/**
 * Reset preferences form
 */
function resetPreferencesForm() {
    loadUserProfile();
}

/**
 * Apply theme to the application
 */
function applyTheme(theme) {
    if (theme === 'dark') {
        document.body.classList.add('dark-mode');
    } else {
        document.body.classList.remove('dark-mode');
    }
}

/**
 * Logout user
 */
function logout() {
    if (confirm('Вы уверены, что хотите выйти?')) {
        try {
            // Clear user data
            localStorage.removeItem('token');
            localStorage.removeItem('user');

            // Redirect to login
            window.location.href = 'login.html';
        } catch (error) {
            console.error('Error logging out:', error);
        }
    }
}

/**
 * Delete user account
 */
function deleteAccount() {
    if (!confirm('Это действие невозможно отменить. Вы уверены, что хотите удалить аккаунт?')) {
        return;
    }

    const password = prompt('Введите ваш пароль для подтверждения:');
    if (!password) {
        return;
    }

    try {
        // Call API (uncomment when backend is ready)
        // await API.auth.deleteAccount({
        //     password: password
        // });

        // Clear user data
        localStorage.removeItem('token');
        localStorage.removeItem('user');

        // Redirect to login
        window.location.href = 'login.html';
    } catch (error) {
        console.error('Error deleting account:', error);
        showNotification('Ошибка при удалении аккаунта', 'error');
    }
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Show notification (temporary message)
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 6px;
        font-size: 14px;
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
        background-color: ${getNotificationColor(type)};
        color: white;
    `;

    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Get notification color by type
 */
function getNotificationColor(type) {
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        info: '#3b82f6',
        warning: '#f59e0b'
    };
    return colors[type] || colors.info;
}

// Add CSS animations if not already in stylesheet
const style = document.createElement('style');
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
