// ai_trading_system Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard
    initializeDashboard();
    
    // Set up theme toggle
    setupThemeToggle();
    
    // Set up real-time updates
    setupRealtimeUpdates();
    
    // Initialize charts
    initializeCharts();
});

function initializeDashboard() {
    // Update user name
    updateUserInfo();
    
    // Set up navigation
    setupNavigation();
    
    // Initialize market data
    updateMarketData();
    
    // Set up event listeners
    setupEventListeners();
}

function setupRealtimeUpdates() {
    // Update market data every 5 seconds
    setInterval(updateMarketData, 5000);
    
    // Update trading signals every 30 seconds
    setInterval(updateTradingSignals, 30000);
    
    // Update portfolio data every minute
    setInterval(updatePortfolio, 60000);
}

function updateMarketData() {
    fetch('/api/market-data')
        .then(response => response.json())
        .then(data => {
            updateMarketStats(data);
            updateMarketChart(data);
        })
        .catch(error => console.error('Error updating market data:', error));
}

function updateTradingSignals() {
    fetch('/api/trading-signals')
        .then(response => response.json())
        .then(data => {
            updateSignalsContainer(data);
        })
        .catch(error => console.error('Error updating signals:', error));
}

function updatePortfolio() {
    fetch('/api/portfolio')
        .then(response => response.json())
        .then(data => {
            updatePortfolioStats(data);
            updatePortfolioChart(data);
            updateInvestmentStats(data);
        })
        .catch(error => console.error('Error updating portfolio:', error));
}

function updateMarketStats(data) {
    // Update market statistics
    const stats = document.querySelectorAll('.market-stats .stat-box');
    
    data.indices.forEach((index, i) => {
        const priceElement = stats[i].querySelector('.price');
        const changeElement = stats[i].querySelector('.change');
        
        priceElement.textContent = index.price.toLocaleString('en-IN');
        changeElement.textContent = `${index.change > 0 ? '+' : ''}${index.change}%`;
        
        // Update classes for styling
        priceElement.className = `price ${index.change > 0 ? 'up' : 'down'}`;
        changeElement.className = `change ${index.change > 0 ? 'up' : 'down'}`;
    });
}

function updateSignalsContainer(data) {
    const container = document.querySelector('.signals-container');
    container.innerHTML = ''; // Clear existing signals
    
    data.signals.forEach(signal => {
        const signalBox = document.createElement('div');
        signalBox.className = `signal-box ${signal.type.toLowerCase()}`;
        
        signalBox.innerHTML = `
            <h4>${signal.symbol}</h4>
            <p class="signal-type">${signal.type}</p>
            <p class="signal-price">₹${signal.price.toLocaleString('en-IN')}</p>
            <p class="signal-confidence">Confidence: ${signal.confidence}%</p>
        `;
        
        container.appendChild(signalBox);
    });
}

function updatePortfolioStats(data) {
    const stats = document.querySelectorAll('.portfolio-stats .metric-box p');
    
    // Update total value
    stats[0].textContent = `₹${data.totalValue.toLocaleString('en-IN')}`;
    
    // Update today's P&L
    const pnl = stats[1];
    pnl.textContent = `${data.todayPnL > 0 ? '+' : ''}₹${Math.abs(data.todayPnL).toLocaleString('en-IN')}`;
    pnl.className = data.todayPnL > 0 ? 'up' : 'down';
    
    // Update overall return
    const returns = stats[2];
    returns.textContent = `${data.overallReturn > 0 ? '+' : ''}${data.overallReturn}%`;
    returns.className = data.overallReturn > 0 ? 'up' : 'down';
}

function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Remove active class from all links
            navLinks.forEach(l => l.classList.remove('active'));
            
            // Add active class to clicked link
            link.classList.add('active');
            
            // Update content based on selected nav item
            updateContent(link.getAttribute('href').substring(1));
        });
    });
}

function setupEventListeners() {
    // Logout button
    const logoutBtn = document.getElementById('logout-btn');
    logoutBtn.addEventListener('click', handleLogout);
    
    // Refresh button
    const refreshBtn = document.querySelector('.refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            updateMarketData();
            updateTradingSignals();
            updatePortfolio();
        });
    }
    
    // Charges breakdown toggle
    const chargesToggle = document.querySelector('.charges-toggle');
    if (chargesToggle) {
        chargesToggle.addEventListener('click', () => {
            const details = document.querySelector('.charges-details');
            const isHidden = details.classList.contains('hidden');
            
            details.classList.toggle('hidden');
            chargesToggle.textContent = isHidden ? 'Hide Charges ▲' : 'View Charges ▼';
        });
    }
}

function handleLogout() {
    fetch('/api/logout', {
        method: 'POST',
        credentials: 'same-origin'
    })
    .then(response => {
        if (response.ok) {
            window.location.href = '/login';
        }
    })
    .catch(error => console.error('Error during logout:', error));
}

function updateUserInfo() {
    fetch('/api/user-info')
        .then(response => response.json())
        .then(data => {
            const userNameElement = document.getElementById('user-name');
            userNameElement.textContent = `Welcome, ${data.name}`;
        })
        .catch(error => console.error('Error updating user info:', error));
}

