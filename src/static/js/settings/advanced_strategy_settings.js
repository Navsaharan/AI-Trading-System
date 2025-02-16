// Advanced Strategy Settings Manager
class AdvancedStrategySettings {
    constructor() {
        this.initialized = false;
        this.currentSettings = {};
        this.riskWarningAccepted = false;
    }

    async initialize() {
        if (this.initialized) return;
        
        // Load user settings
        await this.loadUserSettings();
        
        // Initialize UI
        this.initializeUI();
        
        this.initialized = true;
    }

    async loadUserSettings() {
        try {
            const response = await fetch('/api/user/strategy-settings');
            this.currentSettings = await response.json();
        } catch (error) {
            console.error('Error loading settings:', error);
            this.currentSettings = this.getDefaultSettings();
        }
    }

    getDefaultSettings() {
        return {
            gamma_scalping: {
                enabled: false,
                risk_level: 'moderate',
                max_position_size: 5, // % of portfolio
                max_daily_trades: 10,
                use_ai_protection: true
            },
            news_trading: {
                enabled: false,
                risk_level: 'high',
                max_position_size: 3,
                max_daily_trades: 15,
                use_ai_protection: true
            },
            vix_hedging: {
                enabled: false,
                risk_level: 'moderate',
                max_hedge_ratio: 0.5,
                auto_adjust: true,
                use_ai_protection: true
            },
            gap_trading: {
                enabled: false,
                risk_level: 'high',
                max_gap_size: 5, // %
                max_position_size: 4,
                use_ai_protection: true
            },
            dark_pool_tracking: {
                enabled: false,
                risk_level: 'extreme',
                min_block_size: 10000, // shares
                use_ai_protection: true
            },
            multi_broker_execution: {
                enabled: false,
                risk_level: 'high',
                max_brokers: 3,
                randomize_execution: true,
                use_ai_protection: true
            },
            stealth_execution: {
                enabled: false,
                risk_level: 'extreme',
                max_order_split: 5,
                random_delays: true,
                use_ai_protection: true
            }
        };
    }

    initializeUI() {
        const container = document.createElement('div');
        container.className = 'advanced-settings-container';
        container.innerHTML = this.generateSettingsHTML();
        
        document.getElementById('settings-content').appendChild(container);
        
        this.initializeEventListeners();
    }

    generateSettingsHTML() {
        return `
            <div class="settings-section">
                <h2>Advanced Trading Strategies ⚠️</h2>
                <div class="risk-warning">
                    <p>⚠️ WARNING: These strategies involve higher risk and should be used with caution.</p>
                    <p>Please ensure you understand the risks before enabling any strategy.</p>
                </div>
                
                ${this.generateStrategySettings()}
                
                <div class="risk-acceptance">
                    <label>
                        <input type="checkbox" id="risk-acceptance-checkbox">
                        I understand and accept the risks associated with these strategies
                    </label>
                </div>
                
                <div class="settings-actions">
                    <button id="save-advanced-settings" class="btn-primary" disabled>
                        Save Advanced Settings
                    </button>
                    <button id="reset-advanced-settings" class="btn-secondary">
                        Reset to Default
                    </button>
                </div>
            </div>
        `;
    }

    generateStrategySettings() {
        return `
            <div class="strategy-settings">
                ${this.generateGammaScalpingSettings()}
                ${this.generateNewsTradingSettings()}
                ${this.generateVixHedgingSettings()}
                ${this.generateGapTradingSettings()}
                ${this.generateDarkPoolSettings()}
                ${this.generateMultiBrokerSettings()}
                ${this.generateStealthExecutionSettings()}
            </div>
        `;
    }

