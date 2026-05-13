/**
 * EMS Pro — Frontend Interactivity
 */

document.addEventListener('DOMContentLoaded', () => {
    initSidebar();
    initAuthToggles();
    initAlerts();
    initAutoCloseMessages();
});

/**
 * Sidebar Toggle Logic for Mobile
 */
function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const toggle = document.getElementById('sidebarToggle');
    
    if (toggle && sidebar) {
        toggle.addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.classList.toggle('open');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (sidebar.classList.contains('open') && !sidebar.contains(e.target)) {
                sidebar.classList.remove('open');
            }
        });
    }
}

/**
 * Password Visibility Toggle
 */
function initAuthToggles() {
    const eyeToggle = document.getElementById('eyeToggle');
    const passwordInput = document.getElementById('password');

    if (eyeToggle && passwordInput) {
        eyeToggle.addEventListener('click', () => {
            const isPassword = passwordInput.type === 'password';
            passwordInput.type = isPassword ? 'text' : 'password';
            eyeToggle.textContent = isPassword ? '🔒' : '👁';
        });
    }

    // Login button loading state
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', () => {
            const btn = document.getElementById('loginBtn');
            const text = btn.querySelector('.btn-text');
            const loader = btn.querySelector('.btn-loader');
            
            btn.disabled = true;
            text.classList.add('hidden');
            loader.classList.remove('hidden');
        });
    }
}

/**
 * Alert Management
 */
function initAlerts() {
    const closeButtons = document.querySelectorAll('.alert-close');
    closeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const alert = btn.closest('.alert');
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 300);
        });
    });
}

/**
 * Auto-close success messages after 5 seconds
 */
function initAutoCloseMessages() {
    const alerts = document.querySelectorAll('.alert-success, .alert-info');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentNode) {
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-10px)';
                setTimeout(() => alert.remove(), 300);
            }
        }, 5000);
    });
}

/**
 * Generic Modal Opener Helper
 */
window.openModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.hidden = false;
        document.body.style.overflow = 'hidden';
    }
};

window.closeModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.hidden = true;
        document.body.style.overflow = 'auto';
    }
};