function updateContent(section) {
    // Hide all sections
    const sections = document.querySelectorAll('main > section');
    sections.forEach(s => s.style.display = 'none');
    
    // Show selected section
    const selectedSection = document.querySelector(`#${section}`);
    if (selectedSection) {
        selectedSection.style.display = 'block';
    }
    
    // Update charts if needed
    if (section === 'dashboard') {
        updateMarketData();
        updateTradingSignals();
        updatePortfolio();
    }
}

function setupThemeToggle() {
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const toggleIcon = themeToggleBtn.querySelector('.toggle-icon');
    const toggleText = themeToggleBtn.querySelector('.toggle-text');
    
    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        toggleIcon.textContent = '🌙';
        toggleText.textContent = 'Dark Mode';
    }
    
    themeToggleBtn.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        const isDarkMode = document.body.classList.contains('dark-mode');
        
        // Update toggle button
        toggleIcon.textContent = isDarkMode ? '🌙' : '🌞';
        toggleText.textContent = isDarkMode ? 'Dark Mode' : 'Light Mode';
        
        // Save preference
        localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
        
        // Update charts theme
        updateChartsTheme(isDarkMode);
    });
}

function updateInvestmentStats(data) {
    // Update total invested
    const totalInvestedElement = document.querySelector('.stat-card:nth-child(1) .stat-value');
    totalInvestedElement.textContent = `₹${data.totalInvested.toLocaleString('en-IN')}`;
    
    // Update total return
    const totalReturnElement = document.querySelector('.stat-card:nth-child(2) .stat-value');
    const totalReturnChangeElement = document.querySelector('.stat-card:nth-child(2) .stat-change');
    const totalReturnPercentage = ((data.totalReturn - data.totalInvested) / data.totalInvested) * 100;
    
    totalReturnElement.textContent = `₹${data.totalReturn.toLocaleString('en-IN')}`;
    totalReturnElement.className = `stat-value ${totalReturnPercentage >= 0 ? 'positive' : 'negative'}`;
    
    totalReturnChangeElement.textContent = `${totalReturnPercentage >= 0 ? '+' : ''}${totalReturnPercentage.toFixed(2)}%`;
    totalReturnChangeElement.className = `stat-change ${totalReturnPercentage >= 0 ? 'positive' : 'negative'}`;
    
    // Update profit
    const profitElement = document.querySelector('.stat-card:nth-child(3) .stat-value');
    const profitChangeElement = document.querySelector('.stat-card:nth-child(3) .stat-change');
    const profit = data.totalReturn - data.totalInvested;
    const profitPercentage = (profit / data.totalInvested) * 100;
    
    profitElement.textContent = `₹${profit.toLocaleString('en-IN')}`;
    profitElement.className = `stat-value ${profit >= 0 ? 'positive' : 'negative'}`;
    
    profitChangeElement.textContent = `${profitPercentage >= 0 ? '+' : ''}${profitPercentage.toFixed(2)}%`;
    profitChangeElement.className = `stat-change ${profitPercentage >= 0 ? 'positive' : 'negative'}`;
    
    // Update net profit and charges
    const netProfitElement = document.querySelector('.stat-card:nth-child(4) .stat-value');
    
    // Update charges breakdown
    if (data.charges) {
        const chargeValues = document.querySelectorAll('.charge-value');
        chargeValues[0].textContent = `₹${data.charges.brokerage.toLocaleString('en-IN')}`;
        chargeValues[1].textContent = `₹${data.charges.stt.toLocaleString('en-IN')}`;
        chargeValues[2].textContent = `₹${data.charges.transaction_charges.toLocaleString('en-IN')}`;
        chargeValues[3].textContent = `₹${data.charges.gst.toLocaleString('en-IN')}`;
        chargeValues[4].textContent = `₹${data.charges.sebi_charges.toLocaleString('en-IN')}`;
        chargeValues[5].textContent = `₹${data.charges.stamp_duty.toLocaleString('en-IN')}`;
        chargeValues[6].textContent = `₹${data.charges.total.toLocaleString('en-IN')}`;
    }
    
    const netProfit = profit - (data.charges ? data.charges.total : 0);
    netProfitElement.textContent = `₹${netProfit.toLocaleString('en-IN')}`;
    netProfitElement.className = `stat-value ${netProfit >= 0 ? 'positive' : 'negative'}`;
}

function updateChartsTheme(isDarkMode) {
    const chartConfig = {
        paper_bgcolor: isDarkMode ? '#1a1a1a' : '#ffffff',
        plot_bgcolor: isDarkMode ? '#1a1a1a' : '#ffffff',
        font: {
            color: isDarkMode ? '#ffffff' : '#333333'
        },
        xaxis: {
            gridcolor: isDarkMode ? '#404040' : '#e0e0e0'
        },
        yaxis: {
            gridcolor: isDarkMode ? '#404040' : '#e0e0e0'
        }
    };
    
    // Update all charts with new theme
    const charts = ['market-chart', 'portfolio-chart', 'risk-chart', 'ai-chart'];
    charts.forEach(chartId => {
        const chartDiv = document.getElementById(chartId);
        if (chartDiv && chartDiv.data) {
            Plotly.relayout(chartId, chartConfig);
        }
    });
}
