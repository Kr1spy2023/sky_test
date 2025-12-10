// ============================================
// INTERACTIONS.JS - JavaScript для интерактивности
// ============================================

// Функция для копирования ссылки на тест
function copyTestLink(linkToken) {
    const url = window.location.origin + '/take-test/' + linkToken;
    navigator.clipboard.writeText(url).then(() => {
        alert('Ссылка скопирована в буфер обмена!');
    }).catch(err => {
        console.error('Ошибка копирования:', err);
    });
}

// Функция подтверждения удаления
function confirmDelete(message) {
    return confirm(message || 'Вы уверены, что хотите удалить?');
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Автоматическое скрытие flash сообщений через 5 секунд
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(flash => {
        setTimeout(() => {
            flash.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => flash.remove(), 300);
        }, 5000);
    });
});
