class EditorController {
    constructor(editor) {
        this.editor = editor;
        this.currentFile = null;
        this.originalContent = '';
        this.unsavedChanges = false;
    }

    async init() {
        this.initializeEventListeners();
        await this.loadFileList();
    }

    initializeEventListeners() {
        // File search
        document.getElementById('file-search').addEventListener('input', (e) => {
            this.filterFiles(e.target.value);
        });

        // Button actions
        document.getElementById('preview-btn').addEventListener('click', () => {
            this.previewChanges();
        });

        document.getElementById('save-btn').addEventListener('click', () => {
            this.showCommitDialog();
        });

        document.getElementById('history-btn').addEventListener('click', () => {
            this.showVersionHistory();
        });

        // Dialog actions
        document.querySelector('.close-preview').addEventListener('click', () => {
            document.querySelector('.preview-panel').style.display = 'none';
        });

        document.querySelector('.close-history').addEventListener('click', () => {
            document.querySelector('.history-panel').style.display = 'none';
        });

        document.querySelector('.cancel-commit').addEventListener('click', () => {
            document.querySelector('.commit-dialog').style.display = 'none';
        });

        document.querySelector('.confirm-commit').addEventListener('click', () => {
            this.saveChanges();
        });

        // Editor change tracking
        this.editor.onDidChangeModelContent(() => {
            this.unsavedChanges = true;
            this.updateSaveButton();
        });
    }

    async loadFileList() {
        try {
            const response = await fetch('/admin/code-editor/files');
            const files = await response.json();
            this.renderFileTree(files);
        } catch (error) {
            console.error('Error loading file list:', error);
        }
    }

    renderFileTree(files) {
        const tree = document.getElementById('file-tree');
        tree.innerHTML = '';

        const filesByFolder = this.groupFilesByFolder(files);
        this.renderFolderStructure(tree, filesByFolder);
    }

    groupFilesByFolder(files) {
        const structure = {};
        files.forEach(file => {
            const parts = file.path.split('/');
            let current = structure;
            parts.forEach((part, index) => {
                if (index === parts.length - 1) {
                    current[part] = file;
                } else {
                    current[part] = current[part] || {};
                    current = current[part];
                }
            });
        });
        return structure;
    }

    renderFolderStructure(parent, structure, path = '') {
        Object.entries(structure).forEach(([name, value]) => {
            const item = document.createElement('div');
            const fullPath = path ? `${path}/${name}` : name;

            if (value.path) { // File
                item.className = 'file-item';
                item.innerHTML = `
                    <span class="file-icon ${value.type}-icon"></span>
                    <span class="file-name">${name}</span>
                `;
                item.addEventListener('click', () => this.openFile(value.path));
            } else { // Folder
                item.className = 'folder-item';
                item.innerHTML = `
                    <div class="folder-header">
                        <span class="folder-icon"></span>
                        <span class="folder-name">${name}</span>
                    </div>
                    <div class="folder-content"></div>
                `;
                this.renderFolderStructure(
                    item.querySelector('.folder-content'),
                    value,
                    fullPath
                );
            }
            parent.appendChild(item);
        });
    }

    async openFile(path) {
        try {
            const response = await fetch(`/admin/code-editor/file?path=${encodeURIComponent(path)}`);
            const data = await response.json();

            this.currentFile = path;
            this.originalContent = data.content;
            this.unsavedChanges = false;

            // Update editor
            this.editor.setValue(data.content);
            monaco.editor.setModelLanguage(this.editor.getModel(), data.file_type);

            // Update UI
            document.querySelector('.current-file').textContent = path;
            this.updateSaveButton();
        } catch (error) {
            console.error('Error opening file:', error);
        }
    }

