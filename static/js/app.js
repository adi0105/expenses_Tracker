/* Main Application JavaScript */

/**
 * Utility function to format currency
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

/**
 * Utility function to format date
 */
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

/**
 * Utility to toggle form visibility
 */
function toggleForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.classList.toggle('hidden');
        if (!form.classList.contains('hidden')) {
            form.scrollIntoView({ behavior: 'smooth' });
        }
    }
}

/**
 * Show notification message
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    // Make notification accessible to screen readers
    notification.setAttribute('role', 'status');
    notification.setAttribute('aria-live', 'polite');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 9999;
        animation: slideInRight 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    `;

    if (type === 'success') {
        notification.style.background = '#48bb78';
    } else if (type === 'error') {
        notification.style.background = '#f56565';
    } else if (type === 'warning') {
        notification.style.background = '#ed8936';
    } else {
        notification.style.background = '#4299e1';
    }

    document.body.appendChild(notification);

    // Update live region for assistive tech
    let live = document.getElementById('app-live-region');
    if (!live) {
        live = document.createElement('div');
        live.id = 'app-live-region';
        live.style.position = 'absolute';
        live.style.left = '-9999px';
        live.style.width = '1px';
        live.style.height = '1px';
        live.setAttribute('aria-live', 'polite');
        live.setAttribute('aria-atomic', 'true');
        document.body.appendChild(live);
    }
    live.textContent = message;

    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Check authentication status
 */
async function checkAuth() {
    try {
        const response = await fetch('/api/auth/check-session');
        const data = await response.json();

        if (!data.authenticated) {
            window.location.href = '/api/auth/login';
            return false;
        }
        return true;
    } catch (error) {
        console.error('Auth check error:', error);
        window.location.href = '/api/auth/login';
        return false;
    }
}

/**
 * Logout user
 */
async function logout() {
    try {
        const response = await fetch('/api/auth/logout', {
            method: 'POST'
        });

        if (response.ok) {
            window.location.href = '/api/auth/login';
        }
    } catch (error) {
        console.error('Logout error:', error);
        showNotification('Logout failed', 'error');
    }
}

/**
 * Set date input to today
 */
function setDateToToday(inputId) {
    const today = new Date().toISOString().split('T')[0];
    const input = document.getElementById(inputId);
    if (input) {
        input.value = today;
    }
}

/**
 * Create month select options
 */
function populateMonthSelect() {
    const select = document.getElementById('monthSelect');
    const today = new Date();
    const currentMonth = today.getMonth() + 1;
    const currentYear = today.getFullYear();

    const months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ];

    // Add last 12 months
    for (let i = 0; i < 12; i++) {
        let month = currentMonth - i;
        let year = currentYear;

        if (month <= 0) {
            month += 12;
            year -= 1;
        }

        const option = document.createElement('option');
        option.value = JSON.stringify({ month, year });
        option.textContent = `${months[month - 1]} ${year}`;

        if (i === 0) {
            option.selected = true;
        }

        select.appendChild(option);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    const isAuthenticated = await checkAuth();

    if (isAuthenticated) {
        populateMonthSelect();
        setDateToToday('expenseDate');
        setDateToToday('incomeDate');

        // Add logout button listener
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', logout);
        }
        // Setup sidebar toggle for accessibility/responsiveness
        if (typeof setupSidebarToggle === 'function') setupSidebarToggle();
    }
});

// Add slide animations styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100px);
        }
    }
`;
document.head.appendChild(style);

/**
 * Sidebar toggle for responsive layout and accessibility
 */
function setupSidebarToggle() {
    const toggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('mainNav');
    if (!toggle || !sidebar) return;

    // Initialize state from localStorage
    const stored = localStorage.getItem('sidebar-collapsed');
    const collapsed = stored === '1';
    if (collapsed) {
        sidebar.classList.add('collapsed');
        document.body.classList.add('sidebar-collapsed');
        toggle.setAttribute('aria-expanded', 'false');
    } else {
        toggle.setAttribute('aria-expanded', 'true');
    }

    function setState(isCollapsed) {
        if (isCollapsed) {
            sidebar.classList.add('collapsed');
            document.body.classList.add('sidebar-collapsed');
            toggle.setAttribute('aria-expanded', 'false');
            localStorage.setItem('sidebar-collapsed', '1');
        } else {
            sidebar.classList.remove('collapsed');
            document.body.classList.remove('sidebar-collapsed');
            toggle.setAttribute('aria-expanded', 'true');
            localStorage.setItem('sidebar-collapsed', '0');
        }
    }

    toggle.addEventListener('click', () => {
        const isCollapsed = sidebar.classList.toggle('collapsed');
        document.body.classList.toggle('sidebar-collapsed', isCollapsed);
        toggle.setAttribute('aria-expanded', isCollapsed ? 'false' : 'true');
        localStorage.setItem('sidebar-collapsed', isCollapsed ? '1' : '0');
    });

    // Support keyboard activation (Enter / Space)
    toggle.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            toggle.click();
        }
    });
}
