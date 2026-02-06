// API Base URL
const API_BASE = 'http://localhost:8001/api';

// State
let currentDocument = null;
let documents = [];
let editor = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeEditor();
    loadDocuments();
    setupEventListeners();
});

function initializeEditor() {
    const textarea = document.getElementById('markdownEditor');
    editor = CodeMirror.fromTextArea(textarea, {
        mode: 'markdown',
        theme: 'material',
        lineNumbers: true,
        lineWrapping: true,
        autoCloseBrackets: true,
        matchBrackets: true,
        indentUnit: 2
    });
    
    editor.on('change', () => {
        if (currentDocument) {
            currentDocument.content = editor.getValue();
        }
    });
}

function setupEventListeners() {
    // New document button
    document.getElementById('newDocBtn').addEventListener('click', () => {
        document.getElementById('newDocModal').style.display = 'flex';
    });

    // Close modal
    document.getElementById('closeModal').addEventListener('click', closeModal);
    document.getElementById('cancelBtn').addEventListener('click', closeModal);

    // Create document
    document.getElementById('createBtn').addEventListener('click', createNewDocument);

    // Save button
    document.getElementById('saveBtn').addEventListener('click', saveDocument);

    // Preview button
    document.getElementById('previewBtn').addEventListener('click', togglePreview);

    // Delete button
    document.getElementById('deleteBtn').addEventListener('click', deleteDocument);

    // Refresh button
    document.getElementById('refreshBtn').addEventListener('click', loadDocuments);

    // Search
    document.getElementById('searchInput').addEventListener('input', filterDocuments);

    // Tab switching
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            const tabName = e.target.dataset.tab;
            switchTab(tabName);
        });
    });
}

async function loadDocuments() {
    try {
        const response = await fetch(`${API_BASE}/documents`);
        documents = await response.json();
        renderDocumentList();
    } catch (error) {
        console.error('Error loading documents:', error);
        showError('Failed to load documents');
    }
}

function renderDocumentList() {
    const list = document.getElementById('documentList');
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    
    const filtered = documents.filter(doc => 
        doc.path.toLowerCase().includes(searchTerm) ||
        doc.name.toLowerCase().includes(searchTerm)
    );

    if (filtered.length === 0) {
        list.innerHTML = '<div class="loading">No documents found</div>';
        return;
    }

    list.innerHTML = filtered.map(doc => `
        <div class="document-item" data-path="${doc.path}">
            <div class="doc-name">${doc.name}</div>
            <div class="doc-path">${doc.path}</div>
        </div>
    `).join('');

    // Add click listeners
    list.querySelectorAll('.document-item').forEach(item => {
        item.addEventListener('click', () => {
            const path = item.dataset.path;
            loadDocument(path);
        });
    });

    // Highlight active document
    if (currentDocument) {
        const activeItem = list.querySelector(`[data-path="${currentDocument.path}"]`);
        if (activeItem) {
            activeItem.classList.add('active');
        }
    }
}

function filterDocuments() {
    renderDocumentList();
}

async function loadDocument(path) {
    try {
        const response = await fetch(`${API_BASE}/documents/${encodeURIComponent(path)}`);
        if (!response.ok) throw new Error('Failed to load document');
        
        const doc = await response.json();
        currentDocument = doc;
        
        editor.setValue(doc.content);
        document.getElementById('currentFilePath').textContent = doc.path;
        document.getElementById('lastModified').textContent = 
            doc.last_modified ? `Last modified: ${new Date(doc.last_modified).toLocaleString()}` : '';
        
        // Show editor, hide empty state
        document.getElementById('emptyState').style.display = 'none';
        document.getElementById('editorContainer').style.display = 'flex';
        
        // Switch to edit tab
        switchTab('edit');
        
        // Update document list highlighting
        renderDocumentList();
    } catch (error) {
        console.error('Error loading document:', error);
        showError('Failed to load document');
    }
}

