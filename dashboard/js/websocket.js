/* VPS Panel - WebSocket Manager */
const WS = {
    socket: null, reconnectTimer: null, reconnectDelay: 2000, maxDelay: 30000, callbacks: [],
    connect() {
        const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
        const url = `${proto}//${location.host}/ws/monitor?token=${Auth.getToken()}`;
        try {
            this.socket = new WebSocket(url);
            this.socket.onopen = () => {
                this.reconnectDelay = 2000;
                this.updateStatus(true);
                console.log('[WS] Connected');
            };
            this.socket.onmessage = (e) => {
                try {
                    const data = JSON.parse(e.data);
                    if (data.type === 'pong') return;
                    this.callbacks.forEach(cb => cb(data));
                } catch(err) { console.warn('[WS] Parse error', err); }
            };
            this.socket.onclose = (e) => {
                this.updateStatus(false);
                if (e.code !== 4001) this.scheduleReconnect();
            };
            this.socket.onerror = () => { this.updateStatus(false); };
        } catch(e) { console.error('[WS] Error', e); this.scheduleReconnect(); }
    },
    scheduleReconnect() {
        if (this.reconnectTimer) return;
        console.log(`[WS] Reconnecting in ${this.reconnectDelay/1000}s...`);
        this.reconnectTimer = setTimeout(() => {
            this.reconnectTimer = null;
            this.reconnectDelay = Math.min(this.reconnectDelay * 1.5, this.maxDelay);
            this.connect();
        }, this.reconnectDelay);
    },
    updateStatus(connected) {
        const dot = document.getElementById('wsIndicator');
        const text = document.getElementById('wsStatus');
        if (dot) dot.classList.toggle('connected', connected);
        if (text) text.textContent = connected ? 'Live' : 'Disconnected';
    },
    onData(callback) { this.callbacks.push(callback); },
    send(msg) { if (this.socket && this.socket.readyState === 1) this.socket.send(msg); }
};
