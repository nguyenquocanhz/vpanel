/* VPS Panel - Shared Sidebar Component (Lucide Icons) */
const SIDEBAR_HTML = `
<div class="sidebar-header">
    <div class="logo-box"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/></svg></div>
    <div><div class="logo-text text-gradient">VPS Panel</div><div class="logo-version">v1.0.0</div></div>
</div>
<nav class="sidebar-nav">
    <div class="nav-section">
        <div class="nav-section-title">Monitoring</div>
        <a href="/dashboard" class="nav-item" data-page="dashboard">
            <span class="nav-icon"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg></span>
            Overview
        </a>
    </div>
    <div class="nav-section">
        <div class="nav-section-title">Management</div>
        <a href="/partitions" class="nav-item" data-page="partitions">
            <span class="nav-icon"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0 0 18 0V5"/><path d="M3 12a9 3 0 0 0 18 0"/></svg></span>
            Disk & Partitions
        </a>
        <a href="/services" class="nav-item" data-page="services">
            <span class="nav-icon"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg></span>
            Services
        </a>
        <a href="/appstore" class="nav-item" data-page="appstore">
            <span class="nav-icon"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg></span>
            AppStore
        </a>
    </div>
    <div class="nav-section">
        <div class="nav-section-title">System</div>
        <a href="#" class="nav-item" onclick="showPowerModal && showPowerModal(); return false;" data-page="power">
            <span class="nav-icon"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v10"/><path d="M18.4 6.6a9 9 0 1 1-12.8 0"/></svg></span>
            Power Control
        </a>
        <a href="#" class="nav-item" onclick="return false;" data-page="license">
            <span class="nav-icon"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15.5 7.5 2.3 2.3a1 1 0 0 0 1.4 0l2.1-2.1a1 1 0 0 0 0-1.4L19 4"/><path d="m21 2-9.6 9.6"/><circle cx="7.5" cy="15.5" r="5.5"/></svg></span>
            License
        </a>
    </div>
</nav>
<div class="sidebar-footer">
    <div class="sidebar-user">
        <div class="sidebar-avatar" id="userAvatar">A</div>
        <div class="sidebar-user-info">
            <div class="sidebar-user-name" id="userName">Admin</div>
            <div class="sidebar-user-role">Administrator</div>
        </div>
        <button class="btn btn-icon btn-ghost" onclick="logout()" title="Logout">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/></svg>
        </button>
    </div>
</div>`;

function initSidebar() {
    const el = document.getElementById('sidebar');
    if (!el) return;
    el.innerHTML = SIDEBAR_HTML;

    // Highlight active page
    const path = window.location.pathname;
    const page = path === '/' ? 'dashboard' : path.replace('/', '');
    el.querySelectorAll('.nav-item').forEach(item => {
        if (item.dataset.page === page) item.classList.add('active');
    });

    // Load user info
    if (typeof Auth !== 'undefined' && Auth.getToken()) {
        Auth.apiFetch('/api/auth/me').then(async res => {
            if (!res) return;
            const user = await res.json();
            const avatar = document.getElementById('userAvatar');
            const name = document.getElementById('userName');
            if (avatar) avatar.textContent = (user.username || 'A')[0].toUpperCase();
            if (name) name.textContent = user.username || 'Admin';
        }).catch(() => {});
    }
}

document.addEventListener('DOMContentLoaded', initSidebar);