    async previewChanges() {
        if (!this.currentFile) return;

        try {
            const response = await fetch('/admin/code-editor/preview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    path: this.currentFile,
                    content: this.editor.getValue()
                })
            });
            const data = await response.json();

            // Show preview panel
            const previewPanel = document.querySelector('.preview-panel');
            const diffView = previewPanel.querySelector('.diff-view');
            const syntaxCheck = previewPanel.querySelector('.syntax-check');

            diffView.innerHTML = this.formatDiff(data.diff);
            syntaxCheck.innerHTML = this.formatSyntaxCheck(data.syntax_check);
            previewPanel.style.display = 'block';
        } catch (error) {
            console.error('Error previewing changes:', error);
        }
    }

    async showVersionHistory() {
        if (!this.currentFile) return;

        try {
            const response = await fetch(`/admin/code-editor/history?path=${encodeURIComponent(this.currentFile)}`);
            const history = await response.json();

            // Show history panel
            const historyPanel = document.querySelector('.history-panel');
            const historyList = historyPanel.querySelector('.history-list');

            historyList.innerHTML = history.map(version => `
                <div class="version-item">
                    <div class="version-header">
                        <span class="commit-hash">${version.commit_hash.slice(0, 7)}</span>
                        <span class="commit-date">${new Date(version.timestamp).toLocaleString()}</span>
                    </div>
                    <div class="commit-message">${version.message}</div>
                    <div class="commit-author">by ${version.author}</div>
                    <button class="rollback-btn" data-hash="${version.commit_hash}">Rollback to this version</button>
                </div>
            `).join('');

            // Add rollback handlers
            historyList.querySelectorAll('.rollback-btn').forEach(btn => {
                btn.addEventListener('click', () => this.rollbackToVersion(btn.dataset.hash));
            });

            historyPanel.style.display = 'block';
        } catch (error) {
            console.error('Error loading version history:', error);
        }
    }

    showCommitDialog() {
        if (!this.unsavedChanges) return;
        document.querySelector('.commit-dialog').style.display = 'block';
    }

    async saveChanges() {
        const message = document.getElementById('commit-message').value;
        if (!message) return;

        try {
            const response = await fetch('/admin/code-editor/file', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    path: this.currentFile,
                    content: this.editor.getValue(),
                    message: message
                })
            });
            const result = await response.json();

            if (result.status === 'success') {
                this.unsavedChanges = false;
                this.originalContent = this.editor.getValue();
                this.updateSaveButton();
                document.querySelector('.commit-dialog').style.display = 'none';
            }
        } catch (error) {
            console.error('Error saving changes:', error);
        }
    }

    async rollbackToVersion(commitHash) {
        if (!confirm('Are you sure you want to rollback to this version? All changes will be lost.')) {
            return;
        }

        try {
            const response = await fetch('/admin/code-editor/rollback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    path: this.currentFile,
                    commit_hash: commitHash
                })
            });
            const result = await response.json();

            if (result.status === 'success') {
                await this.openFile(this.currentFile);
                document.querySelector('.history-panel').style.display = 'none';
            }
        } catch (error) {
            console.error('Error rolling back version:', error);
        }
    }

    filterFiles(search) {
        const items = document.querySelectorAll('.file-item');
        items.forEach(item => {
            const name = item.querySelector('.file-name').textContent;
            item.style.display = name.toLowerCase().includes(search.toLowerCase()) ? 'flex' : 'none';
        });
    }

    updateSaveButton() {
        const saveBtn = document.getElementById('save-btn');
        saveBtn.disabled = !this.unsavedChanges;
        saveBtn.classList.toggle('primary', this.unsavedChanges);
    }

    formatDiff(diff) {
        return diff.map(line => {
            const className = line.startsWith('+') ? 'addition' : 
                            line.startsWith('-') ? 'deletion' : 'context';
            return `<div class="diff-line ${className}">${this.escapeHtml(line)}</div>`;
        }).join('');
    }

    formatSyntaxCheck(check) {
        if (check.valid) {
            return '<div class="syntax-valid">✓ Syntax is valid</div>';
        }
        return `
            <div class="syntax-invalid">
                <div class="error-header">❌ Syntax errors found:</div>
                ${check.errors.map(error => `<div class="error-item">${this.escapeHtml(error)}</div>`).join('')}
            </div>
        `;
    }

    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}
