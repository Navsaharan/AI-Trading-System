// Initialize DataTables
$(document).ready(function() {
    $('#recentTradesTable').DataTable({
        responsive: true,
        ajax: '/api/admin/recent-trades',
        columns: [
            { data: 'user' },
            { data: 'symbol' },
            { data: 'type' },
            { 
                data: 'amount',
                render: function(data) {
                    return new Intl.NumberFormat('en-IN', {
                        style: 'currency',
                        currency: 'INR'
                    }).format(data);
                }
            },
            {
                data: 'status',
                render: function(data) {
                    const statusClasses = {
                        'COMPLETE': 'bg-green-100 text-green-800',
                        'PENDING': 'bg-yellow-100 text-yellow-800',
                        'FAILED': 'bg-red-100 text-red-800'
                    };
                    return `<span class="px-2 py-1 text-xs font-medium rounded-full ${statusClasses[data]}">${data}</span>`;
                }
            }
        ],
        order: [[0, 'desc']]
    });
});

// WebSocket connection for real-time updates
const socket = new WebSocket('ws://localhost:5000/admin/ws');

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    switch (data.type) {
        case 'STATS_UPDATE':
            updateStats(data.payload);
            break;
        case 'SYSTEM_LOG':
            addSystemLog(data.payload);
            break;
        case 'TRADE_UPDATE':
            updateTradeTable(data.payload);
            break;
    }
};

// Update statistics
function updateStats(stats) {
    // Update user stats
    document.querySelector('#total-users').textContent = stats.users.total;
    document.querySelector('#user-growth').textContent = `${stats.users.growth}%`;
    updateChart('usersChart', stats.users.chart_data);

    // Update trades stats
    document.querySelector('#active-trades').textContent = stats.trades.total;
    document.querySelector('#trade-change').textContent = `${stats.trades.change}%`;
    updateChart('tradesChart', stats.trades.chart_data);

    // Update revenue stats
    document.querySelector('#total-revenue').textContent = formatCurrency(stats.revenue.total);
    document.querySelector('#revenue-growth').textContent = `${stats.revenue.growth}%`;
    updateChart('revenueChart', stats.revenue.chart_data);

    // Update system status
    document.querySelector('#cpu-usage').textContent = `${stats.system.cpu}%`;
    document.querySelector('#cpu-bar').style.width = `${stats.system.cpu}%`;
    document.querySelector('#memory-usage').textContent = `${stats.system.memory}%`;
    document.querySelector('#memory-bar').style.width = `${stats.system.memory}%`;
}

// Initialize charts
function initializeCharts() {
    const chartConfig = {
        type: 'line',
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    display: false
                },
                y: {
                    display: false
                }
            },
            elements: {
                point: {
                    radius: 0
                },
                line: {
                    tension: 0.4
                }
            }
        }
    };

    ['usersChart', 'tradesChart', 'revenueChart'].forEach(chartId => {
        const ctx = document.getElementById(chartId).getContext('2d');
        new Chart(ctx, {
            ...chartConfig,
            data: {
                labels: Array(12).fill(''),
                datasets: [{
                    data: Array(12).fill(0),
                    borderColor: '#10B981',
                    borderWidth: 2,
                    fill: false
                }]
            }
        });
    });
}

// Update chart data
function updateChart(chartId, data) {
    const chart = Chart.getChart(chartId);
    chart.data.datasets[0].data = data;
    chart.update();
}

// Add system log
function addSystemLog(log) {
    const logsContainer = document.querySelector('#system-logs');
    const logElement = document.createElement('div');
    logElement.className = 'flex items-start space-x-4';
    
    const statusColors = {
        'error': 'bg-red-500',
        'warning': 'bg-yellow-500',
        'info': 'bg-green-500'
    };
    
    logElement.innerHTML = `
        <div class="flex-shrink-0">
            <span class="inline-block w-2 h-2 rounded-full ${statusColors[log.level]} mt-2"></span>
        </div>
        <div>
            <p class="text-sm text-gray-600">${log.message}</p>
            <p class="text-xs text-gray-400">${formatTime(log.timestamp)}</p>
        </div>
    `;
    
    logsContainer.insertBefore(logElement, logsContainer.firstChild);
    
    // Keep only last 5 logs
    if (logsContainer.children.length > 5) {
        logsContainer.removeChild(logsContainer.lastChild);
    }
}

// Update trade table
function updateTradeTable(trade) {
    const table = $('#recentTradesTable').DataTable();
    table.row.add(trade).draw(false);
}

// Utility functions
function formatCurrency(value) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(value);
}

function formatTime(timestamp) {
    const now = new Date();
    const date = new Date(timestamp);
    const diffMinutes = Math.floor((now - date) / 60000);
    
    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes} minutes ago`;
    if (diffMinutes < 1440) return `${Math.floor(diffMinutes / 60)} hours ago`;
    return `${Math.floor(diffMinutes / 1440)} days ago`;
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeCharts();
});
