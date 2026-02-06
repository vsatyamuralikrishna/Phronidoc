// API Base URL
const API_BASE = 'http://localhost:8001/api';

// State
let currentDocument = null;
let documents = [];
let sections = null;
let editor = null;
let isEditMode = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeEditor();
    loadSections();
    loadDocuments();
    setupEventListeners();
});

function initializeEditor() {
    const textarea = document.getElementById('markdownEditor');
    if (textarea) {
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
}

function setupEventListeners() {
    // New section button
    const newSectionBtn = document.getElementById('newSectionBtn');
    if (newSectionBtn) {
        newSectionBtn.addEventListener('click', () => {
            document.getElementById('newSectionModal').style.display = 'flex';
        });
    }

    // Empty state buttons
    const emptyNewSectionBtn = document.getElementById('emptyNewSectionBtn');
    if (emptyNewSectionBtn) {
        emptyNewSectionBtn.addEventListener('click', () => {
            document.getElementById('newSectionModal').style.display = 'flex';
        });
    }

    const emptyNewDocBtn = document.getElementById('emptyNewDocBtn');
    if (emptyNewDocBtn) {
        emptyNewDocBtn.addEventListener('click', async () => {
            await loadSections();
            populateSectionSelectors();
            document.getElementById('newDocModal').style.display = 'flex';
        });
    }

    // New subsection button
    const newSubsectionBtn = document.getElementById('newSubsectionBtn');
    if (newSubsectionBtn) {
        newSubsectionBtn.addEventListener('click', () => {
            populateParentSectionSelector();
            document.getElementById('newSubsectionModal').style.display = 'flex';
        });
    }

    // New document button
    const newDocBtn = document.getElementById('newDocBtn');
    if (newDocBtn) {
        newDocBtn.addEventListener('click', async () => {
            await loadSections();
            populateSectionSelectors();
            document.getElementById('newDocModal').style.display = 'flex';
            
            // Add listeners for path updates
            const docSection = document.getElementById('docSection');
            const docSubsection = document.getElementById('docSubsection');
            const newDocTitle = document.getElementById('newDocTitle');
            
            if (docSection) {
                docSection.addEventListener('change', updateDocPath);
            }
            if (docSubsection) {
                docSubsection.addEventListener('change', updateDocPath);
            }
            if (newDocTitle) {
                newDocTitle.addEventListener('input', updateDocPath);
            }
        });
    }

    // Section modals
    const closeSectionModal = document.getElementById('closeSectionModal');
    if (closeSectionModal) {
        closeSectionModal.addEventListener('click', () => {
            document.getElementById('newSectionModal').style.display = 'none';
            document.getElementById('sectionName').value = '';
        });
    }
    
    const cancelSectionBtn = document.getElementById('cancelSectionBtn');
    if (cancelSectionBtn) {
        cancelSectionBtn.addEventListener('click', () => {
            document.getElementById('newSectionModal').style.display = 'none';
            document.getElementById('sectionName').value = '';
        });
    }
    
    const createSectionBtn = document.getElementById('createSectionBtn');
    if (createSectionBtn) {
        createSectionBtn.addEventListener('click', createSection);
    }

    // Sub-section modals
    const closeSubsectionModal = document.getElementById('closeSubsectionModal');
    if (closeSubsectionModal) {
        closeSubsectionModal.addEventListener('click', () => {
            document.getElementById('newSubsectionModal').style.display = 'none';
            document.getElementById('parentSection').value = '';
            document.getElementById('subsectionName').value = '';
        });
    }
    
    const cancelSubsectionBtn = document.getElementById('cancelSubsectionBtn');
    if (cancelSubsectionBtn) {
        cancelSubsectionBtn.addEventListener('click', () => {
            document.getElementById('newSubsectionModal').style.display = 'none';
            document.getElementById('parentSection').value = '';
            document.getElementById('subsectionName').value = '';
        });
    }
    
    const createSubsectionBtn = document.getElementById('createSubsectionBtn');
    if (createSubsectionBtn) {
        createSubsectionBtn.addEventListener('click', createSubsection);
    }

    // Document modals
    const closeModal = document.getElementById('closeModal');
    if (closeModal) {
        closeModal.addEventListener('click', () => {
            document.getElementById('newDocModal').style.display = 'none';
            document.getElementById('newDocPath').value = '';
            document.getElementById('newDocTitle').value = '';
            document.getElementById('newDocContent').value = '';
        });
    }
    
    const cancelBtn = document.getElementById('cancelBtn');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
            document.getElementById('newDocModal').style.display = 'none';
            document.getElementById('newDocPath').value = '';
            document.getElementById('newDocTitle').value = '';
            document.getElementById('newDocContent').value = '';
        });
    }
    
    const createBtn = document.getElementById('createBtn');
    if (createBtn) {
        createBtn.addEventListener('click', createNewDocument);
    }

    // Edit toggle
    const editToggleBtn = document.getElementById('editToggleBtn');
    if (editToggleBtn) {
        editToggleBtn.addEventListener('click', toggleEditMode);
    }

    // Save button
    const saveBtn = document.getElementById('saveBtn');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveDocument);
    }

    // Delete button
    const deleteBtn = document.getElementById('deleteBtn');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', deleteDocument);
    }

    // Refresh button
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            loadSections();
            loadDocuments();
        });
    }

    // Navigation search
    const navSearchInput = document.getElementById('navSearchInput');
    if (navSearchInput) {
        navSearchInput.addEventListener('input', filterNavigation);
    }
}

