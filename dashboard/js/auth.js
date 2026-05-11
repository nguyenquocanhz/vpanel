/* VPS Panel - Auth Client */
const Auth = {
    getToken() { return localStorage.getItem('vpspanel_token'); },
    getRefresh() { return localStorage.getItem('vpspanel_refresh'); },
    setTokens(access, refresh) {
        localStorage.setItem('vpspanel_token', access);
        if (refresh) localStorage.setItem('vpspanel_refresh', refresh);
    },
    clear() { localStorage.removeItem('vpspanel_token'); localStorage.removeItem('vpspanel_refresh'); },
    isLoggedIn() { return !!this.getToken(); },
    headers() { return { 'Authorization': 'Bearer ' + this.getToken(), 'Content-Type': 'application/json' }; },
    requireAuth() {
        if (!this.isLoggedIn()) { window.location.href = '/'; return false; }
        return true;
    },
    async apiFetch(url, options = {}) {
        if (!options.headers) options.headers = {};
        options.headers['Authorization'] = 'Bearer ' + this.getToken();
        if (!options.headers['Content-Type'] && options.method && options.method !== 'GET')
            options.headers['Content-Type'] = 'application/json';
        const res = await fetch(url, options);
        if (res.status === 401) { this.clear(); window.location.href = '/'; return null; }
        return res;
    }
};
function logout() { Auth.clear(); window.location.href = '/'; }
if (!Auth.requireAuth()) window.location.href = '/';
