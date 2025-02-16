class AdminLayout {
    constructor() {
        this.sidebar = document.querySelector('.sidebar');
        this.mainContent = document.querySelector('.main-content');
        this.pageConfigs = {};
        this.initializeLayout();
    }

    initializeLayout() {
        // Load saved layout preferences
        const savedLayout = localStorage.getItem('adminLayout');
        if (savedLayout) {
            this.pageConfigs = JSON.parse(savedLayout);
        }
        
        this.setupDragAndDrop();
        this.setupPageManager();
    }

    setupDragAndDrop() {
        const sidebarItems = document.querySelectorAll('.sidebar-item');
        sidebarItems.forEach(item => {
            item.draggable = true;
            item.addEventListener('dragstart', this.handleDragStart.bind(this));
            item.addEventListener('dragend', this.handleDragEnd.bind(this));
        });
    }

    setupPageManager() {
        const addPageBtn = document.getElementById('add-page-btn');
        if (addPageBtn) {
            addPageBtn.addEventListener('click', () => this.showAddPageModal());
        }
    }

    addNewPage(pageConfig) {
        // Add to sidebar
        const sidebarItem = document.createElement('a');
        sidebarItem.href = `#${pageConfig.id}`;
        sidebarItem.className = 'sidebar-item';
        sidebarItem.innerHTML = `
            <i class="${pageConfig.icon}"></i>
            <span>${pageConfig.title}</span>
            <div class="item-controls">
                <button class="edit-btn"><i class="fas fa-edit"></i></button>
                <button class="move-btn"><i class="fas fa-arrows-alt"></i></button>
            </div>
        `;
        this.sidebar.appendChild(sidebarItem);

        // Create content container
        const contentSection = document.createElement('section');
        contentSection.id = pageConfig.id;
        contentSection.className = 'page-section';
        contentSection.innerHTML = `
            <div class="page-header">
                <h2>${pageConfig.title}</h2>
                <div class="page-controls">
                    <button class="customize-btn">Customize</button>
                    <button class="settings-btn">Settings</button>
                </div>
            </div>
            <div class="page-content">
                ${pageConfig.content || 'New page content goes here'}
            </div>
        `;
        this.mainContent.appendChild(contentSection);

        // Save to config
        this.pageConfigs[pageConfig.id] = pageConfig;
        this.saveLayout();
    }

    showAddPageModal() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h3>Add New Page</h3>
                <form id="new-page-form">
                    <div class="form-group">
                        <label>Page Title</label>
                        <input type="text" name="title" required>
                    </div>
                    <div class="form-group">
                        <label>Icon Class</label>
                        <input type="text" name="icon" placeholder="fas fa-chart-bar">
                    </div>
                    <div class="form-group">
                        <label>Parent Page (Optional)</label>
                        <select name="parent">
                            <option value="">None</option>
                            ${this.getParentPageOptions()}
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Layout Template</label>
                        <select name="template">
                            <option value="blank">Blank Page</option>
                            <option value="dashboard">Dashboard Layout</option>
                            <option value="table">Table Layout</option>
                            <option value="form">Form Layout</option>
                        </select>
                    </div>
                    <div class="modal-buttons">
                        <button type="submit" class="btn-primary">Create Page</button>
                        <button type="button" class="btn-secondary" onclick="this.closest('.modal').remove()">Cancel</button>
                    </div>
                </form>
            </div>
        `;
        document.body.appendChild(modal);

        modal.querySelector('form').addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            this.addNewPage({
                id: this.generatePageId(formData.get('title')),
                title: formData.get('title'),
                icon: formData.get('icon'),
                parent: formData.get('parent'),
                template: formData.get('template')
            });
            modal.remove();
        });
    }

    getParentPageOptions() {
        return Object.entries(this.pageConfigs)
            .map(([id, config]) => `<option value="${id}">${config.title}</option>`)
            .join('');
    }

    generatePageId(title) {
        return title.toLowerCase().replace(/\s+/g, '-');
    }

    handleDragStart(e) {
        e.target.classList.add('dragging');
        e.dataTransfer.setData('text/plain', e.target.id);
    }

    handleDragEnd(e) {
        e.target.classList.remove('dragging');
        this.saveLayout();
    }

    movePageTo(pageId, position) {
        const page = this.pageConfigs[pageId];
        const newOrder = Object.keys(this.pageConfigs);
        const currentIndex = newOrder.indexOf(pageId);
        newOrder.splice(currentIndex, 1);
        newOrder.splice(position, 0, pageId);
        
        const newConfig = {};
        newOrder.forEach(id => {
            newConfig[id] = this.pageConfigs[id];
        });
        this.pageConfigs = newConfig;
        this.saveLayout();
        this.renderSidebar();
    }

    saveLayout() {
        localStorage.setItem('adminLayout', JSON.stringify(this.pageConfigs));
    }

    renderSidebar() {
        this.sidebar.innerHTML = '';
        Object.entries(this.pageConfigs).forEach(([id, config]) => {
            const sidebarItem = document.createElement('a');
            sidebarItem.href = `#${id}`;
            sidebarItem.className = 'sidebar-item';
            sidebarItem.innerHTML = `
                <i class="${config.icon}"></i>
                <span>${config.title}</span>
                <div class="item-controls">
                    <button class="edit-btn"><i class="fas fa-edit"></i></button>
                    <button class="move-btn"><i class="fas fa-arrows-alt"></i></button>
                </div>
            `;
            this.sidebar.appendChild(sidebarItem);
        });
    }
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
    window.adminLayout = new AdminLayout();
});
