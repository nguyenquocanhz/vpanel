/* VPS Panel - Monitor Data Handler */
function updateMetrics(data) {
    // CPU
    if (data.cpu) {
        const cpu = data.cpu.overall || 0;
        setText('cpuValue', cpu.toFixed(1) + '%');
        setBar('cpuBar', cpu); setBarColor('cpuBar', cpu);
    }
    // Temperature
    if (data.temperature) {
        const temp = data.temperature.cpu || 0;
        const status = data.temperature.status || 'unknown';
        setText('tempValue', temp > 0 ? temp.toFixed(1) + '°C' : 'N/A');
        setBar('tempBar', Math.min(temp, 100));
        const badge = document.getElementById('tempBadge');
        if (badge) {
            badge.textContent = status.charAt(0).toUpperCase() + status.slice(1);
            badge.className = 'badge badge-' + (status === 'normal' ? 'green' : status === 'warning' ? 'amber' : status === 'critical' ? 'red' : 'cyan');
        }
    }
    // RAM
    if (data.ram) {
        setText('ramValue', data.ram.percent.toFixed(1) + '%');
        setText('ramSub', data.ram.used_gb + ' / ' + data.ram.total_gb + ' GB');
        setBar('ramBar', data.ram.percent); setBarColor('ramBar', data.ram.percent);
    }
    // Disk (primary)
    if (data.disk && data.disk.length > 0) {
        const d = data.disk[0];
        setText('diskValue', d.percent.toFixed(1) + '%');
        setText('diskSub', d.used_gb + ' / ' + d.total_gb + ' GB');
        setBar('diskBar', d.percent); setBarColor('diskBar', d.percent);
        renderDiskList(data.disk);
    }
    // Push to charts
    pushChartData(data);
}

function renderDiskList(disks) {
    const el = document.getElementById('diskList');
    if (!el) return;
    el.innerHTML = disks.map(d => `
        <div class="disk-item">
            <span class="disk-icon">💿</span>
            <div class="disk-info">
                <div class="disk-name">${d.mountpoint}</div>
                <div class="disk-detail">${d.used_gb} / ${d.total_gb} GB</div>
            </div>
            <div class="disk-percent" style="color:${getColor(d.percent)}">${d.percent}%</div>
            <div style="width:80px"><div class="progress-bar" style="margin:0"><div class="progress-fill dynamic" style="width:${d.percent}%;background:${getGradient(d.percent)}"></div></div></div>
        </div>
    `).join('');
}

function setText(id, text) { const el = document.getElementById(id); if (el) el.textContent = text; }
function setBar(id, pct) { const el = document.getElementById(id); if (el) el.style.width = Math.min(pct, 100) + '%'; }
function setBarColor(id, pct) {
    const el = document.getElementById(id);
    if (!el) return;
    el.className = 'progress-fill ' + (pct > 90 ? 'red' : pct > 70 ? 'purple' : 'cyan');
}
function getColor(pct) { return pct > 90 ? '#ef4444' : pct > 70 ? '#f59e0b' : '#10b981'; }
function getGradient(pct) { return pct > 90 ? 'linear-gradient(90deg,#ef4444,#dc2626)' : pct > 70 ? 'linear-gradient(90deg,#f59e0b,#ef4444)' : 'linear-gradient(90deg,#10b981,#00d4ff)'; }

async function loadOverview() {
    try {
        const res = await Auth.apiFetch('/api/monitor/overview');
        if (!res) return;
        const data = await res.json();
        if (data.system) {
            setText('serverHostname', data.system.hostname);
            setText('uptimeBadge', '⏱ ' + data.system.uptime_human);
            if (data.cpu?.info) setText('cpuSub', data.cpu.info.logical_cores + ' cores • ' + (data.cpu.info.frequency?.current || 0) + ' MHz');
        }
    } catch (e) { console.warn('Overview load failed:', e); }
}

async function loadProcesses() {
    try {
        const res = await Auth.apiFetch('/api/monitor/processes?sort=cpu&limit=8');
        if (!res) return;
        const data = await res.json();
        if (data.summary) setText('procCount', data.summary.total + ' processes');
        const tbody = document.getElementById('processTable');
        if (tbody && data.processes) {
            tbody.innerHTML = data.processes.map(p => `
                <tr><td class="truncate" style="max-width:120px">${p.name}</td>
                <td style="color:${getColor(p.cpu_percent)}">${p.cpu_percent}%</td>
                <td>${p.memory_percent}%</td>
                <td class="text-muted text-xs">${p.user}</td></tr>
            `).join('');
        }
    } catch(e) { console.warn('Process load failed:', e); }
}
