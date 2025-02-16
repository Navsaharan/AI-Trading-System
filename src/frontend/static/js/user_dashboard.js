// WebSocket connection for real-time updates
const socket = new WebSocket('ws://localhost:5000/ws');

// Handle WebSocket messages
socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    switch (data.type) {
        case 'MARKET_DATA':
            updateMarketData(data.payload);
            break;
        case 'PORTFOLIO_UPDATE':
            updatePortfolio(data.payload);
            break;
        case 'POSITION_UPDATE':
            updatePositions(data.payload);
            break;
        case 'ORDER_UPDATE':
            updateOrders(data.payload);
            break;
        case 'AI_INSIGHTS':
            updateAIInsights(data.payload);
            break;
    }
};

// Update market data
function updateMarketData(data) {
    // Update NIFTY and BANKNIFTY widgets
    if (window.niftyWidget) {
        window.niftyWidget.setSymbol('NSE:NIFTY', data.nifty.last_price);
    }
    if (window.bankniftyWidget) {
        window.bankniftyWidget.setSymbol('NSE:BANKNIFTY', data.banknifty.last_price);
    }
}

// Update portfolio summary
function updatePortfolio(data) {
    document.querySelector('#total-value').textContent = formatCurrency(data.total_value);
    document.querySelector('#pnl').textContent = formatCurrency(data.pnl);
    document.querySelector('#available-margin').textContent = formatCurrency(data.available_margin);
    
    // Update progress bars
    document.querySelector('#total-value-bar').style.width = `${data.total_value_percentage}%`;
    document.querySelector('#pnl-bar').style.width = `${data.pnl_percentage}%`;
    document.querySelector('#margin-bar').style.width = `${data.margin_percentage}%`;
}

// Update positions table
function updatePositions(positions) {
    const tbody = document.querySelector('#positions-table tbody');
    tbody.innerHTML = '';
    
    positions.forEach(position => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${position.symbol}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500">${position.quantity}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500">${formatCurrency(position.average_price)}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500">${formatCurrency(position.ltp)}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-right ${position.pnl >= 0 ? 'text-green-500' : 'text-red-500'}">${formatCurrency(position.pnl)}</td>
        `;
        tbody.appendChild(row);
    });
}

// Update orders table
function updateOrders(orders) {
    const tbody = document.querySelector('#orders-table tbody');
    tbody.innerHTML = '';
    
    orders.forEach(order => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${formatTime(order.time)}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${order.symbol}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-right ${order.type === 'BUY' ? 'text-green-500' : 'text-red-500'}">${order.type}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500">${order.quantity}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500">${formatCurrency(order.price)}</td>
        `;
        tbody.appendChild(row);
    });
}

// Update AI insights
function updateAIInsights(insights) {
    // Update sentiment chart
    updateSentimentChart(insights.sentiment);
    
    // Update price predictions
    document.querySelector('#nifty-current').textContent = formatCurrency(insights.nifty.current);
    document.querySelector('#nifty-predicted').textContent = formatCurrency(insights.nifty.predicted);
    
    // Update trading signals
    const signalsContainer = document.querySelector('#trading-signals');
    signalsContainer.innerHTML = '';
    
    insights.signals.forEach(signal => {
        const signalElement = document.createElement('div');
        signalElement.className = 'flex items-center justify-between';
        signalElement.innerHTML = `
            <span class="text-sm">${signal.symbol}</span>
            <span class="px-2 py-1 text-xs font-medium rounded-full ${
                signal.action === 'BUY' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }">${signal.action}</span>
        `;
        signalsContainer.appendChild(signalElement);
    });
}

// Utility functions
function formatCurrency(value) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(value);
}

function formatTime(timestamp) {
    return new Date(timestamp).toLocaleTimeString('en-IN', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Initialize TradingView widgets
document.addEventListener('DOMContentLoaded', () => {
    initializeTradingViewWidgets();
    initializeCharts();
});
