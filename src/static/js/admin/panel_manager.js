// Admin Panel Manager
class AdminPanelManager {
    constructor() {
        this.initialized = false;
        this.currentLayout = {};
        this.defaultLayout = {};
        this.draggedItem = null;
        this.darkMode = false;
    }

    async initialize() {
        if (this.initialized) return;
        
        // Load layouts
        await this.loadLayouts();
        
        // Initialize UI
        this.initializeUI();
        
        // Setup event listeners
        this.setupEventListeners();
        
        this.initialized = true;
    }

    async loadLayouts() {
        try {
            // Load current layout
            const response = await fetch('/api/admin/layout');
            this.currentLayout = await response.json();
            
            // Load default layout
            const defaultResponse = await fetch('/api/admin/default-layout');
            this.defaultLayout = await defaultResponse.json();
            
        } catch (error) {
            console.error('Error loading layouts:', error);
            this.currentLayout = this.getDefaultLayout();
            this.defaultLayout = this.getDefaultLayout();
        }
    }

    getDefaultLayout() {
        return {
            pages: [
                {
                    id: 'dashboard',
                    title: 'Dashboard',
                    icon: 'dashboard',
                    order: 1,
                    visible: true,
                    sections: [
                        {
                            id: 'overview',
                            title: 'Overview',
                            order: 1,
                            options: [
                                {
                                    id: 'performance',
                                    title: 'Performance Metrics',
                                    type: 'widget'
                                }
                            ]
                        }
                    ]
                },
                {
                    id: 'trading',
                    title: 'Trading',
                    icon: 'trending_up',
                    order: 2,
                    visible: true,
                    sections: [
                        {
                            id: 'allocations',
                            title: 'Trading Allocations',
                            order: 1,
                            options: [
                                {
                                    id: 'hft_settings',
                                    title: 'HFT Settings',
                                    type: 'settings'
                                }
                            ]
                        }
                    ]
                }
            ],
            sidebar: {
                visible: true,
                expanded: true
            }
        };
    }

    initializeUI() {
        // Create main container
        const container = document.createElement('div');
        container.id = 'admin-panel-container';
        container.className = 'admin-panel';
        
        // Add panel content
        container.innerHTML = this.generatePanelHTML();
        
        // Add to document
        document.getElementById('admin-content').appendChild(container);
        
        // Initialize Sortable.js for drag & drop
        this.initializeSortable();
    }

    generatePanelHTML() {
        return `
            <div class="admin-header">
                <h2>Admin Panel Customization</h2>
                <div class="admin-actions">
                    <button id="save-layout" class="btn-primary">
                        <i class="material-icons">save</i> Save Layout
                    </button>
                    <button id="reset-layout" class="btn-secondary">
                        <i class="material-icons">restore</i> Reset to Default
                    </button>
                    <button id="toggle-dark-mode" class="btn-icon">
                        <i class="material-icons">dark_mode</i>
                    </button>
                </div>
            </div>

            <div class="admin-content">
                <div class="pages-container">
                    ${this.generatePagesHTML()}
                </div>
                
                <div class="sidebar-preview">
                    <h3>Sidebar Preview</h3>
                    ${this.generateSidebarHTML()}
                </div>
            </div>

            <div class="new-page-creator">
                <h3>Create New Page</h3>
                <div class="page-creator-form">
                    <input type="text" id="new-page-title" placeholder="Page Title">
                    <input type="text" id="new-page-icon" placeholder="Material Icon Name">
                    <button id="create-page" class="btn-primary">
                        <i class="material-icons">add</i> Create Page
                    </button>
                </div>
            </div>
        `;
    }

    generatePagesHTML() {
        return this.currentLayout.pages.map(page => `
            <div class="page-card" data-id="${page.id}">
                <div class="page-header" draggable="true">
                    <i class="material-icons">${page.icon}</i>
                    <span>${page.title}</span>
                    <div class="page-actions">
                        <button class="btn-icon toggle-visibility" 
                                data-visible="${page.visible}">
                            <i class="material-icons">
                                ${page.visible ? 'visibility' : 'visibility_off'}
                            </i>
                        </button>
                        <button class="btn-icon edit-page">
                            <i class="material-icons">edit</i>
                        </button>
                        <button class="btn-icon delete-page">
                            <i class="material-icons">delete</i>
                        </button>
                    </div>
                </div>
                
                <div class="page-sections">
                    ${this.generateSectionsHTML(page.sections)}
                </div>
                
                <button class="add-section btn-secondary">
                    <i class="material-icons">add</i> Add Section
                </button>
            </div>
        `).join('');
    }

    generateSectionsHTML(sections) {
        return sections.map(section => `
            <div class="section-card" data-id="${section.id}">
                <div class="section-header" draggable="true">
                    <span>${section.title}</span>
                    <div class="section-actions">
                        <button class="btn-icon edit-section">
                            <i class="material-icons">edit</i>
                        </button>
                        <button class="btn-icon delete-section">
                            <i class="material-icons">delete</i>
                        </button>
                    </div>
                </div>
                
                <div class="section-options">
                    ${this.generateOptionsHTML(section.options)}
                </div>
                
                <button class="add-option btn-secondary">
                    <i class="material-icons">add</i> Add Option
                </button>
            </div>
        `).join('');
    }

