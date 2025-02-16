// Investment Preferences Popup Manager
class InvestmentPreferencesManager {
    constructor() {
        this.isNewUser = this.checkIfNewUser();
        this.smartInvestmentService = new SmartInvestmentService();
        this.initialized = false;
    }

    async initialize() {
        if (this.initialized) return;
        
        if (this.isNewUser) {
            await this.showPreferencesPopup();
        }
        
        this.initialized = true;
    }

    checkIfNewUser() {
        return !localStorage.getItem('investment_preferences_set');
    }

    async showPreferencesPopup() {
        const popup = document.createElement('div');
        popup.className = 'preferences-popup';
        popup.innerHTML = `
            <div class="preferences-content">
                <h2>Welcome to Smart Trading! 🚀</h2>
                <p>Let's set up your investment preferences to get started.</p>
                
                <div class="preference-section">
                    <h3>Investment Allocation</h3>
                    
                    <div class="allocation-sliders">
                        <div class="slider-group">
                            <label>Intraday Trading</label>
                            <input type="range" id="intraday-slider" min="0" max="100" value="20">
                            <span id="intraday-value">20%</span>
                        </div>
                        
                        <div class="slider-group">
                            <label>Swing Trading</label>
                            <input type="range" id="swing-slider" min="0" max="100" value="30">
                            <span id="swing-value">30%</span>
                        </div>
                        
                        <div class="slider-group">
                            <label>Long-term Investment</label>
                            <input type="range" id="longterm-slider" min="0" max="100" value="50">
                            <span id="longterm-value">50%</span>
                        </div>
                    </div>
                </div>
                
                <div class="preference-section">
                    <h3>Profit Reinvestment</h3>
                    <div class="slider-group">
                        <label>Percentage of Profits to Reinvest</label>
                        <input type="range" id="reinvestment-slider" min="0" max="100" value="50">
                        <span id="reinvestment-value">50%</span>
                    </div>
                </div>
                
                <div class="preference-section">
                    <h3>Risk Profile</h3>
                    <div class="risk-options">
                        <label>
                            <input type="radio" name="risk-level" value="low">
                            Conservative (Low Risk)
                        </label>
                        <label>
                            <input type="radio" name="risk-level" value="medium" checked>
                            Balanced (Medium Risk)
                        </label>
                        <label>
                            <input type="radio" name="risk-level" value="high">
                            Aggressive (High Risk)
                        </label>
                    </div>
                </div>
                
                <div class="preference-section">
                    <h3>Auto-Compounding</h3>
                    <div class="compound-options">
                        <label>
                            <input type="checkbox" id="auto-compound" checked>
                            Enable AI-powered auto-compounding
                        </label>
                    </div>
                </div>
                
                <div class="action-buttons">
                    <button id="use-ai-recommended" class="btn-secondary">Use AI Recommended</button>
                    <button id="save-preferences" class="btn-primary">Save Preferences</button>
                </div>
            </div>
        `;

        document.body.appendChild(popup);
        this.initializeEventListeners(popup);
    }

    initializeEventListeners(popup) {
        // Sliders synchronization
        const sliders = ['intraday', 'swing', 'longterm'];
        sliders.forEach(type => {
            const slider = document.getElementById(`${type}-slider`);
            const value = document.getElementById(`${type}-value`);
            
            slider.addEventListener('input', () => {
                value.textContent = `${slider.value}%`;
                this.synchronizeSliders(type, parseInt(slider.value));
            });
        });

        // Reinvestment slider
        const reinvestmentSlider = document.getElementById('reinvestment-slider');
        const reinvestmentValue = document.getElementById('reinvestment-value');
        reinvestmentSlider.addEventListener('input', () => {
            reinvestmentValue.textContent = `${reinvestmentSlider.value}%`;
        });

        // AI Recommended button
        document.getElementById('use-ai-recommended').addEventListener('click', async () => {
            await this.loadAIRecommendedSettings();
        });

        // Save button
        document.getElementById('save-preferences').addEventListener('click', async () => {
            await this.savePreferences(popup);
        });
    }

