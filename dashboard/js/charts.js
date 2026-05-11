/* VPS Panel - Chart.js Setup */
const CHART_MAX_POINTS = 60;
const chartColors = {
    cyan: 'rgba(0,212,255,', purple: 'rgba(124,58,237,',
    green: 'rgba(16,185,129,', red: 'rgba(239,68,68,',
    amber: 'rgba(245,158,11,', pink: 'rgba(236,72,153,'
};
function makeGradient(ctx, color) {
    const g = ctx.createLinearGradient(0, 0, 0, 220);
    g.addColorStop(0, color + '0.3)'); g.addColorStop(1, color + '0.01)');
    return g;
}
const chartDefaults = {
    responsive: true, maintainAspectRatio: false, animation: { duration: 500 },
    plugins: { legend: { display: true, labels: { color: '#94a3b8', boxWidth: 10, padding: 15, font: { family: 'Inter', size: 11 } } } },
    scales: {
        x: { display: true, grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { color: '#64748b', font: { size: 10 }, maxTicksLimit: 8 } },
        y: { display: true, min: 0, max: 100, grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { color: '#64748b', font: { size: 10 }, callback: v => v + '%' } }
    }
};
let historyChart, networkChart, timeLabels = [];

function initCharts() {
    const hCtx = document.getElementById('historyChart');
    const nCtx = document.getElementById('networkChart');
    if (!hCtx || !nCtx) return;
    historyChart = new Chart(hCtx, {
        type: 'line',
        data: {
            labels: timeLabels,
            datasets: [
                { label: 'CPU %', data: [], borderColor: chartColors.cyan + '1)', backgroundColor: makeGradient(hCtx.getContext('2d'), chartColors.cyan), fill: true, tension: 0.4, borderWidth: 2, pointRadius: 0 },
                { label: 'RAM %', data: [], borderColor: chartColors.purple + '1)', backgroundColor: 'transparent', fill: false, tension: 0.4, borderWidth: 2, pointRadius: 0, borderDash: [5, 3] }
            ]
        },
        options: { ...chartDefaults }
    });
    const netOpts = JSON.parse(JSON.stringify(chartDefaults));
    netOpts.scales.y.max = undefined; netOpts.scales.y.ticks = { color: '#64748b', font: { size: 10 }, callback: v => v + ' KB/s' };
    networkChart = new Chart(nCtx, {
        type: 'line',
        data: {
            labels: timeLabels,
            datasets: [
                { label: '↑ Upload', data: [], borderColor: chartColors.green + '1)', backgroundColor: makeGradient(nCtx.getContext('2d'), chartColors.green), fill: true, tension: 0.4, borderWidth: 2, pointRadius: 0 },
                { label: '↓ Download', data: [], borderColor: chartColors.amber + '1)', backgroundColor: 'transparent', fill: false, tension: 0.4, borderWidth: 2, pointRadius: 0 }
            ]
        },
        options: netOpts
    });
}

function pushChartData(data) {
    if (!historyChart || !networkChart) return;
    const now = new Date().toLocaleTimeString('en', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    timeLabels.push(now);
    if (timeLabels.length > CHART_MAX_POINTS) timeLabels.shift();

    const cpuDs = historyChart.data.datasets[0].data;
    const ramDs = historyChart.data.datasets[1].data;
    cpuDs.push(data.cpu?.overall || 0); ramDs.push(data.ram?.percent || 0);
    if (cpuDs.length > CHART_MAX_POINTS) { cpuDs.shift(); ramDs.shift(); }
    historyChart.update('none');

    const upDs = networkChart.data.datasets[0].data;
    const downDs = networkChart.data.datasets[1].data;
    upDs.push(data.network?.upload_speed || 0); downDs.push(data.network?.download_speed || 0);
    if (upDs.length > CHART_MAX_POINTS) { upDs.shift(); downDs.shift(); }
    networkChart.update('none');
}