    generateOptionsHTML(options) {
        return options.map(option => `
            <div class="option-card" data-id="${option.id}" draggable="true">
                <i class="material-icons">${this.getOptionIcon(option.type)}</i>
                <span>${option.title}</span>
                <div class="option-actions">
                    <button class="btn-icon move-option">
                        <i class="material-icons">open_with</i>
                    </button>
                    <button class="btn-icon edit-option">
                        <i class="material-icons">edit</i>
                    </button>
                    <button class="btn-icon delete-option">
                        <i class="material-icons">delete</i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    generateSidebarHTML() {
        return `
            <div class="sidebar-preview-content">
                ${this.currentLayout.pages
                    .filter(page => page.visible)
                    .sort((a, b) => a.order - b.order)
                    .map(page => `
                        <div class="sidebar-item">
                            <i class="material-icons">${page.icon}</i>
                            <span>${page.title}</span>
                        </div>
                    `).join('')}
            </div>
        `;
    }

    initializeSortable() {
        // Initialize Sortable.js for pages
        new Sortable(document.querySelector('.pages-container'), {
            animation: 150,
            handle: '.page-header',
            onEnd: (evt) => this.handlePageReorder(evt)
        });

        // Initialize Sortable.js for sections
        document.querySelectorAll('.page-sections').forEach(el => {
            new Sortable(el, {
                animation: 150,
                handle: '.section-header',
                onEnd: (evt) => this.handleSectionReorder(evt)
            });
        });

        // Initialize Sortable.js for options
        document.querySelectorAll('.section-options').forEach(el => {
            new Sortable(el, {
                animation: 150,
                group: 'options',
                onEnd: (evt) => this.handleOptionReorder(evt)
            });
        });
    }

    setupEventListeners() {
        // Save layout
        document.getElementById('save-layout')
            .addEventListener('click', () => this.saveLayout());
        
        // Reset layout
        document.getElementById('reset-layout')
            .addEventListener('click', () => this.resetLayout());
        
        // Toggle dark mode
        document.getElementById('toggle-dark-mode')
            .addEventListener('click', () => this.toggleDarkMode());
        
        // Create new page
        document.getElementById('create-page')
            .addEventListener('click', () => this.createNewPage());
        
        // Page visibility toggles
        document.querySelectorAll('.toggle-visibility')
            .forEach(btn => {
                btn.addEventListener('click', (e) => 
                    this.togglePageVisibility(e.target.closest('.page-card'))
                );
            });
        
        // Edit buttons
        document.querySelectorAll('.edit-page')
            .forEach(btn => {
                btn.addEventListener('click', (e) => 
                    this.editPage(e.target.closest('.page-card'))
                );
            });
        
        // Delete buttons
        document.querySelectorAll('.delete-page')
            .forEach(btn => {
                btn.addEventListener('click', (e) => 
                    this.deletePage(e.target.closest('.page-card'))
                );
            });
        
        // Add section buttons
        document.querySelectorAll('.add-section')
            .forEach(btn => {
                btn.addEventListener('click', (e) => 
                    this.addSection(e.target.closest('.page-card'))
                );
            });
        
        // Add option buttons
        document.querySelectorAll('.add-option')
            .forEach(btn => {
                btn.addEventListener('click', (e) => 
                    this.addOption(e.target.closest('.section-card'))
                );
            });
    }

    async saveLayout() {
        try {
            const response = await fetch('/api/admin/layout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.currentLayout)
            });
            
            if (response.ok) {
                this.showSuccess('Layout saved successfully!');
            } else {
                throw new Error('Failed to save layout');
            }
            
        } catch (error) {
            this.showError('Error saving layout: ' + error.message);
        }
    }

    async resetLayout() {
        if (confirm('Are you sure you want to reset to the default layout?')) {
            this.currentLayout = JSON.parse(JSON.stringify(this.defaultLayout));
            this.initializeUI();
            await this.saveLayout();
        }
    }

    toggleDarkMode() {
        this.darkMode = !this.darkMode;
        document.body.classList.toggle('dark-mode', this.darkMode);
    }

    async createNewPage() {
        const title = document.getElementById('new-page-title').value;
        const icon = document.getElementById('new-page-icon').value;
        
        if (!title || !icon) {
            this.showError('Please provide both title and icon');
            return;
        }
        
        const newPage = {
            id: this.generateId(),
            title,
            icon,
            order: this.currentLayout.pages.length + 1,
            visible: true,
            sections: []
        };
        
        this.currentLayout.pages.push(newPage);
        this.initializeUI();
        await this.saveLayout();
    }

    // Helper methods
    getOptionIcon(type) {
        const icons = {
            'widget': 'widgets',
            'settings': 'settings',
            'chart': 'insert_chart',
            'table': 'table_chart'
        };
        return icons[type] || 'extension';
    }

    generateId() {
        return 'id_' + Math.random().toString(36).substr(2, 9);
    }

    showSuccess(message) {
        // Implement success notification
        console.log('Success:', message);
    }

    showError(message) {
        // Implement error notification
        console.error('Error:', message);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    const panelManager = new AdminPanelManager();
    panelManager.initialize();
});
