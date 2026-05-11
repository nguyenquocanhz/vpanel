/* VPS Panel - Main App Logic */
// Toast notifications
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const icons = { success: '✅', error: '❌', warning: '⚠️' };
    toast.innerHTML = `<span>${icons[type] || '📌'}</span><span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; toast.style.transform = 'translateX(100%)'; setTimeout(() => toast.remove(), 300); }, 4000);
}

// Power Modal
function showPowerModal() { document.getElementById('powerModal')?.classList.add('active'); }
function closePowerModal() { document.getElementById('powerModal')?.classList.remove('active'); }

async function serverAction(action) {
    if (!confirm(`Are you sure you want to ${action} the server?`)) return;
    closePowerModal();
    try {
        const res = await Auth.apiFetch(`/api/manager/power/${action}`, {
            method: 'POST',
            body: JSON.stringify({ confirm: true, delay_seconds: 60 })
        });
        if (!res) return;
        const data = await res.json();
        showToast(data.message || `Server ${action} initiated`, data.success ? 'success' : 'error');
    } catch(e) { showToast('Failed: ' + e.message, 'error'); }
}

// Sidebar toggle (mobile)
function toggleSidebar() { document.getElementById('sidebar')?.classList.toggle('open'); }

// Close modal on overlay click
document.getElementById('powerModal')?.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay')) closePowerModal();
});

// ── Initialize ──
document.addEventListener('DOMContentLoaded', () => {
    // Load initial data
    loadOverview();
    loadProcesses();

    // Init charts
    initCharts();

    // Connect WebSocket
    WS.onData(updateMetrics);
    WS.connect();

    // Periodic refresh for processes (every 10s)
    setInterval(loadProcesses, 10000);

    // Load user info
    Auth.apiFetch('/api/auth/me').then(async res => {
        if (!res) return;
        const user = await res.json();
        const avatar = document.getElementById('userAvatar');
        const name = document.getElementById('userName');
        if (avatar) avatar.textContent = (user.username || 'A')[0].toUpperCase();
        if (name) name.textContent = user.username || 'Admin';
    }).catch(() => {});

    // Responsive sidebar
    const mq = window.matchMedia('(max-width: 768px)');
    function handleResize(e) { document.getElementById('menuBtn')?.classList.toggle('hidden', !e.matches); }
    mq.addEventListener('change', handleResize);
    handleResize(mq);
});