    generateGammaScalpingSettings() {
        const settings = this.currentSettings.gamma_scalping;
        return `
            <div class="strategy-card">
                <h3>Gamma Scalping</h3>
                <div class="strategy-controls">
                    <label class="switch">
                        <input type="checkbox" 
                               id="gamma-scalping-enabled"
                               ${settings.enabled ? 'checked' : ''}>
                        <span class="slider"></span>
                    </label>
                    
                    <div class="strategy-params">
                        <div class="param-group">
                            <label>Risk Level</label>
                            <select id="gamma-scalping-risk">
                                <option value="moderate" ${settings.risk_level === 'moderate' ? 'selected' : ''}>Moderate</option>
                                <option value="high" ${settings.risk_level === 'high' ? 'selected' : ''}>High</option>
                            </select>
                        </div>
                        
                        <div class="param-group">
                            <label>Max Position Size (%)</label>
                            <input type="number" 
                                   id="gamma-scalping-size"
                                   value="${settings.max_position_size}"
                                   min="1" max="10">
                        </div>
                        
                        <div class="param-group">
                            <label>Max Daily Trades</label>
                            <input type="number"
                                   id="gamma-scalping-trades"
                                   value="${settings.max_daily_trades}"
                                   min="1" max="50">
                        </div>
                        
                        <div class="param-group">
                            <label>
                                <input type="checkbox"
                                       id="gamma-scalping-ai"
                                       ${settings.use_ai_protection ? 'checked' : ''}>
                                Use AI Protection
                            </label>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Similar generate functions for other strategies...

    initializeEventListeners() {
        // Risk acceptance
        const riskCheckbox = document.getElementById('risk-acceptance-checkbox');
        const saveButton = document.getElementById('save-advanced-settings');
        
        riskCheckbox.addEventListener('change', (e) => {
            this.riskWarningAccepted = e.target.checked;
            saveButton.disabled = !this.riskWarningAccepted;
        });
        
        // Save settings
        saveButton.addEventListener('click', async () => {
            await this.saveSettings();
        });
        
        // Reset settings
        document.getElementById('reset-advanced-settings')
            .addEventListener('click', () => {
                this.resetSettings();
            });
        
        // Strategy toggles
        this.initializeStrategyToggles();
    }

    initializeStrategyToggles() {
        const strategies = [
            'gamma-scalping',
            'news-trading',
            'vix-hedging',
            'gap-trading',
            'dark-pool',
            'multi-broker',
            'stealth-execution'
        ];
        
        strategies.forEach(strategy => {
            const toggle = document.getElementById(`${strategy}-enabled`);
            if (toggle) {
                toggle.addEventListener('change', (e) => {
                    this.updateStrategyState(strategy, e.target.checked);
                });
            }
        });
    }

    updateStrategyState(strategy, enabled) {
        const strategyParams = document.querySelector(`#${strategy}-params`);
        if (strategyParams) {
            strategyParams.style.display = enabled ? 'block' : 'none';
        }
        
        // Show warning if enabling high-risk strategy
        if (enabled && this.isHighRiskStrategy(strategy)) {
            this.showHighRiskWarning(strategy);
        }
    }

    isHighRiskStrategy(strategy) {
        const highRiskStrategies = [
            'dark-pool',
            'stealth-execution'
        ];
        return highRiskStrategies.includes(strategy);
    }

    showHighRiskWarning(strategy) {
        const warning = `
            ⚠️ WARNING: ${this.getStrategyName(strategy)} is a high-risk strategy.
            Please ensure you understand the risks and have proper risk management in place.
        `;
        
        // Show warning modal
        this.showWarningModal(warning);
    }

    async saveSettings() {
        if (!this.riskWarningAccepted) {
            this.showWarningModal('Please accept the risk warning first.');
            return;
        }
        
        try {
            const settings = this.gatherCurrentSettings();
            
            // Validate settings
            if (!this.validateSettings(settings)) {
                return;
            }
            
            // Save to backend
            await this.saveToBackend(settings);
            
            this.showSuccess('Advanced strategy settings saved successfully!');
            
        } catch (error) {
            console.error('Error saving settings:', error);
            this.showError('Failed to save settings. Please try again.');
        }
    }

    gatherCurrentSettings() {
        const settings = {};
        
        // Gather settings for each strategy
        const strategies = [
            'gamma-scalping',
            'news-trading',
            'vix-hedging',
            'gap-trading',
            'dark-pool',
            'multi-broker',
            'stealth-execution'
        ];
        
        strategies.forEach(strategy => {
            settings[strategy] = this.gatherStrategySettings(strategy);
        });
        
        return settings;
    }

    gatherStrategySettings(strategy) {
        return {
            enabled: document.getElementById(`${strategy}-enabled`).checked,
            risk_level: document.getElementById(`${strategy}-risk`).value,
            max_position_size: parseFloat(document.getElementById(`${strategy}-size`).value),
            max_daily_trades: parseInt(document.getElementById(`${strategy}-trades`).value),
            use_ai_protection: document.getElementById(`${strategy}-ai`).checked
        };
    }

    validateSettings(settings) {
        // Implement validation logic
        return true;
    }

    async saveToBackend(settings) {
        const response = await fetch('/api/user/strategy-settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        });
        
        if (!response.ok) {
            throw new Error('Failed to save settings');
        }
    }

    resetSettings() {
        this.currentSettings = this.getDefaultSettings();
        this.initializeUI();
    }

    showWarningModal(message) {
        // Implement warning modal
        console.warn(message);
    }

    showSuccess(message) {
        // Implement success notification
        console.log(message);
    }

    showError(message) {
        // Implement error notification
        console.error(message);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    const strategySettings = new AdvancedStrategySettings();
    strategySettings.initialize();
});