async function loadSections() {
    try {
        // Load both sections structure and navigation
        const [sectionsResponse, navResponse] = await Promise.all([
            fetch(`${API_BASE}/sections`),
            fetch(`${API_BASE}/navigation`)
        ]);
        
        if (!sectionsResponse.ok) {
            throw new Error(`HTTP ${sectionsResponse.status}: ${sectionsResponse.statusText}`);
        }
        
        sections = await sectionsResponse.json();
        let navigation = null;
        
        if (navResponse.ok) {
            const navData = await navResponse.json();
            navigation = navData.navigation || [];
        }
        
        renderNavigation(navigation);
        return sections;
    } catch (error) {
        console.error('Error loading sections:', error);
        showError(`Failed to load sections: ${error.message}`);
        return null;
    }
}

async function loadDocuments() {
    try {
        const response = await fetch(`${API_BASE}/documents`);
        documents = await response.json();
        renderNavigation(); // Re-render to include all documents
    } catch (error) {
        console.error('Error loading documents:', error);
        showError('Failed to load documents');
    }
}

function renderNavigation(navigation = null) {
    const navTree = document.getElementById('navTree');
    if (!navTree) return;
    
    // If we have navigation from mkdocs.yml, use that for hierarchical display
    if (navigation && navigation.length > 0) {
        renderNavigationFromMkdocs(navTree, navigation);
        return;
    }
    
    // Fallback to sections structure
    if (!sections || !sections.sections || sections.sections.length === 0) {
        navTree.innerHTML = '<div class="loading">No sections yet. Create one to get started!</div>';
        return;
    }
    
    let html = '';
    
    sections.sections.forEach(section => {
        // Section header
        html += `
            <div class="nav-item">
                <div class="nav-item-link section" data-section="${section.name}">
                    <span class="nav-item-icon">📁</span>
                    <span class="nav-item-text">${section.name}</span>
                    <button class="nav-item-action" data-section="${section.name}" title="Create sub-section">+</button>
                </div>
            </div>
        `;
        
        // Sub-sections
        if (section.subsections && section.subsections.length > 0) {
            section.subsections.forEach(subsection => {
                const cleanSubName = subsection.name
                    .replace(/[-_]/g, ' ')
                    .split(' ')
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
                    .join(' ');
                
                html += `
                    <div class="nav-item">
                        <div class="nav-item-link subsection" data-path="${subsection.path}">
                            <span class="nav-item-icon">📂</span>
                            <span class="nav-item-text">${cleanSubName}</span>
                        </div>
                    </div>
                `;
                
                // Documents in sub-section
                if (subsection.documents && subsection.documents.length > 0) {
                    subsection.documents.forEach(doc => {
                        const cleanName = getCleanDocumentName(doc.name, doc.path);
                        html += `
                            <div class="nav-item">
                                <div class="nav-item-link document" data-path="${doc.path}">
                                    <span class="nav-item-icon">📄</span>
                                    <span class="nav-item-text">${cleanName}</span>
                                </div>
                            </div>
                        `;
                    });
                }
            });
        }
        
        // Documents in section root
        if (section.documents && section.documents.length > 0) {
            section.documents.forEach(doc => {
                const cleanName = getCleanDocumentName(doc.name, doc.path);
                html += `
                    <div class="nav-item">
                        <div class="nav-item-link document" data-path="${doc.path}">
                            <span class="nav-item-icon">📄</span>
                            <span class="nav-item-text">${cleanName}</span>
                        </div>
                    </div>
                `;
            });
        }
    });
    
    navTree.innerHTML = html;
    attachNavigationListeners(navTree);
}