async function saveDocument() {
    if (!currentDocument) {
        showError('No document selected');
        return;
    }

    try {
        const content = editor.getValue();
        const response = await fetch(
            `${API_BASE}/documents/${encodeURIComponent(currentDocument.path)}`,
            {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    content: content,
                    title: extractTitle(content)
                })
            }
        );

        if (!response.ok) throw new Error('Failed to save document');

        const updated = await response.json();
        currentDocument = updated;
        document.getElementById('lastModified').textContent = 
            `Last modified: ${new Date(updated.last_modified).toLocaleString()}`;
        
        showSuccess('Document saved and committed to git successfully');
        loadDocuments(); // Refresh list
    } catch (error) {
        console.error('Error saving document:', error);
        showError('Failed to save document');
    }
}

async function createNewDocument() {
    const path = document.getElementById('newDocPath').value.trim();
    const title = document.getElementById('newDocTitle').value.trim();
    const content = document.getElementById('newDocContent').value;

    if (!path) {
        showError('Please provide a document path');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/documents`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                path: path,
                content: content || `# ${title || 'New Document'}\n\nWrite your content here...`,
                title: title
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create document');
        }

        const newDoc = await response.json();
        closeModal();
        showSuccess('Document created and committed to git successfully');
        loadDocuments();
        loadDocument(newDoc.path);
    } catch (error) {
        console.error('Error creating document:', error);
        showError(error.message || 'Failed to create document');
    }
}

async function deleteDocument() {
    if (!currentDocument) {
        showError('No document selected');
        return;
    }

    if (!confirm(`Are you sure you want to delete "${currentDocument.path}"?`)) {
        return;
    }

    try {
        const response = await fetch(
            `${API_BASE}/documents/${encodeURIComponent(currentDocument.path)}`,
            { method: 'DELETE' }
        );

        if (!response.ok) throw new Error('Failed to delete document');

        const result = await response.json();
        const gitStatus = result.git_status ? ` (${result.git_status})` : '';
        showSuccess(`Document deleted and committed to git successfully${gitStatus}`);
        currentDocument = null;
        document.getElementById('emptyState').style.display = 'flex';
        document.getElementById('editorContainer').style.display = 'none';
        loadDocuments();
    } catch (error) {
        console.error('Error deleting document:', error);
        showError('Failed to delete document');
    }
}

function togglePreview() {
    const editTab = document.querySelector('[data-tab="edit"]');
    const previewTab = document.querySelector('[data-tab="preview"]');
    const editorPane = document.getElementById('editorPane');
    const previewPane = document.getElementById('previewPane');

    if (previewPane.style.display === 'none') {
        // Show preview
        const content = editor.getValue();
        previewPane.innerHTML = marked.parse(content);
        editorPane.style.display = 'none';
        previewPane.style.display = 'block';
        editTab.classList.remove('active');
        previewTab.classList.add('active');
    } else {
        // Show editor
        editorPane.style.display = 'block';
        previewPane.style.display = 'none';
        editTab.classList.add('active');
        previewTab.classList.remove('active');
    }
}

function switchTab(tabName) {
    const editTab = document.querySelector('[data-tab="edit"]');
    const previewTab = document.querySelector('[data-tab="preview"]');
    const editorPane = document.getElementById('editorPane');
    const previewPane = document.getElementById('previewPane');

    if (tabName === 'preview') {
        const content = editor.getValue();
        previewPane.innerHTML = marked.parse(content);
        editorPane.style.display = 'none';
        previewPane.style.display = 'block';
        editTab.classList.remove('active');
        previewTab.classList.add('active');
    } else {
        editorPane.style.display = 'block';
        previewPane.style.display = 'none';
        editTab.classList.add('active');
        previewTab.classList.remove('active');
    }
}

function closeModal() {
    document.getElementById('newDocModal').style.display = 'none';
    document.getElementById('newDocPath').value = '';
    document.getElementById('newDocTitle').value = '';
    document.getElementById('newDocContent').value = '';
}

function extractTitle(content) {
    const match = content.match(/^#\s+(.+)$/m);
    return match ? match[1] : null;
}

function showError(message) {
    alert(`Error: ${message}`);
}

function showSuccess(message) {
    // You can replace this with a toast notification
    console.log(`Success: ${message}`);
}
