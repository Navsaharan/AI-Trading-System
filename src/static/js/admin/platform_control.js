class PlatformControl {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.platforms = [];
        this.init();
    }

    async init() {
        // Create UI
        this.createUI();
        
        // Load platforms
        await this.loadPlatforms();
        
        // Start monitoring
        this.startMonitoring();
    }

    createUI() {
        this.container.innerHTML = `
            <div class="platform-control">
                <div class="platform-header">
                    <h2>Trading Platforms</h2>
                    <button class="add-platform-btn">Add Platform</button>
                </div>
                
                <div class="platform-types">
                    <div class="type-section" data-type="stocks">
                        <h3>Stocks</h3>
                        <div class="platform-list"></div>
                    </div>
                    <div class="type-section" data-type="crypto">
                        <h3>Crypto</h3>
                        <div class="platform-list"></div>
                    </div>
                    <div class="type-section" data-type="forex">
                        <h3>Forex</h3>
                        <div class="platform-list"></div>
                    </div>
                    <div class="type-section" data-type="futures">
                        <h3>Futures</h3>
                        <div class="platform-list"></div>
                    </div>
                </div>
                
                <div class="platform-modal" style="display: none;">
                    <div class="modal-content">
                        <h3>Add Trading Platform</h3>
                        <form id="platform-form">
                            <div class="form-group">
                                <label>Platform Name</label>
                                <input type="text" name="name" required>
                            </div>
                            <div class="form-group">
                                <label>Platform Type</label>
                                <select name="platform_type" required>
                                    <option value="stocks">Stocks</option>
                                    <option value="crypto">Crypto</option>
                                    <option value="forex">Forex</option>
                                    <option value="futures">Futures</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Broker Type</label>
                                <select name="broker_type" required>
                                    <option value="api">API</option>
                                    <option value="manual">Manual</option>
                                </select>
                            </div>
                            <div class="credentials-section">
                                <h4>API Credentials</h4>
                                <div class="form-group">
                                    <label>API Key</label>
                                    <input type="text" name="api_key">
                                </div>
                                <div class="form-group">
                                    <label>API Secret</label>
                                    <input type="password" name="api_secret">
                                </div>
                            </div>
                            <div class="form-actions">
                                <button type="submit">Add Platform</button>
                                <button type="button" class="cancel-btn">Cancel</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        `;

        // Add event listeners
        this.container.querySelector('.add-platform-btn')
            .addEventListener('click', () => this.showAddPlatformModal());
        
        this.container.querySelector('.cancel-btn')
            .addEventListener('click', () => this.hideAddPlatformModal());
        
        this.container.querySelector('#platform-form')
            .addEventListener('submit', (e) => this.handleAddPlatform(e));
        
        // Toggle credentials section based on broker type
        this.container.querySelector('select[name="broker_type"]')
            .addEventListener('change', (e) => {
                const credentialsSection = this.container.querySelector('.credentials-section');
                credentialsSection.style.display = e.target.value === 'api' ? 'block' : 'none';
            });
    }

    async loadPlatforms() {
        try {
            const response = await fetch('/api/admin/platforms');
            const platforms = await response.json();
            
            this.platforms = platforms;
            this.renderPlatforms();
            
        } catch (error) {
            console.error('Error loading platforms:', error);
            this.showError('Failed to load platforms');
        }
    }

    renderPlatforms() {
        // Group platforms by type
        const grouped = this.platforms.reduce((acc, platform) => {
            if (!acc[platform.type]) acc[platform.type] = [];
            acc[platform.type].push(platform);
            return acc;
        }, {});

        // Render each type section
        Object.entries(grouped).forEach(([type, platforms]) => {
            const section = this.container.querySelector(`[data-type="${type}"] .platform-list`);
            section.innerHTML = platforms.map(platform => `
                <div class="platform-card ${platform.is_active ? 'active' : ''}"
                     data-name="${platform.name}">
                    <div class="platform-info">
                        <h4>${platform.name}</h4>
                        <span class="broker-type">${platform.broker_type}</span>
                        <span class="status ${platform.is_active ? 'active' : ''}">
                            ${platform.is_active ? 'Active' : 'Inactive'}
                        </span>
                    </div>
                    <div class="platform-assets">
                        ${platform.supported_assets.map(asset => 
                            `<span class="asset-tag">${asset}</span>`
                        ).join('')}
                    </div>
                    <div class="platform-actions">
                        ${!platform.is_active ? `
                            <button class="activate-btn">Activate</button>
                        ` : ''}
                        <button class="remove-btn">Remove</button>
                    </div>
                </div>
            `).join('');

            // Add event listeners
            section.querySelectorAll('.activate-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const card = e.target.closest('.platform-card');
                    this.activatePlatform(card.dataset.name);
                });
            });

            section.querySelectorAll('.remove-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const card = e.target.closest('.platform-card');
                    this.removePlatform(card.dataset.name);
                });
            });
        });
    }

    async activatePlatform(name) {
        try {
            const response = await fetch('/api/admin/platforms/activate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name })
            });

            if (!response.ok) {
                throw new Error('Failed to activate platform');
            }

            // Refresh platforms
            await this.loadPlatforms();
            this.showSuccess('Platform activated successfully');

        } catch (error) {
            console.error('Error activating platform:', error);
            this.showError('Failed to activate platform');
        }
    }

    async handleAddPlatform(e) {
        e.preventDefault();
        
        try {
            const formData = new FormData(e.target);
            const data = {
                name: formData.get('name'),
                platform_type: formData.get('platform_type'),
                broker_type: formData.get('broker_type'),
                credentials: formData.get('broker_type') === 'api' ? {
                    api_key: formData.get('api_key'),
                    api_secret: formData.get('api_secret')
                } : null
            };

            const response = await fetch('/api/admin/platforms/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error('Failed to add platform');
            }

            // Refresh platforms and hide modal
            await this.loadPlatforms();
            this.hideAddPlatformModal();
            this.showSuccess('Platform added successfully');

        } catch (error) {
            console.error('Error adding platform:', error);
            this.showError('Failed to add platform');
        }
    }

    startMonitoring() {
        // Check active platforms every 30 seconds
        setInterval(async () => {
            try {
                const response = await fetch('/api/admin/platforms/active');
                const active = await response.json();
                
                // Update UI to reflect active platforms
                this.updateActivePlatforms(active);
                
            } catch (error) {
                console.error('Error monitoring platforms:', error);
            }
        }, 30000);
    }

    updateActivePlatforms(active) {
        Object.entries(active).forEach(([type, name]) => {
            const section = this.container.querySelector(`[data-type="${type}"]`);
            if (!section) return;

            // Update active status
            section.querySelectorAll('.platform-card').forEach(card => {
                const isActive = card.dataset.name === name;
                card.classList.toggle('active', isActive);
                
                // Update status label
                const status = card.querySelector('.status');
                status.textContent = isActive ? 'Active' : 'Inactive';
                status.className = `status ${isActive ? 'active' : ''}`;
                
                // Toggle activate button
                const activateBtn = card.querySelector('.activate-btn');
                if (activateBtn) {
                    activateBtn.style.display = isActive ? 'none' : 'block';
                }
            });
        });
    }

    showAddPlatformModal() {
        const modal = this.container.querySelector('.platform-modal');
        modal.style.display = 'flex';
    }

    hideAddPlatformModal() {
        const modal = this.container.querySelector('.platform-modal');
        modal.style.display = 'none';
        
        // Reset form
        this.container.querySelector('#platform-form').reset();
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
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

// Initialize platform control
document.addEventListener('DOMContentLoaded', () => {
    const platformControl = new PlatformControl('platform-control-container');
});
