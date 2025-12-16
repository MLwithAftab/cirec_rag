// Admin Interface JavaScript

const API_BASE = '/api/admin';

// Check authentication
const token = localStorage.getItem('token');
if (!token) {
    window.location.href = '/login';
}

// Headers with token
const authHeaders = {
    'Authorization': `Bearer ${token}`
};

// Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');
const uploadProgress = document.getElementById('uploadProgress');
const progressFill = document.getElementById('progressFill');
const uploadStatus = document.getElementById('uploadStatus');
const documentsTable = document.getElementById('documentsTable');
const refreshBtn = document.getElementById('refreshBtn');
const rebuildIndexBtn = document.getElementById('rebuildIndexBtn');
const systemStatusBtn = document.getElementById('systemStatusBtn');
const logoutBtn = document.getElementById('logoutBtn');
const deleteModal = document.getElementById('deleteModal');
const cancelDelete = document.getElementById('cancelDelete');
const confirmDelete = document.getElementById('confirmDelete');
const deleteFilename = document.getElementById('deleteFilename');

let fileToDelete = null;

// Logout
logoutBtn.addEventListener('click', () => {
    localStorage.removeItem('token');
    window.location.href = '/login';
});

// Browse files
browseBtn.addEventListener('click', () => {
    fileInput.click();
});

// File input change
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        uploadFiles(Array.from(e.target.files));
    }
});

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = Array.from(e.dataTransfer.files);
    uploadFiles(files);
});

// Upload files
async function uploadFiles(files) {
    uploadProgress.style.display = 'block';
    
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const progress = ((i + 1) / files.length) * 100;
        
        progressFill.style.width = `${progress}%`;
        uploadStatus.textContent = `Uploading ${file.name}... (${i + 1}/${files.length})`;
        
        try {
            await uploadFile(file);
            showStatus(`${file.name} uploaded successfully`, 'success');
        } catch (error) {
            showStatus(`Failed to upload ${file.name}`, 'error');
            console.error('Upload error:', error);
        }
    }
    
    uploadProgress.style.display = 'none';
    progressFill.style.width = '0%';
    fileInput.value = '';
    
    // Refresh documents list
    loadDocuments();
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        headers: authHeaders,
        body: formData
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Upload failed');
    }
    
    return await response.json();
}

// Load documents
async function loadDocuments() {
    documentsTable.innerHTML = '<div class="table-loading"><span class="spinner"></span> Loading documents...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/documents`, {
            headers: authHeaders
        });
        
        if (!response.ok) {
            throw new Error('Failed to load documents');
        }
        
        const documents = await response.json();
        displayDocuments(documents);
        
    } catch (error) {
        console.error('Error loading documents:', error);
        documentsTable.innerHTML = '<p style="color: var(--danger-color); padding: 2rem; text-align: center;">Failed to load documents</p>';
        
        if (error.message.includes('401')) {
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
    }
}

function displayDocuments(documents) {
    if (documents.length === 0) {
        documentsTable.innerHTML = '<p style="color: var(--text-secondary); padding: 2rem; text-align: center;">No documents uploaded yet</p>';
        return;
    }
    
    const table = document.createElement('table');
    table.innerHTML = `
        <thead>
            <tr>
                <th>Filename</th>
                <th>Type</th>
                <th>Size</th>
                <th>Upload Date</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody id="documentsList"></tbody>
    `;
    
    documentsTable.innerHTML = '';
    documentsTable.appendChild(table);
    
    const tbody = document.getElementById('documentsList');
    
    documents.forEach(doc => {
        const row = createDocumentRow(doc);
        tbody.appendChild(row);
    });
}

function createDocumentRow(doc) {
    const tr = document.createElement('tr');
    
    const fileType = doc.type.substring(1).toUpperCase();
    const badgeClass = getBadgeClass(doc.type);
    const size = formatFileSize(doc.size);
    const date = new Date(doc.upload_date).toLocaleString();
    
    tr.innerHTML = `
        <td><strong>${doc.filename}</strong></td>
        <td><span class="file-type-badge ${badgeClass}">${fileType}</span></td>
        <td>${size}</td>
        <td>${date}</td>
        <td>${doc.indexed ? '✅ Indexed' : '⏳ Pending'}</td>
        <td>
            <button class="btn btn-danger btn-sm delete-btn" data-filename="${doc.filename}">
                🗑️ Delete
            </button>
        </td>
    `;
    
    // Add delete event
    tr.querySelector('.delete-btn').addEventListener('click', () => {
        showDeleteModal(doc.filename);
    });
    
    return tr;
}

function getBadgeClass(type) {
    if (type === '.pdf') return 'badge-pdf';
    if (type === '.docx' || type === '.doc') return 'badge-word';
    if (type === '.xlsx' || type === '.xls') return 'badge-excel';
    return 'badge-pdf';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Delete document
function showDeleteModal(filename) {
    fileToDelete = filename;
    deleteFilename.textContent = filename;
    deleteModal.style.display = 'flex';
}

cancelDelete.addEventListener('click', () => {
    deleteModal.style.display = 'none';
    fileToDelete = null;
});

confirmDelete.addEventListener('click', async () => {
    if (!fileToDelete) return;
    
    try {
        const response = await fetch(`${API_BASE}/documents/${fileToDelete}`, {
            method: 'DELETE',
            headers: authHeaders
        });
        
        if (!response.ok) {
            throw new Error('Delete failed');
        }
        
        showStatus(`${fileToDelete} deleted successfully`, 'success');
        deleteModal.style.display = 'none';
        fileToDelete = null;
        
        loadDocuments();
        
    } catch (error) {
        console.error('Delete error:', error);
        showStatus('Failed to delete document', 'error');
    }
});

// Refresh documents
refreshBtn.addEventListener('click', loadDocuments);

// Rebuild index
rebuildIndexBtn.addEventListener('click', async () => {
    if (!confirm('Are you sure you want to rebuild the entire index? This may take some time.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/rebuild-index`, {
            method: 'POST',
            headers: authHeaders
        });
        
        if (!response.ok) {
            throw new Error('Rebuild failed');
        }
        
        showStatus('Index rebuild initiated', 'success');
        
    } catch (error) {
        console.error('Rebuild error:', error);
        showStatus('Failed to rebuild index', 'error');
    }
});

// System status
systemStatusBtn.addEventListener('click', async () => {
    try {
        const response = await fetch('/health');
        const data = await response.json();
        
        alert(`System Status: ${data.status}\nVersion: ${data.version}`);
        
    } catch (error) {
        console.error('Status error:', error);
        showStatus('Failed to get system status', 'error');
    }
});

// Show status message
function showStatus(message, type = 'info') {
    const statusDiv = document.getElementById('statusMessage');
    statusDiv.textContent = message;
    statusDiv.className = `status-message status-${type}`;
    statusDiv.style.display = 'block';
    
    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 3000);
}

// Load documents on page load
loadDocuments();