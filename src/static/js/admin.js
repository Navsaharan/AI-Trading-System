// FamilyHVSDN Admin Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Firebase Auth
    initializeAuth();
    
    // Setup navigation
    setupNavigation();
    
    // Load initial dashboard data
    loadDashboardData();
    
    // Setup event listeners for settings
    setupSettingsListeners();
});

// Firebase Authentication
function initializeAuth() {
    firebase.auth().onAuthStateChanged(function(user) {
        if (!user) {
            window.location.href = '/login';
        }
    });
}

// Navigation Setup
function setupNavigation() {
    const navLinks = {
        'Dashboard': '/',
        'Users': '/admin/users',
        'Trading': '/admin/trading-rules',
        'Settings': '/admin/settings'
    };
    
    document.querySelectorAll('nav a').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.textContent.trim();
            window.location.href = navLinks[page];
        });
    });
}

// Load Dashboard Data
async function loadDashboardData() {
    try {
        const [usersData, tradesData, systemHealth] = await Promise.all([
            fetch('/api/admin/users/stats').then(r => r.json()),
            fetch('/api/admin/trades/stats').then(r => r.json()),
            fetch('/api/admin/system/health').then(r => r.json())
        ]);
        
        // Update UI
        document.getElementById('totalUsers').textContent = usersData.total;
        document.getElementById('activeTrades').textContent = tradesData.active;
        
        // Update system health indicators
        updateSystemHealth(systemHealth);
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showError('Failed to load dashboard data');
    }
}

// Settings Event Listeners
function setupSettingsListeners() {
    // Trading Settings
    const tradingForm = document.querySelector('.trading-settings form');
    if (tradingForm) {
        tradingForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(tradingForm);
            try {
                const response = await fetch('/api/admin/trading-settings', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(Object.fromEntries(formData))
                });
                
                if (response.ok) {
                    showSuccess('Trading settings updated successfully');
                } else {
                    throw new Error('Failed to update trading settings');
                }
            } catch (error) {
                console.error('Error updating trading settings:', error);
                showError('Failed to update trading settings');
            }
        });
    }
    
    // AI Settings
    const aiForm = document.querySelector('.ai-settings form');
    if (aiForm) {
        aiForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(aiForm);
            try {
                const response = await fetch('/api/admin/ai-settings', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(Object.fromEntries(formData))
                });
                
                if (response.ok) {
                    showSuccess('AI settings updated successfully');
                } else {
                    throw new Error('Failed to update AI settings');
                }
            } catch (error) {
                console.error('Error updating AI settings:', error);
                showError('Failed to update AI settings');
            }
        });
    }
}

// Utility Functions
function updateSystemHealth(health) {
    const indicators = {
        system: document.querySelector('.system-health'),
        api: document.querySelector('.api-status')
    };
    
    if (indicators.system) {
        indicators.system.textContent = health.status;
        indicators.system.className = `text-3xl font-bold text-${health.status === 'Good' ? 'green' : 'red'}-500`;
    }
    
    if (indicators.api) {
        indicators.api.textContent = health.api_status;
        indicators.api.className = `text-3xl font-bold text-${health.api_status === 'Online' ? 'green' : 'red'}-500`;
    }
}

function showSuccess(message) {
    // Implement toast or notification system
    alert(message);
}

function showError(message) {
    // Implement toast or notification system
    alert('Error: ' + message);
}