function renderNavigationFromMkdocs(navTree, navigation) {
    let html = '';
    
    function renderNavItem(item, level = 0) {
        if (typeof item === 'string') {
            // Simple string path
            const cleanName = getCleanDocumentName(item.split('/').pop(), item);
            html += `
                <div class="nav-item">
                    <div class="nav-item-link document" data-path="${item}" style="padding-left: ${16 + level * 24}px;">
                        <span class="nav-item-icon">📄</span>
                        <span class="nav-item-text">${cleanName}</span>
                    </div>
                </div>
            `;
        } else if (typeof item === 'object') {
            // Object with title and children
            Object.entries(item).forEach(([title, value]) => {
                if (Array.isArray(value)) {
                    // Section with children
                    html += `
                        <div class="nav-item">
                            <div class="nav-item-link section" data-section="${title.toLowerCase().replace(/\s+/g, '-')}" style="padding-left: ${16 + level * 24}px;">
                                <span class="nav-item-icon">📁</span>
                                <span class="nav-item-text">${title}</span>
                                <button class="nav-item-action" data-section="${title.toLowerCase().replace(/\s+/g, '-')}" title="Create sub-section">+</button>
                            </div>
                        </div>
                    `;
                    // Render children
                    value.forEach(child => renderNavItem(child, level + 1));
                } else if (typeof value === 'string') {
                    // Single document
                    const cleanName = getCleanDocumentName(value.split('/').pop(), value);
                    html += `
                        <div class="nav-item">
                            <div class="nav-item-link document" data-path="${value}" style="padding-left: ${16 + level * 24}px;">
                                <span class="nav-item-icon">📄</span>
                                <span class="nav-item-text">${title}</span>
                            </div>
                        </div>
                    `;
                }
            });
        }
    }
    
    navigation.forEach(item => renderNavItem(item, 0));
    
    navTree.innerHTML = html;
    attachNavigationListeners(navTree);
}

function attachNavigationListeners(navTree) {
    // Add click listeners
    navTree.querySelectorAll('.nav-item-link').forEach(link => {
        link.addEventListener('click', (e) => {
            // Don't trigger if clicking the action button
            if (e.target.classList.contains('nav-item-action')) {
                return;
            }
            
            const path = link.dataset.path;
            const section = link.dataset.section;
            
            if (path) {
                // Remove active from all
                navTree.querySelectorAll('.nav-item-link').forEach(l => l.classList.remove('active'));
                // Add active to clicked
                link.classList.add('active');
                loadDocument(path);
            } else if (section) {
                // Section clicked - load index
                const sectionPath = `${section}/index.md`;
                navTree.querySelectorAll('.nav-item-link').forEach(l => l.classList.remove('active'));
                link.classList.add('active');
                loadDocument(sectionPath);
            }
        });
    });
    
    // Add click listeners for subsection creation buttons
    navTree.querySelectorAll('.nav-item-action').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.stopPropagation();
            e.preventDefault();
            const sectionName = btn.dataset.section;
            if (sectionName) {
                if (!sections) {
                    await loadSections();
                }
                populateParentSectionSelector();
                setTimeout(() => {
                    const parentSectionSelect = document.getElementById('parentSection');
                    if (parentSectionSelect) {
                        parentSectionSelect.value = sectionName;
                    }
                    document.getElementById('newSubsectionModal').style.display = 'flex';
                }, 50);
            }
        });
    });
}

function filterNavigation() {
    const searchTerm = document.getElementById('navSearchInput').value.toLowerCase();
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        const text = item.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}

function getCleanDocumentName(filename, path) {
    let cleanName = filename.replace(/\.md$/, '');
    cleanName = cleanName.replace(/[-_]/g, ' ');
    cleanName = cleanName.split(' ').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
    ).join(' ');
    
    if (filename === 'index.md' && path) {
        const pathParts = path.split('/');
        if (pathParts.length > 1) {
            const parentName = pathParts[pathParts.length - 2];
            return parentName.charAt(0).toUpperCase() + parentName.slice(1);
        }
    }
    
    return cleanName;
}

