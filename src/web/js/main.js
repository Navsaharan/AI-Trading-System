// API Configuration
const API_URL = 'http://localhost:8000';
let token = localStorage.getItem('token');

// Chart Configuration
let tradingChart;

// Authentication Functions
async function login(event) {
    event.preventDefault();
    
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch(`${API_URL}/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
        });
        
        const data = await response.json();
        
        if (response.ok) {
            token = data.access_token;
            localStorage.setItem('token', token);
            localStorage.setItem('username', username);
            showDashboard();
        } else {
            alert('Login failed: ' + data.detail);
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('Login failed. Please try again.');
    }
}

async function register(event) {
    event.preventDefault();
    
    const username = document.getElementById('registerUsername').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    
    try {
        const response = await fetch(`${API_URL}/users/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Registration successful! Please login.');
            toggleForms();
        } else {
            alert('Registration failed: ' + data.detail);
        }
    } catch (error) {
        console.error('Registration error:', error);
        alert('Registration failed. Please try again.');
    }
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    showAuthForms();
}

// UI Functions
function toggleForms() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    loginForm.classList.toggle('hidden');
    registerForm.classList.toggle('hidden');
}

function showDashboard() {
    document.getElementById('authForms').classList.add('hidden');
    document.getElementById('dashboard').classList.remove('hidden');
    document.getElementById('userInfo').classList.remove('hidden');
    document.getElementById('username').textContent = localStorage.getItem('username');
    
    initializeChart();
    loadPositions();
    startDataUpdates();
}

function showAuthForms() {
    document.getElementById('authForms').classList.remove('hidden');
    document.getElementById('dashboard').classList.add('hidden');
    document.getElementById('userInfo').classList.add('hidden');
}

// Trading Functions
async function startTrading() {
    const strategy = document.getElementById('strategySelect').value;
    if (!strategy) {
        alert('Please select a strategy');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/trading/start`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                strategy_id: strategy,
                risk_params: {
                    stop_loss: parseFloat(document.getElementById('stopLoss').value) / 100,
                    take_profit: parseFloat(document.getElementById('takeProfit').value) / 100
                }
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Trading started successfully!');
        } else {
            alert('Failed to start trading: ' + data.detail);
        }
    } catch (error) {
        console.error('Trading error:', error);
        alert('Failed to start trading. Please try again.');
    }
}

async function loadPositions() {
    try {
        const response = await fetch(`${API_URL}/trading/positions`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const positions = await response.json();
        
        const tbody = document.getElementById('positionsTable');
        tbody.innerHTML = '';
        
        positions.forEach(position => {
            const row = document.createElement('tr');
            const pnl = position.unrealized_pnl;
            const pnlClass = pnl >= 0 ? 'text-green-500' : 'text-red-500';
            
            row.innerHTML = `
                <td class="p-4">${position.symbol}</td>
                <td class="p-4">${position.quantity}</td>
                <td class="p-4">$${position.entry_price.toFixed(2)}</td>
                <td class="p-4">$${position.current_price.toFixed(2)}</td>
                <td class="p-4 ${pnlClass}">$${pnl.toFixed(2)}</td>
            `;
            
            tbody.appendChild(row);
        });
        
        updatePortfolioMetrics(positions);
    } catch (error) {
        console.error('Error loading positions:', error);
    }
}

function updatePortfolioMetrics(positions) {
    const totalValue = positions.reduce((sum, pos) => sum + pos.current_price * pos.quantity, 0);
    const dailyPnL = positions.reduce((sum, pos) => sum + pos.unrealized_pnl, 0);
    
    document.getElementById('totalValue').textContent = `$${totalValue.toFixed(2)}`;
    document.getElementById('dailyPnL').textContent = `$${dailyPnL.toFixed(2)}`;
    document.getElementById('openPositions').textContent = positions.length;
    
    document.getElementById('dailyPnL').className = 
        dailyPnL >= 0 ? 'font-bold text-green-500' : 'font-bold text-red-500';
}

// Chart Functions
function initializeChart() {
    const ctx = document.getElementById('tradingChart').getContext('2d');
    
    tradingChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Portfolio Value',
                data: [],
                borderColor: 'rgb(59, 130, 246)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Portfolio Performance'
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

function updateChart(value) {
    const now = new Date().toLocaleTimeString();
    
    tradingChart.data.labels.push(now);
    tradingChart.data.datasets[0].data.push(value);
    
    if (tradingChart.data.labels.length > 20) {
        tradingChart.data.labels.shift();
        tradingChart.data.datasets[0].data.shift();
    }
    
    tradingChart.update();
}

// Real-time Updates
function startDataUpdates() {
    // Update positions and chart every 5 seconds
    setInterval(() => {
        loadPositions();
        const totalValue = parseFloat(document.getElementById('totalValue').textContent.replace('$', ''));
        updateChart(totalValue);
    }, 5000);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    if (token) {
        showDashboard();
    } else {
        showAuthForms();
    }
});
