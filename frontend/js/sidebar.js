/**
 * Sidebar management
 * Handles user info display and active navigation states
 */

// ============================================
// USER INFO MANAGEMENT
// ============================================

/**
 * Update sidebar user information
 * Fetches current user and updates avatar, name, and email
 */
function updateSidebarUserInfo() {
    const user = getCurrentUser();

    if (!user) {
        // If no user, redirect to login
        window.location.href = 'login.html';
        return;
    }

    // Update user avatar
    const userAvatar = document.querySelector('.user-avatar');
    if (userAvatar) {
        safeSetText(userAvatar, getInitials(user.name));
    }

    // Update user name
    const userName = document.querySelector('.user-name');
    if (userName) {
        safeSetText(userName, user.name);
    }

    // Update user email
    const userEmail = document.querySelector('.user-email');
    if (userEmail) {
        safeSetText(userEmail, user.email);
    }
}

// ============================================
// NAVIGATION MANAGEMENT
// ============================================

/**
 * Set active navigation item based on current page
 */
function setActiveNavItem() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';

    // Map of page names to nav link hrefs
    const pageMap = {
        'dashboard.html': 'dashboard.html',
        'create-test.html': 'create-test.html',
        'settings.html': 'settings.html',
        'statistics.html': 'statistics.html',
        'results.html': 'results.html'
    };

    // Remove all active classes
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.classList.remove('active');
    });

    // Add active class to current page link
    const activePage = pageMap[currentPage];
    if (activePage) {
        const activeLink = document.querySelector(`.nav-link[href="${activePage}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
    }
}

// ============================================
// INITIALIZATION
// ============================================

/**
 * Initialize sidebar functionality
 * Call this when DOM is ready on pages with sidebar
 */
function initSidebar() {
    updateSidebarUserInfo();
    setActiveNavItem();
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSidebar);
} else {
    // DOM already loaded
    initSidebar();
}

// Export for use in other modules (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        updateSidebarUserInfo,
        setActiveNavItem,
        initSidebar
    };
}