async function createSection() {
    const sectionNameInput = document.getElementById('sectionName');
    if (!sectionNameInput) {
        showError('Section name input not found');
        return;
    }
    
    const sectionName = sectionNameInput.value.trim();
    
    if (!sectionName) {
        showError('Please provide a section name');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/sections`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: sectionName,
                push: true
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }));
            throw new Error(errorData.detail || `Failed to create section: ${response.statusText}`);
        }
        
        const result = await response.json();
        closeSectionModal();
        
        if (result.git_error) {
            showSuccess(`Section "${sectionName}" created, but git commit failed: ${result.git_status}`);
        } else {
            showSuccess(`Section "${sectionName}" created successfully! ${result.git_status || ''}`);
        }
        
        await loadSections();
        await loadDocuments();
    } catch (error) {
        console.error('Error creating section:', error);
        showError(error.message || 'Failed to create section. Check console for details.');
    }
}

async function createSubsection() {
    const parentSection = document.getElementById('parentSection').value;
    const subsectionName = document.getElementById('subsectionName').value.trim();
    
    if (!parentSection) {
        showError('Please select a parent section');
        return;
    }
    
    if (!subsectionName) {
        showError('Please provide a sub-section name');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/sections/${encodeURIComponent(parentSection)}/subsections`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: subsectionName,
                push: true
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }));
            throw new Error(errorData.detail || `Failed to create sub-section: ${response.statusText}`);
        }
        
        const result = await response.json();
        closeSubsectionModal();
        
        if (result.git_error) {
            showSuccess(`Sub-section created, but git commit failed: ${result.git_status}`);
        } else {
            showSuccess(`Sub-section created successfully! ${result.git_status || ''}`);
        }
        
        await loadSections();
        await loadDocuments();
    } catch (error) {
        console.error('Error creating sub-section:', error);
        showError(error.message || 'Failed to create sub-section. Check console for details.');
    }
}

function populateSectionSelectors() {
    const docSection = document.getElementById('docSection');
    const docSubsection = document.getElementById('docSubsection');
    
    if (!docSection) return;
    
    docSection.innerHTML = '<option value="">Select a section...</option>';
    if (docSubsection) {
        docSubsection.innerHTML = '<option value="">None (root of section)</option>';
    }
    
    // Remove old event listener by cloning
    const newDocSection = docSection.cloneNode(true);
    docSection.parentNode.replaceChild(newDocSection, docSection);
    
    if (sections && sections.sections) {
        sections.sections.forEach(section => {
            const option = document.createElement('option');
            option.value = section.name;
            option.textContent = section.name;
            newDocSection.appendChild(option);
        });
    }
    
    // Update subsection when section changes
    newDocSection.addEventListener('change', () => {
        const selectedSection = newDocSection.value;
        const docSubsection = document.getElementById('docSubsection');
        if (docSubsection) {
            docSubsection.innerHTML = '<option value="">None (root of section)</option>';
            
            if (selectedSection && sections) {
                const section = sections.sections.find(s => s.name === selectedSection);
                if (section && section.subsections) {
                    section.subsections.forEach(subsection => {
                        const option = document.createElement('option');
                        option.value = subsection.name;
                        option.textContent = subsection.name;
                        docSubsection.appendChild(option);
                    });
                }
            }
        }
        updateDocPath();
    });
}

function populateParentSectionSelector() {
    const parentSection = document.getElementById('parentSection');
    if (!parentSection) return;
    
    parentSection.innerHTML = '<option value="">Select a section...</option>';
    
    if (sections && sections.sections) {
        sections.sections.forEach(section => {
            const option = document.createElement('option');
            option.value = section.name;
            option.textContent = section.name;
            parentSection.appendChild(option);
        });
    }
}

function updateDocPath() {
    const sectionEl = document.getElementById('docSection');
    const subsectionEl = document.getElementById('docSubsection');
    const titleEl = document.getElementById('newDocTitle');
    const pathEl = document.getElementById('newDocPath');
    
    if (!sectionEl || !pathEl) return;
    
    const section = sectionEl.value;
    const subsection = subsectionEl ? subsectionEl.value : '';
    const title = titleEl ? titleEl.value.trim() : '';
    
    let path = '';
    if (section) {
        path = section;
        if (subsection) {
            path += `/${subsection}`;
        }
        
        if (title) {
            const filename = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
            path += `/${filename}.md`;
        } else {
            path += '/new-document.md';
        }
    }
    
    pathEl.value = path;
}

function closeSectionModal() {
    document.getElementById('newSectionModal').style.display = 'none';
    document.getElementById('sectionName').value = '';
}

