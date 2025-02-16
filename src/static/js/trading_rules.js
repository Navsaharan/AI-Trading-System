// FamilyHVSDN Trading Rules JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Firebase Auth
    initializeAuth();
    
    // Load initial data
    loadTradingRules();
    
    // Setup event listeners
    setupEventListeners();
});

// Firebase Authentication
function initializeAuth() {
    firebase.auth().onAuthStateChanged(function(user) {
        if (!user) {
            window.location.href = '/login';
        }
    });
}

// Load Trading Rules
async function loadTradingRules() {
    try {
        // Load risk management rules
        const riskResponse = await fetch('/api/admin/trading-rules/risk');
        const riskRules = await riskResponse.json();
        populateRiskManagementForm(riskRules);
        
        // Load trading time rules
        const timeResponse = await fetch('/api/admin/trading-rules/time');
        const timeRules = await timeResponse.json();
        populateTradingTimeForm(timeRules);
        
        // Load custom rules
        const customResponse = await fetch('/api/admin/trading-rules/custom');
        const customRules = await customResponse.json();
        populateCustomRulesTable(customRules);
        
    } catch (error) {
        console.error('Error loading trading rules:', error);
        showError('Failed to load trading rules');
    }
}

// Populate Risk Management Form
function populateRiskManagementForm(rules) {
    const form = document.getElementById('riskManagementForm');
    form.maxDailyLoss.value = rules.maxDailyLoss;
    form.maxPositionSize.value = rules.maxPositionSize;
    form.stopLoss.value = rules.stopLoss;
}

// Populate Trading Time Form
function populateTradingTimeForm(rules) {
    const form = document.getElementById('tradingTimeForm');
    form.tradingStartTime.value = rules.startTime;
    form.tradingEndTime.value = rules.endTime;
    
    // Set trading days
    const tradingDays = rules.tradingDays || [];
    form.querySelectorAll('input[name="tradingDays"]').forEach(checkbox => {
        checkbox.checked = tradingDays.includes(checkbox.value);
    });
}

// Populate Custom Rules Table
function populateCustomRulesTable(rules) {
    const tableBody = document.getElementById('customRulesTableBody');
    tableBody.innerHTML = ''; // Clear existing rows
    
    rules.forEach(rule => {
        const row = createCustomRuleRow(rule);
        tableBody.appendChild(row);
    });
}

// Create Custom Rule Row
function createCustomRuleRow(rule) {
    const row = document.createElement('tr');
    
    row.innerHTML = `
        <td class="px-6 py-4 whitespace-nowrap">
            <div class="text-sm font-medium text-gray-900">${rule.name}</div>
        </td>
        <td class="px-6 py-4">
            <div class="text-sm text-gray-500">${rule.description}</div>
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
            <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${rule.active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                ${rule.active ? 'Active' : 'Inactive'}
            </span>
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
            <button onclick="editRule('${rule.id}')" class="text-indigo-600 hover:text-indigo-900 mr-4">Edit</button>
            <button onclick="deleteRule('${rule.id}')" class="text-red-600 hover:text-red-900">Delete</button>
        </td>
    `;
    
    return row;
}

// Setup Event Listeners
function setupEventListeners() {
    // Risk Management Form
    document.getElementById('riskManagementForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        
        try {
            const response = await fetch('/api/admin/trading-rules/risk', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(Object.fromEntries(formData))
            });
            
            if (response.ok) {
                showSuccess('Risk management rules updated successfully');
            } else {
                throw new Error('Failed to update risk management rules');
            }
        } catch (error) {
            console.error('Error updating risk rules:', error);
            showError('Failed to update risk management rules');
        }
    });
    
    // Trading Time Form
    document.getElementById('tradingTimeForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        
        // Get selected trading days
        const tradingDays = [];
        e.target.querySelectorAll('input[name="tradingDays"]:checked').forEach(checkbox => {
            tradingDays.push(checkbox.value);
        });
        
        try {
            const response = await fetch('/api/admin/trading-rules/time', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    startTime: formData.get('tradingStartTime'),
                    endTime: formData.get('tradingEndTime'),
                    tradingDays: tradingDays
                })
            });
            
            if (response.ok) {
                showSuccess('Trading time rules updated successfully');
            } else {
                throw new Error('Failed to update trading time rules');
            }
        } catch (error) {
            console.error('Error updating time rules:', error);
            showError('Failed to update trading time rules');
        }
    });
    
    // Add Rule Button
    document.getElementById('addRuleBtn').addEventListener('click', () => {
        document.getElementById('addRuleModal').classList.remove('hidden');
    });
    
    // Add Rule Form
    document.getElementById('addRuleForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        
        try {
            const response = await fetch('/api/admin/trading-rules/custom', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(Object.fromEntries(formData))
            });
            
            if (response.ok) {
                closeModal();
                loadTradingRules();
                showSuccess('Custom rule added successfully');
            } else {
                throw new Error('Failed to add custom rule');
            }
        } catch (error) {
            console.error('Error adding custom rule:', error);
            showError('Failed to add custom rule');
        }
    });
}

// Edit Rule
async function editRule(ruleId) {
    // Implement edit rule functionality
    console.log('Edit rule:', ruleId);
}

// Delete Rule
async function deleteRule(ruleId) {
    if (!confirm('Are you sure you want to delete this rule?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/admin/trading-rules/custom/${ruleId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            loadTradingRules();
            showSuccess('Rule deleted successfully');
        } else {
            throw new Error('Failed to delete rule');
        }
    } catch (error) {
        console.error('Error deleting rule:', error);
        showError('Failed to delete rule');
    }
}

// Modal Functions
function closeModal() {
    document.getElementById('addRuleModal').classList.add('hidden');
    document.getElementById('addRuleForm').reset();
}

// Utility Functions
function showSuccess(message) {
    // Implement toast or notification system
    alert(message);
}

function showError(message) {
    // Implement toast or notification system
    alert('Error: ' + message);
}
