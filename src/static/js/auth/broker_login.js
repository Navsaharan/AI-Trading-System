class BrokerLogin {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.selectedBroker = null;
        this.init();
    }

    init() {
        this.createUI();
        this.loadBrokerList();
    }

    createUI() {
        this.container.innerHTML = `
            <div class="broker-login">
                <div class="step-indicator">
                    <div class="step active" data-step="1">
                        <span class="step-number">1</span>
                        <span class="step-text">Select Platform</span>
                    </div>
                    <div class="step" data-step="2">
                        <span class="step-number">2</span>
                        <span class="step-text">Login</span>
                    </div>
                    <div class="step" data-step="3">
                        <span class="step-number">3</span>
                        <span class="step-text">Link Account</span>
                    </div>
                    <div class="step" data-step="4">
                        <span class="step-number">4</span>
                        <span class="step-text">Start Trading</span>
                    </div>
                </div>

                <div class="login-content">
                    <!-- Step 1: Broker Selection -->
                    <div class="broker-selection active" data-content="1">
                        <h3>Select Your Trading Platform</h3>
                        <div class="broker-grid"></div>
                    </div>

                    <!-- Step 2: Login Form -->
                    <div class="login-form" data-content="2">
                        <h3>Login to <span class="broker-name"></span></h3>
                        <div class="login-methods"></div>
                    </div>

                    <!-- Step 3: Account Linking -->
                    <div class="account-linking" data-content="3">
                        <h3>Linking Your Account</h3>
                        <div class="linking-status"></div>
                    </div>

                    <!-- Step 4: Success -->
                    <div class="login-success" data-content="4">
                        <h3>Account Successfully Linked!</h3>
                        <div class="success-message"></div>
                        <button class="start-trading-btn">Start Trading</button>
                    </div>
                </div>
            </div>
        `;

        // Add event listener for start trading button
        this.container.querySelector('.start-trading-btn')
            .addEventListener('click', () => this.startTrading());
    }

    async loadBrokerList() {
        try {
            const response = await fetch('/api/brokers/list');
            const brokers = await response.json();
            
            this.renderBrokerGrid(brokers);
        } catch (error) {
            console.error('Error loading broker list:', error);
            this.showError('Failed to load brokers');
        }
    }

    renderBrokerGrid(brokers) {
        const grid = this.container.querySelector('.broker-grid');
        grid.innerHTML = brokers.map(broker => `
            <div class="broker-card" data-broker="${broker.name.toLowerCase()}">
                <img src="/static/images/brokers/${broker.name.toLowerCase()}.png" 
                     alt="${broker.name}" 
                     class="broker-logo">
                <h4>${broker.name}</h4>
                <span class="broker-type">${broker.type}</span>
                <div class="broker-features">
                    ${broker.features.map(feature => 
                        `<span class="feature-tag">${feature}</span>`
                    ).join('')}
                </div>
            </div>
        `).join('');

        // Add click handlers
        grid.querySelectorAll('.broker-card').forEach(card => {
            card.addEventListener('click', () => {
                this.selectBroker(card.dataset.broker);
            });
        });
    }

    async selectBroker(brokerName) {
        try {
            this.selectedBroker = brokerName;
            
            // Initialize broker login
            const response = await fetch('/api/brokers/login/init', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ broker: brokerName })
            });

            const loginData = await response.json();
            
            if (loginData.error) {
                throw new Error(loginData.error);
            }

            // Move to login step
            this.showStep(2);
            this.renderLoginMethods(loginData);

        } catch (error) {
            console.error('Error selecting broker:', error);
            this.showError('Failed to initialize login');
        }
    }

    renderLoginMethods(loginData) {
        const methodsContainer = this.container.querySelector('.login-methods');
        const brokerName = this.container.querySelector('.broker-name');
        
        brokerName.textContent = this.selectedBroker.charAt(0).toUpperCase() + 
                                this.selectedBroker.slice(1);

        if (loginData.type === 'oauth') {
            methodsContainer.innerHTML = `
                <div class="oauth-login">
                    <p>Click below to securely connect your account</p>
                    <button class="oauth-btn" onclick="window.location.href='${loginData.auth_url}'">
                        Connect ${this.selectedBroker.charAt(0).toUpperCase() + 
                        this.selectedBroker.slice(1)} Account
                    </button>
                </div>
            `;
        } else {
            methodsContainer.innerHTML = `
                <div class="manual-login">
                    <p>Enter your login credentials</p>
                    <form class="manual-login-form">
                        <div class="form-group">
                            <label>User ID</label>
                            <input type="text" name="user_id" required>
                        </div>
                        <div class="form-group">
                            <label>Password</label>
                            <input type="password" name="password" required>
                        </div>
                        <div class="form-group">
                            <label>PIN</label>
                            <input type="password" name="pin" required>
                        </div>
                        <button type="submit">Login</button>
                    </form>
                </div>
            `;

            // Add form submit handler
            methodsContainer.querySelector('.manual-login-form')
                .addEventListener('submit', (e) => this.handleManualLogin(e));
        }
    }

    async handleManualLogin(e) {
        e.preventDefault();
        
        try {
            const formData = new FormData(e.target);
            const credentials = {
                user_id: formData.get('user_id'),
                password: formData.get('password'),
                pin: formData.get('pin')
            };

            const response = await fetch('/api/brokers/login/manual', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    broker: this.selectedBroker,
                    credentials
                })
            });

            const result = await response.json();
            
            if (result.error) {
                throw new Error(result.error);
            }

            // Move to linking step
            this.showStep(3);
            this.handleAccountLinking(result);

        } catch (error) {
            console.error('Manual login error:', error);
            this.showError('Login failed. Please check your credentials.');
        }
    }

    async handleAccountLinking(sessionData) {
        const linkingStatus = this.container.querySelector('.linking-status');
        linkingStatus.innerHTML = `
            <div class="linking-progress">
                <div class="spinner"></div>
                <p>Linking your account...</p>
            </div>
        `;

        try {
            // Verify session
            const response = await fetch('/api/brokers/session/verify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    broker: this.selectedBroker,
                    session: sessionData
                })
            });

            const result = await response.json();
            
            if (result.error) {
                throw new Error(result.error);
            }

            // Move to success step
            setTimeout(() => {
                this.showStep(4);
                this.showSuccess(result);
            }, 1500);

        } catch (error) {
            console.error('Account linking error:', error);
            linkingStatus.innerHTML = `
                <div class="linking-error">
                    <span class="error-icon">❌</span>
                    <p>Failed to link account. Please try again.</p>
                    <button onclick="window.location.reload()">Retry</button>
                </div>
            `;
        }
    }

    showSuccess(result) {
        const successMessage = this.container.querySelector('.success-message');
        successMessage.innerHTML = `
            <div class="success-details">
                <span class="success-icon">✓</span>
                <h4>${this.selectedBroker.charAt(0).toUpperCase() + 
                     this.selectedBroker.slice(1)} Account Linked</h4>
                <p>Your account has been successfully connected.</p>
                <div class="account-info">
                    <p>Account ID: ${result.account_id}</p>
                    <p>Session valid until: ${new Date(result.expires_at).toLocaleString()}</p>
                </div>
            </div>
        `;
    }

    startTrading() {
        window.location.href = '/trading/dashboard';
    }

    showStep(step) {
        // Update step indicators
        this.container.querySelectorAll('.step').forEach(s => {
            s.classList.toggle('active', parseInt(s.dataset.step) <= step);
            s.classList.toggle('complete', parseInt(s.dataset.step) < step);
        });

        // Show corresponding content
        this.container.querySelectorAll('[data-content]').forEach(content => {
            content.classList.toggle('active', 
                parseInt(content.dataset.content) === step);
        });
    }

    showError(message) {
        const notification = document.createElement('div');
        notification.className = 'notification error';
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Initialize broker login
document.addEventListener('DOMContentLoaded', () => {
    const brokerLogin = new BrokerLogin('broker-login-container');
});