function closeSubsectionModal() {
    document.getElementById('newSubsectionModal').style.display = 'none';
    document.getElementById('parentSection').value = '';
    document.getElementById('subsectionName').value = '';
}

async function loadDocument(path) {
    try {
        const response = await fetch(`${API_BASE}/documents/${encodeURIComponent(path)}`);
        if (!response.ok) throw new Error('Failed to load document');
        
        const doc = await response.json();
        currentDocument = doc;
        
        // Extract title from content
        const titleMatch = doc.content.match(/^#\s+(.+)$/m);
        const docTitle = titleMatch ? titleMatch[1] : getCleanDocumentName(path.split('/').pop(), path);
        
        // Update UI
        document.getElementById('docTitle').textContent = docTitle;
        document.getElementById('docPath').textContent = doc.path;
        document.getElementById('docModified').textContent = 
            doc.last_modified ? `Last modified: ${new Date(doc.last_modified).toLocaleString()}` : '';
        
        // Set editor content
        if (editor) {
            editor.setValue(doc.content);
        }
        
        // Show preview (default view)
        showPreview(doc.content);
        
        // Show document container, hide empty state
        document.getElementById('emptyState').style.display = 'none';
        document.getElementById('documentContainer').style.display = 'block';
        
        // Update active nav item
        document.querySelectorAll('.nav-item-link').forEach(link => {
            if (link.dataset.path === path) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
        
        // Reset to preview mode
        isEditMode = false;
        updateEditModeUI();
    } catch (error) {
        console.error('Error loading document:', error);
        showError('Failed to load document');
    }
}

function showPreview(content) {
    const previewView = document.getElementById('previewView');
    const editView = document.getElementById('editView');
    const previewContent = document.getElementById('previewContent');
    
    if (previewView && previewContent) {
        previewContent.innerHTML = marked.parse(content);
        previewView.style.display = 'block';
        if (editView) {
            editView.style.display = 'none';
        }
        
        // Make links clickable
        makePreviewLinksClickable(previewContent, currentDocument ? currentDocument.path : '');
    }
}

function toggleEditMode() {
    isEditMode = !isEditMode;
    
    const previewView = document.getElementById('previewView');
    const editView = document.getElementById('editView');
    
    if (isEditMode) {
        // Show editor
        if (previewView) previewView.style.display = 'none';
        if (editView) editView.style.display = 'block';
        
        // Update content from editor
        if (editor && currentDocument) {
            const content = editor.getValue();
            currentDocument.content = content;
        }
    } else {
        // Show preview
        if (editView) editView.style.display = 'none';
        if (previewView) previewView.style.display = 'block';
        
        // Update preview with latest content
        if (editor && currentDocument) {
            const content = editor.getValue();
            showPreview(content);
        }
    }
    
    updateEditModeUI();
}

function updateEditModeUI() {
    const editToggleBtn = document.getElementById('editToggleBtn');
    const saveBtn = document.getElementById('saveBtn');
    const deleteBtn = document.getElementById('deleteBtn');
    
    if (isEditMode) {
        if (editToggleBtn) editToggleBtn.textContent = '👁️ Preview';
        if (saveBtn) saveBtn.style.display = 'inline-block';
        if (deleteBtn) deleteBtn.style.display = 'inline-block';
    } else {
        if (editToggleBtn) editToggleBtn.textContent = '✏️ Edit';
        if (saveBtn) saveBtn.style.display = 'none';
        if (deleteBtn) deleteBtn.style.display = 'none';
    }
}

function makePreviewLinksClickable(previewPane, currentPath) {
    const links = previewPane.querySelectorAll('a[href]');
    
    links.forEach(link => {
        const href = link.getAttribute('href');
        
        // Skip external links
        if (href.startsWith('http://') || href.startsWith('https://') || href.startsWith('mailto:')) {
            return;
        }
        
        // Handle relative markdown links
        if (href.startsWith('./') || href.startsWith('../') || (!href.startsWith('/') && !href.startsWith('#'))) {
            const currentDir = currentPath.substring(0, currentPath.lastIndexOf('/'));
            let targetPath = href;
            
            if (targetPath.startsWith('./')) {
                targetPath = targetPath.substring(2);
            }
            
            if (targetPath.startsWith('../')) {
                const parts = currentDir.split('/');
                let levels = 0;
                while (targetPath.startsWith('../')) {
                    targetPath = targetPath.substring(3);
                    levels++;
                }
                const parentParts = parts.slice(0, -levels);
                targetPath = parentParts.join('/') + '/' + targetPath;
            } else if (currentDir) {
                targetPath = currentDir + '/' + targetPath;
            }
            
            targetPath = targetPath.replace(/\/$/, '');
            if (!targetPath.endsWith('.md')) {
                targetPath = targetPath + '/index.md';
            }
            targetPath = targetPath.replace(/^\//, '');
            
            link.style.cursor = 'pointer';
            link.style.color = 'var(--primary-color)';
            
            link.addEventListener('click', (e) => {
                e.preventDefault();
                loadDocument(targetPath);
            });
        } else if (href.startsWith('#')) {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const anchor = href.substring(1);
                const element = previewPane.querySelector(`#${anchor}`) || 
                               previewPane.querySelector(`[id="${anchor}"]`);
                if (element) {
                    element.scrollIntoView({ behavior: 'smooth' });
                }
            });
        }
    });
}

async function saveDocument() {
    if (!currentDocument) {
        showError('No document selected');
        return;
    }

    try {
        const content = editor ? editor.getValue() : currentDocument.content;
        const response = await fetch(
            `${API_BASE}/documents/${encodeURIComponent(currentDocument.path)}`,
            {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    content: content,
                    title: extractTitle(content),
                    push: true
                })
            }
        );

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }));
            throw new Error(errorData.detail || 'Failed to save document');
        }

        const updatedDoc = await response.json();
        currentDocument = updatedDoc;
        
        // Update preview
        showPreview(content);
        
        // Switch back to preview mode
        isEditMode = false;
        updateEditModeUI();
        
        // Show git status in success message
        if (updatedDoc.git_error) {
            showSuccess(`Document saved, but git commit failed: ${updatedDoc.git_status || 'Unknown error'}`);
        } else {
            showSuccess(`Document saved and committed! ${updatedDoc.git_status || ''}`);
        }
    } catch (error) {
        console.error('Error saving document:', error);
        showError(error.message || 'Failed to save document');
    }
}

