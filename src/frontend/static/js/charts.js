function initializeCharts() {
    // Initialize Sentiment Chart
    const sentimentCtx = document.getElementById('sentimentChart').getContext('2d');
    new Chart(sentimentCtx, {
        type: 'doughnut',
        data: {
            labels: ['Bullish', 'Bearish', 'Neutral'],
            datasets: [{
                data: [75, 15, 10],
                backgroundColor: [
                    '#10B981', // Green
                    '#EF4444', // Red
                    '#6B7280'  // Gray
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: true
                }
            },
            cutout: '70%'
        }
    });

    // Initialize Portfolio Performance Chart
    const portfolioCtx = document.getElementById('portfolioChart')?.getContext('2d');
    if (portfolioCtx) {
        new Chart(portfolioCtx, {
            type: 'line',
            data: {
                labels: getLast30Days(),
                datasets: [{
                    label: 'Portfolio Value',
                    data: generateSampleData(30),
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
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
                        grid: {
                            display: false
                        },
                        ticks: {
                            maxTicksLimit: 5
                        }
                    },
                    y: {
                        grid: {
                            borderDash: [2, 2]
                        },
                        ticks: {
                            callback: function(value) {
                                return '₹' + formatNumber(value);
                            }
                        }
                    }
                }
            }
        });
    }

    // Initialize P&L Distribution Chart
    const pnlCtx = document.getElementById('pnlDistributionChart')?.getContext('2d');
    if (pnlCtx) {
        new Chart(pnlCtx, {
            type: 'bar',
            data: {
                labels: ['Stocks', 'Options', 'Futures'],
                datasets: [{
                    label: 'Profit/Loss',
                    data: [25000, -12000, 35000],
                    backgroundColor: function(context) {
                        const value = context.dataset.data[context.dataIndex];
                        return value >= 0 ? '#10B981' : '#EF4444';
                    }
                }]
            },
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
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        grid: {
                            borderDash: [2, 2]
                        },
                        ticks: {
                            callback: function(value) {
                                return '₹' + formatNumber(value);
                            }
                        }
                    }
                }
            }
        });
    }
}

// Utility functions
function getLast30Days() {
    const dates = [];
    for (let i = 29; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        dates.push(date.toLocaleDateString('en-IN', { day: '2-digit', month: 'short' }));
    }
    return dates;
}

function generateSampleData(points) {
    const data = [];
    let value = 500000; // Starting value
    for (let i = 0; i < points; i++) {
        value = value * (1 + (Math.random() * 0.04 - 0.02)); // Random change between -2% and +2%
        data.push(Math.round(value));
    }
    return data;
}

function formatNumber(num) {
    return new Intl.NumberFormat('en-IN', {
        maximumFractionDigits: 0,
        notation: 'compact',
        compactDisplay: 'short'
    }).format(num);
}

// Export the initialization function
window.initializeCharts = initializeCharts;