    synchronizeSliders(changedType, value) {
        const sliders = {
            intraday: document.getElementById('intraday-slider'),
            swing: document.getElementById('swing-slider'),
            longterm: document.getElementById('longterm-slider')
        };
        
        const values = {
            intraday: parseInt(sliders.intraday.value),
            swing: parseInt(sliders.swing.value),
            longterm: parseInt(sliders.longterm.value)
        };
        
        values[changedType] = value;
        
        // Calculate adjustment needed
        const total = Object.values(values).reduce((a, b) => a + b, 0);
        const excess = total - 100;
        
        if (excess > 0) {
            // Adjust other sliders proportionally
            const otherTypes = Object.keys(values).filter(t => t !== changedType);
            const totalOthers = otherTypes.reduce((sum, type) => sum + values[type], 0);
            
            otherTypes.forEach(type => {
                const newValue = Math.max(0, values[type] - (excess * values[type] / totalOthers));
                sliders[type].value = newValue;
                document.getElementById(`${type}-value`).textContent = `${Math.round(newValue)}%`;
            });
        }
    }

    async loadAIRecommendedSettings() {
        try {
            const userProfile = await this.getUserProfile();
            const marketConditions = await this.getMarketConditions();
            
            const recommended = await this.smartInvestmentService.getRecommendedAllocation(
                userProfile,
                marketConditions
            );
            
            if (recommended) {
                // Update sliders
                this.updateSlider('intraday', recommended.intraday_amount);
                this.updateSlider('swing', recommended.swing_amount);
                this.updateSlider('longterm', recommended.long_term_amount);
                
                // Update reinvestment
                this.updateSlider('reinvestment', recommended.profit_reinvestment_percentage * 100);
                
                // Update risk level
                document.querySelector(`input[name="risk-level"][value="${recommended.risk_level}"]`).checked = true;
                
                // Update auto-compound
                document.getElementById('auto-compound').checked = recommended.auto_compound;
            }
        } catch (error) {
            console.error('Error loading AI recommendations:', error);
            this.showError('Failed to load AI recommendations. Please try again or set manually.');
        }
    }

    updateSlider(type, value) {
        const slider = document.getElementById(`${type}-slider`);
        const valueSpan = document.getElementById(`${type}-value`);
        if (slider && valueSpan) {
            slider.value = value;
            valueSpan.textContent = `${Math.round(value)}%`;
        }
    }

    async savePreferences(popup) {
        try {
            const preferences = {
                allocation: {
                    intraday: parseInt(document.getElementById('intraday-slider').value) / 100,
                    swing: parseInt(document.getElementById('swing-slider').value) / 100,
                    longterm: parseInt(document.getElementById('longterm-slider').value) / 100
                },
                profit_reinvestment: parseInt(document.getElementById('reinvestment-slider').value) / 100,
                risk_level: document.querySelector('input[name="risk-level"]:checked').value,
                auto_compound: document.getElementById('auto-compound').checked
            };

            // Validate total allocation
            const totalAllocation = Object.values(preferences.allocation).reduce((a, b) => a + b, 0);
            if (Math.abs(totalAllocation - 1) > 0.01) {
                this.showError('Total allocation must equal 100%');
                return;
            }

            // Save to backend
            await this.savePreferencesToBackend(preferences);
            
            // Mark as initialized
            localStorage.setItem('investment_preferences_set', 'true');
            
            // Remove popup
            popup.remove();
            
            // Show success message
            this.showSuccess('Preferences saved successfully!');
            
        } catch (error) {
            console.error('Error saving preferences:', error);
            this.showError('Failed to save preferences. Please try again.');
        }
    }

    showError(message) {
        // Implement error notification
        console.error(message);
    }

    showSuccess(message) {
        // Implement success notification
        console.log(message);
    }

    async getUserProfile() {
        // Implement getting user profile from backend
        return {
            age: 30,
            trading_experience_years: 2,
            income_type: 'stable',
            investment_knowledge: 'medium',
            risk_tolerance: 'medium'
        };
    }

    async getMarketConditions() {
        // Implement getting market conditions from backend
        return {
            market: { trend_score: 0.7 },
            sector: { health_score: 0.8 }
        };
    }

    async savePreferencesToBackend(preferences) {
        // Implement saving to backend
        return new Promise(resolve => setTimeout(resolve, 500));
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    const preferencesManager = new InvestmentPreferencesManager();
    preferencesManager.initialize();
});