async function createNewDocument() {
    const pathEl = document.getElementById('newDocPath');
    const titleEl = document.getElementById('newDocTitle');
    const contentEl = document.getElementById('newDocContent');
    const sectionEl = document.getElementById('docSection');
    
    if (!pathEl || !titleEl || !contentEl) {
        showError('Form elements not found');
        return;
    }
    
    let path = pathEl.value.trim();
    const title = titleEl.value.trim();
    const content = contentEl.value;

    if (!path) {
        const section = sectionEl ? sectionEl.value : '';
        if (!section) {
            showError('Please select a section or provide a document path');
            return;
        }
        updateDocPath();
        path = pathEl.value.trim();
    }

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
                title: title,
                push: true
            })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }));
            throw new Error(errorData.detail || `Failed to create document: ${response.statusText}`);
        }

        const newDoc = await response.json();
        closeModal();
        
        if (newDoc.git_error) {
            showSuccess(`Document "${path}" created, but git commit failed: ${newDoc.git_status || 'Unknown error'}`);
        } else {
            showSuccess(`Document "${path}" created and committed! ${newDoc.git_status || ''}`);
        }
        
        await loadSections();
        await loadDocuments();
        loadDocument(newDoc.path);
    } catch (error) {
        console.error('Error creating document:', error);
        showError(error.message || 'Failed to create document. Check console for details.');
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
        showSuccess(`Document deleted successfully${gitStatus}`);
        
        currentDocument = null;
        document.getElementById('emptyState').style.display = 'flex';
        document.getElementById('documentContainer').style.display = 'none';
        
        await loadSections();
        await loadDocuments();
    } catch (error) {
        console.error('Error deleting document:', error);
        showError('Failed to delete document');
    }
}

function extractTitle(content) {
    const match = content.match(/^#\s+(.+)$/m);
    return match ? match[1] : null;
}

function showError(message) {
    const toast = document.createElement('div');
    toast.className = 'toast toast-error';
    toast.textContent = `❌ ${message}`;
    document.body.appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function showSuccess(message) {
    const toast = document.createElement('div');
    toast.className = 'toast toast-success';
    toast.textContent = `✅ ${message}`;
    document.body.appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function closeModal() {
    document.getElementById('newDocModal').style.display = 'none';
    document.getElementById('newDocPath').value = '';
    document.getElementById('newDocTitle').value = '';
    document.getElementById('newDocContent').value = '';
}
