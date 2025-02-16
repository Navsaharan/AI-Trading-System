class UserPreferences {
    constructor() {
        this.userId = this.getUserId();
        this.preferences = this.loadPreferences();
        this.initializePreferences();
    }

    getUserId() {
        // Get from auth token/session
        return document.querySelector('meta[name="user-id"]').content;
    }

    loadPreferences() {
        const savedPrefs = localStorage.getItem(`user_prefs_${this.userId}`);
        return savedPrefs ? JSON.parse(savedPrefs) : this.getDefaultPreferences();
    }

    getDefaultPreferences() {
        return {
            layout: {
                sidebarItems: [
                    { id: 'dashboard', visible: true, order: 1 },
                    { id: 'portfolio', visible: true, order: 2 },
                    { id: 'orders', visible: true, order: 3 },
                    { id: 'watchlist', visible: true, order: 4 },
                    { id: 'reports', visible: true, order: 5 },
                    { id: 'alerts', visible: true, order: 6 }
                ],
                quickActions: [],
                favoriteStocks: [],
                defaultCharts: []
            },
            display: {
                theme: 'light',
                fontSize: 'medium',
                chartStyle: 'candles',
                showProfitLoss: true,
                showCharges: true
            },
            trading: {
                defaultQuantity: 1,
                defaultOrderType: 'MARKET',
                confirmOrders: true,
                showSlippageWarning: true
            },
            notifications: {
                priceAlerts: true,
                orderUpdates: true,
                newsAlerts: true,
                emailNotifications: true
            },
            widgets: {
                marketOverview: { visible: true, position: 'top' },
                portfolioSummary: { visible: true, position: 'right' },
                orderBook: { visible: true, position: 'bottom' },
                watchlist: { visible: true, position: 'right' }
            }
        };
    }

    initializePreferences() {
        this.setupCustomizationPanel();
        this.applyPreferences();
        this.setupEventListeners();
    }

    setupCustomizationPanel() {
        const customizeBtn = document.createElement('button');
        customizeBtn.id = 'customize-layout-btn';
        customizeBtn.innerHTML = '<i class="fas fa-cog"></i> Customize Layout';
        customizeBtn.onclick = () => this.showCustomizationModal();
        
        document.querySelector('.user-controls').appendChild(customizeBtn);
    }

    showCustomizationModal() {
        const modal = document.createElement('div');
        modal.className = 'preferences-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h3>Customize Your Layout</h3>
                <div class="tabs">
                    <button class="tab-btn active" data-tab="layout">Layout</button>
                    <button class="tab-btn" data-tab="display">Display</button>
                    <button class="tab-btn" data-tab="trading">Trading</button>
                    <button class="tab-btn" data-tab="widgets">Widgets</button>
                </div>

                <div class="tab-content active" data-tab="layout">
                    <h4>Sidebar Items</h4>
                    <div class="sidebar-items-list">
                        ${this.preferences.layout.sidebarItems.map(item => `
                            <div class="preference-item" draggable="true" data-id="${item.id}">
                                <i class="fas fa-grip-lines"></i>
                                <span>${item.id.charAt(0).toUpperCase() + item.id.slice(1)}</span>
                                <label class="switch">
                                    <input type="checkbox" ${item.visible ? 'checked' : ''}>
                                    <span class="slider"></span>
                                </label>
                            </div>
                        `).join('')}
                    </div>

                    <h4>Quick Actions</h4>
                    <div class="quick-actions-editor">
                        <button class="add-action-btn">+ Add Quick Action</button>
                    </div>
                </div>

                <div class="tab-content" data-tab="display">
                    <div class="preference-group">
                        <label>Theme</label>
                        <select name="theme">
                            <option value="light" ${this.preferences.display.theme === 'light' ? 'selected' : ''}>Light</option>
                            <option value="dark" ${this.preferences.display.theme === 'dark' ? 'selected' : ''}>Dark</option>
                        </select>
                    </div>

                    <div class="preference-group">
                        <label>Font Size</label>
                        <select name="fontSize">
                            <option value="small">Small</option>
                            <option value="medium">Medium</option>
                            <option value="large">Large</option>
                        </select>
                    </div>

                    <div class="preference-group">
                        <label>Chart Style</label>
                        <select name="chartStyle">
                            <option value="candles">Candlesticks</option>
                            <option value="line">Line Chart</option>
                            <option value="bars">Bars</option>
                        </select>
                    </div>
                </div>

                <div class="tab-content" data-tab="trading">
                    <div class="preference-group">
                        <label>Default Quantity</label>
                        <input type="number" name="defaultQuantity" value="${this.preferences.trading.defaultQuantity}">
                    </div>

                    <div class="preference-group">
                        <label>Default Order Type</label>
                        <select name="defaultOrderType">
                            <option value="MARKET">Market</option>
                            <option value="LIMIT">Limit</option>
                            <option value="SL">Stop Loss</option>
                        </select>
                    </div>

                    <div class="preference-group">
                        <label>
                            <input type="checkbox" name="confirmOrders" ${this.preferences.trading.confirmOrders ? 'checked' : ''}>
                            Confirm Orders
                        </label>
                    </div>
                </div>

                <div class="tab-content" data-tab="widgets">
                    ${Object.entries(this.preferences.widgets).map(([widget, config]) => `
                        <div class="widget-config">
                            <h4>${widget.replace(/([A-Z])/g, ' $1').trim()}</h4>
                            <label class="switch">
                                <input type="checkbox" name="${widget}_visible" ${config.visible ? 'checked' : ''}>
                                <span class="slider"></span>
                            </label>
                            <select name="${widget}_position">
                                <option value="top" ${config.position === 'top' ? 'selected' : ''}>Top</option>
                                <option value="right" ${config.position === 'right' ? 'selected' : ''}>Right</option>
                                <option value="bottom" ${config.position === 'bottom' ? 'selected' : ''}>Bottom</option>
                                <option value="left" ${config.position === 'left' ? 'selected' : ''}>Left</option>
                            </select>
                        </div>
                    `).join('')}
                </div>

                <div class="modal-footer">
                    <button class="save-btn">Save Changes</button>
                    <button class="cancel-btn">Cancel</button>
                    <button class="reset-btn">Reset to Default</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        this.setupModalEventListeners(modal);
    }

    setupModalEventListeners(modal) {
        // Tab switching
        modal.querySelectorAll('.tab-btn').forEach(btn => {
            btn.onclick = () => {
                modal.querySelectorAll('.tab-btn, .tab-content').forEach(el => el.classList.remove('active'));
                btn.classList.add('active');
                modal.querySelector(`.tab-content[data-tab="${btn.dataset.tab}"]`).classList.add('active');
            };
        });

        // Save changes
        modal.querySelector('.save-btn').onclick = () => {
            this.savePreferences();
            modal.remove();
        };

        // Cancel
        modal.querySelector('.cancel-btn').onclick = () => modal.remove();

        // Reset to default
        modal.querySelector('.reset-btn').onclick = () => {
            if (confirm('Reset all preferences to default?')) {
                this.preferences = this.getDefaultPreferences();
                this.savePreferences();
                modal.remove();
                this.showCustomizationModal();
            }
        };

        // Setup drag and drop for sidebar items
        this.setupDragAndDrop(modal);
    }

    setupDragAndDrop(modal) {
        const items = modal.querySelectorAll('.sidebar-items-list .preference-item');
        items.forEach(item => {
            item.addEventListener('dragstart', e => {
                e.target.classList.add('dragging');
            });

            item.addEventListener('dragend', e => {
                e.target.classList.remove('dragging');
                this.updateSidebarOrder();
            });
        });

        const container = modal.querySelector('.sidebar-items-list');
        container.addEventListener('dragover', e => {
            e.preventDefault();
            const dragging = document.querySelector('.dragging');
            const siblings = [...container.querySelectorAll('.preference-item:not(.dragging)')];
            const nextSibling = siblings.find(sibling => {
                const box = sibling.getBoundingClientRect();
                return e.clientY <= box.top + box.height / 2;
            });
            container.insertBefore(dragging, nextSibling);
        });
    }

    updateSidebarOrder() {
        const items = document.querySelectorAll('.sidebar-items-list .preference-item');
        this.preferences.layout.sidebarItems = [...items].map((item, index) => ({
            id: item.dataset.id,
            visible: item.querySelector('input[type="checkbox"]').checked,
            order: index + 1
        }));
    }

    savePreferences() {
        localStorage.setItem(`user_prefs_${this.userId}`, JSON.stringify(this.preferences));
        this.applyPreferences();
    }

    applyPreferences() {
        // Apply theme
        document.body.className = this.preferences.display.theme;
        document.body.style.fontSize = this.getFontSize();

        // Apply sidebar order and visibility
        const sidebar = document.querySelector('.sidebar-nav');
        if (sidebar) {
            const sortedItems = [...this.preferences.layout.sidebarItems]
                .sort((a, b) => a.order - b.order);

            sidebar.innerHTML = '';
            sortedItems.forEach(item => {
                if (item.visible) {
                    const link = document.createElement('a');
                    link.href = `#${item.id}`;
                    link.className = 'nav-item';
                    link.innerHTML = `
                        <i class="fas fa-${this.getIconForItem(item.id)}"></i>
                        <span>${item.id.charAt(0).toUpperCase() + item.id.slice(1)}</span>
                    `;
                    sidebar.appendChild(link);
                }
            });
        }

        // Apply widget layout
        Object.entries(this.preferences.widgets).forEach(([widget, config]) => {
            const widgetEl = document.querySelector(`.widget-${widget}`);
            if (widgetEl) {
                widgetEl.style.display = config.visible ? 'block' : 'none';
                widgetEl.className = `widget-${widget} widget-position-${config.position}`;
            }
        });

        // Emit event for other components
        window.dispatchEvent(new CustomEvent('preferencesUpdated', {
            detail: this.preferences
        }));
    }

    getFontSize() {
        const sizes = {
            small: '14px',
            medium: '16px',
            large: '18px'
        };
        return sizes[this.preferences.display.fontSize] || sizes.medium;
    }

    getIconForItem(id) {
        const icons = {
            dashboard: 'chart-line',
            portfolio: 'briefcase',
            orders: 'list',
            watchlist: 'star',
            reports: 'file-alt',
            alerts: 'bell'
        };
        return icons[id] || 'circle';
    }

    setupEventListeners() {
        // Listen for theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addListener(e => {
            if (this.preferences.display.theme === 'system') {
                document.body.className = e.matches ? 'dark' : 'light';
            }
        });

        // Listen for font size changes
        document.querySelector('select[name="fontSize"]')?.addEventListener('change', e => {
            this.preferences.display.fontSize = e.target.value;
            this.savePreferences();
        });
    }
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
    window.userPreferences = new UserPreferences();
});
