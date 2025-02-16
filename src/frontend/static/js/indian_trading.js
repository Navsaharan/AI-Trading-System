// Market Data WebSocket
let marketSocket;
let chartWidget;
let backtestChart;

// Initialize TradingView widget
function initTradingViewWidget() {
    new TradingView.widget({
        "container_id": "tradingview-chart",
        "symbol": "NSE:NIFTY",
        "interval": "15",
        "timezone": "Asia/Kolkata",
        "theme": "light",
        "style": "1",
        "locale": "in",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "studies": [
            "RSI@tv-basicstudies",
            "MACD@tv-basicstudies",
            "BB@tv-basicstudies",
            "Supertrend@tv-basicstudies"
        ]
    });
}

// Initialize WebSocket connection
function initWebSocket() {
    marketSocket = new WebSocket('ws://localhost:5000/ws/market');
    
    marketSocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        updateMarketData(data);
    };
    
    marketSocket.onclose = function() {
        console.log('WebSocket connection closed');
        // Attempt to reconnect after 5 seconds
        setTimeout(initWebSocket, 5000);
    };
}

// Update market data
function updateMarketData(data) {
    // Update Nifty 50
    if (data.nifty) {
        document.getElementById('nifty-value').textContent = data.nifty.last;
        document.getElementById('nifty-change').textContent = 
            `${data.nifty.change > 0 ? '+' : ''}${data.nifty.change} (${data.nifty.changePercent}%)`;
    }
    
    // Update Bank Nifty
    if (data.bankNifty) {
        document.getElementById('banknifty-value').textContent = data.bankNifty.last;
        document.getElementById('banknifty-change').textContent = 
            `${data.bankNifty.change > 0 ? '+' : ''}${data.bankNifty.change} (${data.bankNifty.changePercent}%)`;
    }
    
    // Update India VIX
    if (data.vix) {
        document.getElementById('vix-value').textContent = data.vix.last;
        document.getElementById('vix-change').textContent = 
            `${data.vix.change > 0 ? '+' : ''}${data.vix.change} (${data.vix.changePercent}%)`;
    }
    
    // Update Market Breadth
    if (data.breadth) {
        document.getElementById('advances').textContent = data.breadth.advances;
        document.getElementById('declines').textContent = data.breadth.declines;
        document.getElementById('unchanged').textContent = data.breadth.unchanged;
        document.getElementById('ad-ratio').textContent = (data.breadth.advances / data.breadth.declines).toFixed(2);
    }
}

// Place order
async function placeOrder(event) {
    event.preventDefault();
    
    const orderData = {
        symbol: document.getElementById('symbol').value,
        orderType: document.getElementById('orderType').value,
        quantity: parseInt(document.getElementById('quantity').value),
        price: parseFloat(document.getElementById('price').value),
        productType: document.getElementById('productType').value,
        transactionType: event.submitter.textContent.toUpperCase()
    };
    
    try {
        const response = await fetch('/api/order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(orderData)
        });
        
        const result = await response.json();
        if (result.status === 'success') {
            alert('Order placed successfully!');
            updatePositions();
        } else {
            alert(`Order failed: ${result.message}`);
        }
    } catch (error) {
        console.error('Error placing order:', error);
        alert('Failed to place order. Please try again.');
    }
}

// Update positions
async function updatePositions() {
    try {
        const response = await fetch('/api/positions');
        const positions = await response.json();
        
        const tbody = document.getElementById('positions-body');
        tbody.innerHTML = '';
        
        positions.forEach(position => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${position.symbol}</td>
                <td>${position.type}</td>
                <td>${position.quantity}</td>
                <td>${position.averagePrice}</td>
                <td>${position.ltp}</td>
                <td class="${position.pnl >= 0 ? 'text-success' : 'text-danger'}">${position.pnl}</td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="closePosition('${position.symbol}')">
                        Close
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error updating positions:', error);
    }
}

// Close position
async function closePosition(symbol) {
    if (confirm(`Are you sure you want to close position for ${symbol}?`)) {
        try {
            const response = await fetch('/api/position/close', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ symbol })
            });
            
            const result = await response.json();
            if (result.status === 'success') {
                alert('Position closed successfully!');
                updatePositions();
            } else {
                alert(`Failed to close position: ${result.message}`);
            }
        } catch (error) {
            console.error('Error closing position:', error);
            alert('Failed to close position. Please try again.');
        }
    }
}

// Update option chain
async function updateOptionChain() {
    try {
        const symbol = document.getElementById('symbol').value;
        const response = await fetch(`/api/option-chain?symbol=${symbol}`);
        const data = await response.json();
        
        const tbody = document.getElementById('option-chain-body');
        tbody.innerHTML = '';
        
        data.forEach(strike => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${strike.strikePrice}</td>
                <td>${strike.CE.lastPrice}</td>
                <td>${strike.CE.impliedVolatility}%</td>
                <td>${strike.PE.lastPrice}</td>
                <td>${strike.PE.impliedVolatility}%</td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error updating option chain:', error);
    }
}

// Run backtest
async function runBacktest(event) {
    event.preventDefault();
    
    const backtestData = {
        strategy: document.getElementById('strategy').value,
        symbol: document.getElementById('backtest-symbol').value,
        timeframe: document.getElementById('timeframe').value,
        startDate: document.getElementById('start-date').value,
        endDate: document.getElementById('end-date').value
    };
    
    try {
        const response = await fetch('/api/backtest', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(backtestData)
        });
        
        const result = await response.json();
        if (result.status === 'success') {
            updateBacktestResults(result.data);
        } else {
            alert(`Backtest failed: ${result.message}`);
        }
    } catch (error) {
        console.error('Error running backtest:', error);
        alert('Failed to run backtest. Please try again.');
    }
}

// Update backtest results
function updateBacktestResults(data) {
    document.getElementById('total-returns').textContent = `${data.totalReturns}%`;
    document.getElementById('sharpe-ratio').textContent = data.sharpeRatio;
    document.getElementById('max-drawdown').textContent = `${data.maxDrawdown}%`;
    
    // Update backtest chart
    if (backtestChart) {
        backtestChart.destroy();
    }
    
    const ctx = document.getElementById('backtest-chart').getContext('2d');
    backtestChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.dates,
            datasets: [{
                label: 'Portfolio Value',
                data: data.portfolioValues,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Backtest Performance'
                }
            },
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
}

// Initialize everything when the page loads
document.addEventListener('DOMContentLoaded', function() {
    initTradingViewWidget();
    initWebSocket();
    
    // Add event listeners
    document.getElementById('orderForm').addEventListener('submit', placeOrder);
    document.getElementById('backtestForm').addEventListener('submit', runBacktest);
    
    // Initial updates
    updatePositions();
    updateOptionChain();
    
    // Set up periodic updates
    setInterval(updatePositions, 5000);  // Update positions every 5 seconds
    setInterval(updateOptionChain, 10000);  // Update option chain every 10 seconds
});
