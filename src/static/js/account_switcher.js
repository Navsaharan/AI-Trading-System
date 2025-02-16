// Account Switcher Component
class AccountSwitcher {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.accounts = [];
        this.activeAccount = null;
        this.init();
    }

    async init() {
        // Create UI elements
        this.createUI();
        
        // Load accounts
        await this.loadAccounts();
        
        // Start session monitoring
        this.startSessionMonitor();
    }

    createUI() {
        this.container.innerHTML = `
            <div class="account-switcher">
                <div class="account-switcher-header">
                    <span class="active-account-label">Active Account</span>
                    <div class="active-account-info"></div>
                </div>
                <div class="account-list" style="display: none;"></div>
            </div>
        `;

        // Add event listeners
        this.container.querySelector('.account-switcher-header').addEventListener(
            'click', 
            () => this.toggleAccountList()
        );
    }

    async loadAccounts() {
        try {
            const response = await fetch('/api/trading/accounts');
            const accounts = await response.json();
            
            this.accounts = accounts;
            this.renderAccounts();
            
            // Set active account
            const active = accounts.find(acc => acc.is_active);
            if (active) {
                this.setActiveAccount(active.account_id);
            }
        } catch (error) {
            console.error('Error loading accounts:', error);
            this.showError('Failed to load accounts');
        }
    }

    renderAccounts() {
        const accountList = this.container.querySelector('.account-list');
        accountList.innerHTML = this.accounts.map(account => `
            <div class="account-item ${account.is_active ? 'active' : ''}" 
                 data-account-id="${account.account_id}">
                <img src="/static/images/${account.broker_name.toLowerCase()}.png" 
                     alt="${account.broker_name}" 
                     class="broker-icon">
                <div class="account-details">
                    <div class="account-name">${account.broker_name}</div>
                    <div class="account-id">${account.account_id}</div>
                </div>
                ${account.is_active ? '<div class="active-indicator">Active</div>' : ''}
            </div>
        `).join('');

        // Add click handlers
        accountList.querySelectorAll('.account-item').forEach(item => {
            item.addEventListener('click', () => {
                this.switchAccount(item.dataset.accountId);
            });
        });
    }

    async switchAccount(accountId) {
        try {
            // Show loading state
            this.showLoading();

            // Call API to switch account
            const response = await fetch('/api/trading/switch-account', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ account_id: accountId })
            });

            if (!response.ok) {
                throw new Error('Failed to switch account');
            }

            // Update UI
            this.setActiveAccount(accountId);
            this.toggleAccountList();
            
            // Show success message
            this.showSuccess('Account switched successfully');
            
            // Refresh account data
            await this.loadAccounts();

        } catch (error) {
            console.error('Error switching account:', error);
            this.showError('Failed to switch account');
        } finally {
            this.hideLoading();
        }
    }

    setActiveAccount(accountId) {
        this.activeAccount = this.accounts.find(acc => acc.account_id === accountId);
        
        // Update active account display
        const activeInfo = this.container.querySelector('.active-account-info');
        if (this.activeAccount) {
            activeInfo.innerHTML = `
                <img src="/static/images/${this.activeAccount.broker_name.toLowerCase()}.png" 
                     alt="${this.activeAccount.broker_name}" 
                     class="broker-icon">
                <div class="account-details">
                    <div class="account-name">${this.activeAccount.broker_name}</div>
                    <div class="account-id">${this.activeAccount.account_id}</div>
                </div>
            `;
        }
    }

    toggleAccountList() {
        const accountList = this.container.querySelector('.account-list');
        const isHidden = accountList.style.display === 'none';
        
        if (isHidden) {
            accountList.style.display = 'block';
            setTimeout(() => {
                accountList.style.opacity = '1';
                accountList.style.transform = 'translateY(0)';
            }, 10);
        } else {
            accountList.style.opacity = '0';
            accountList.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                accountList.style.display = 'none';
            }, 300);
        }
    }

    startSessionMonitor() {
        // Check session status every minute
        setInterval(async () => {
            try {
                const response = await fetch('/api/trading/session-status');
                const status = await response.json();
                
                if (!status.valid) {
                    this.showWarning('Session expired. Reconnecting...');
                    await this.refreshSession();
                }
            } catch (error) {
                console.error('Session monitor error:', error);
            }
        }, 60000);
    }

    async refreshSession() {
        try {
            const response = await fetch('/api/trading/refresh-session', {
                method: 'POST'
            });
            
            if (!response.ok) {
                throw new Error('Failed to refresh session');
            }
            
            this.showSuccess('Session refreshed');
        } catch (error) {
            console.error('Error refreshing session:', error);
            this.showError('Failed to refresh session');
        }
    }

    // UI Helpers
    showLoading() {
        // Add loading indicator
        this.container.classList.add('loading');
    }

    hideLoading() {
        // Remove loading indicator
        this.container.classList.remove('loading');
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showWarning(message) {
        this.showNotification(message, 'warning');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Initialize account switcher
document.addEventListener('DOMContentLoaded', () => {
    const accountSwitcher = new AccountSwitcher('account-switcher-container');
});
