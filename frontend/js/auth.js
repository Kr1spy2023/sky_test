/**
 * Authentication handling
 */

// Check if user is logged in
function isLoggedIn() {
    return !!localStorage.getItem('token');
}

// Redirect to login if not authenticated
function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = 'login.html';
    }
}

// Get current user info
function getCurrentUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
}

// Save token and user info
function setAuth(token, user) {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
}

// Clear auth data
function clearAuth() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
}

// Validate email format
function validateEmail(email) {
    const emailPattern = /^[\w\.-]+@[\w\.-]+\.\w+$/;
    return emailPattern.test(email);
}

// Validate password
function validatePassword(password) {
    return password && password.length >= 8;
}

// Logout
function logout() {
    clearAuth();
    window.location.href = 'login.html';
}

// Handle login form
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;
            const submitBtn = loginForm.querySelector('button[type="submit"]');

            // Validate email
            if (!validateEmail(email)) {
                showNotification('Введите корректный email', 'error');
                return;
            }

            // Show loading
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Вход...';

            try {
                const data = await API.auth.login(email, password);
                setAuth(data.token, data.user);
                window.location.href = 'dashboard.html';
            } catch (error) {
                showNotification('Ошибка входа: ' + error.message, 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }

    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const name = document.getElementById('name').value.trim();
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm-password').value;
            const submitBtn = registerForm.querySelector('button[type="submit"]');

            // Validate name
            if (!name || name.length < 2) {
                showNotification('Введите корректное имя (минимум 2 символа)', 'error');
                return;
            }

            // Validate email
            if (!validateEmail(email)) {
                showNotification('Введите корректный email', 'error');
                return;
            }

            // Validate password
            if (!validatePassword(password)) {
                showNotification('Пароль должен быть минимум 8 символов', 'error');
                return;
            }

            if (password !== confirmPassword) {
                showNotification('Пароли не совпадают', 'error');
                return;
            }

            // Show loading
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Регистрация...';

            try {
                const data = await API.auth.register(name, email, password);
                setAuth(data.token, data.user);
                window.location.href = 'dashboard.html';
            } catch (error) {
                showNotification('Ошибка регистрации: ' + error.message, 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }
});
