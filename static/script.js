// State management
let currentPath = null;
let navigationHistory = [];
let historyIndex = -1;
let renamingPath = null;
let deletingPath = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    navigateTo('/');
});

// Get common paths (dummy paths)
function getHomePath() {
    return '/';
}

function getUsername() {
    return 'User';
}

function getDesktopPath() {
    return '/Desktop';
}

function getDocumentsPath() {
    return '/Documents';
}

function getDownloadsPath() {
    return '/Downloads';
}

// Navigation
function navigateTo(path) {
    if (!path) return;
    
    path = path.trim();
    
    // Remove from history if navigating back/forward changes the path
    if (historyIndex < navigationHistory.length - 1) {
        navigationHistory = navigationHistory.slice(0, historyIndex + 1);
    }
    
    navigationHistory.push(path);
    historyIndex = navigationHistory.length - 1;
    
    loadFiles(path);
}

function goBack() {
    if (historyIndex > 0) {
        historyIndex--;
        loadFiles(navigationHistory[historyIndex]);
    }
}

function goForward() {
    if (historyIndex < navigationHistory.length - 1) {
        historyIndex++;
        loadFiles(navigationHistory[historyIndex]);
    }
}

function handlePathKeypress(event) {
    if (event.key === 'Enter') {
        const path = document.getElementById('pathInput').value;
        navigateTo(path);
    }
}

// Load files from server
function loadFiles(path) {
    document.getElementById('fileList').innerHTML = '<div class="loading">Loading files...</div>';
    updateStatus('Loading...');
    
    fetch(`/api/list?path=${encodeURIComponent(path)}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.error);
                return;
            }
            
            currentPath = data.current_path;
            document.getElementById('pathInput').value = currentPath;
            
            displayFiles(data.items);
            updateStatus(`Ready - ${data.items.length} items`);
        })
        .catch(error => {
            showError('Failed to load files: ' + error.message);
        });
}

// Display files in the list
function displayFiles(items) {
    const fileList = document.getElementById('fileList');
    
    if (items.length === 0) {
        fileList.innerHTML = '<div class="loading">No files in this directory</div>';
        return;
    }
    
    fileList.innerHTML = items.map(item => `
        <div class="file-item" ondblclick="handleItemDoubleClick('${item.path}', ${item.is_dir})">
            <div class="col-name">
                <div class="file-item-name">
                    <span class="file-icon">${getIconEmoji(item.icon)}</span>
                    <a href="#" class="file-name" onclick="handleItemClick(event, '${item.path}', ${item.is_dir}); return false;">
                        ${escapeHtml(item.name)}
                    </a>
                </div>
            </div>
            <div class="col-size">${item.size}</div>
            <div class="col-modified">${item.modified}</div>
            <div class="col-actions">
                <div class="file-actions">
                    ${!item.is_dir ? `<button class="action-btn" onclick="downloadFile('${item.path}')" title="Download">⬇️</button>` : ''}
                    <button class="action-btn" onclick="showRenameDialog('${item.path}', '${escapeHtml(item.name)}')" title="Rename">✏️</button>
                    <button class="action-btn delete" onclick="showDeleteConfirm('${item.path}', '${escapeHtml(item.name)}')" title="Delete">🗑️</button>
                </div>
            </div>
        </div>
    `).join('');
}

// Get emoji icon based on file type
function getIconEmoji(iconType) {
    const emojiMap = {
        'folder': '📁',
        'file-pdf': '📕',
        'file-word': '📘',
        'file-excel': '📊',
        'file-powerpoint': '📙',
        'file-image': '🖼️',
        'file-video': '🎥',
        'file-audio': '🎵',
        'file-archive': '📦',
        'file-text': '📄',
        'file-code': '💻',
        'file': '📄'
    };
    return emojiMap[iconType] || '📄';
}

// Handle file/folder click
function handleItemClick(event, path, isDir) {
    if (isDir) {
        navigateTo(path);
    } else {
        downloadFile(path);
    }
}

function handleItemDoubleClick(path, isDir) {
    if (isDir) {
        navigateTo(path);
    }
}

// Download file
function downloadFile(path) {
    // In dummy mode, just show a notification instead of actual download
    alert('📥 Download: This is a simulated file manager. No actual files are downloaded.\n\nFile: ' + path);
}

// New folder dialog
function showNewFolderDialog() {
    document.getElementById('folderName').value = '';
    document.getElementById('newFolderDialog').classList.remove('hidden');
    document.getElementById('folderName').focus();
}

function createNewFolder() {
    const folderName = document.getElementById('folderName').value.trim();
    
    if (!folderName) {
        showError('Please enter a folder name');
        return;
    }
    
    fetch('/api/mkdir', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            path: currentPath,
            name: folderName
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showError(data.error);
        } else {
            closeDialog('newFolderDialog');
            loadFiles(currentPath);
            updateStatus(`Created folder: ${folderName}`);
        }
    })
    .catch(error => showError('Failed to create folder: ' + error.message));
}

// Rename dialog
function showRenameDialog(path, currentName) {
    renamingPath = path;
    document.getElementById('renameName').value = currentName;
    document.getElementById('renameDialog').classList.remove('hidden');
    document.getElementById('renameName').focus();
    document.getElementById('renameName').select();
}

function confirmRename() {
    const newName = document.getElementById('renameName').value.trim();
    
    if (!newName) {
        showError('Please enter a new name');
        return;
    }
    
    fetch('/api/rename', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            path: renamingPath,
            new_name: newName
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showError(data.error);
        } else {
            closeDialog('renameDialog');
            loadFiles(currentPath);
            updateStatus(`Renamed to: ${newName}`);
        }
    })
    .catch(error => showError('Failed to rename: ' + error.message));
}

// Delete confirmation
function showDeleteConfirm(path, name) {
    deletingPath = path;
    document.getElementById('confirmMessage').textContent = `Are you sure you want to delete "${name}"?`;
    document.getElementById('confirmDialog').classList.remove('hidden');
}

function confirmDelete() {
    fetch('/api/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: deletingPath })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showError(data.error);
        } else {
            closeDialog('confirmDialog');
            loadFiles(currentPath);
            updateStatus('File deleted');
        }
    })
    .catch(error => showError('Failed to delete: ' + error.message));
}

// Upload file
function uploadFile(event) {
    const files = event.target.files;
    
    if (files.length === 0) return;
    
    const formData = new FormData();
    formData.append('file', files[0]);
    formData.append('path', currentPath);
    
    updateStatus(`Uploading ${files[0].name}...`);
    
    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showError(data.error);
        } else {
            loadFiles(currentPath);
            updateStatus(`Uploaded: ${files[0].name}`);
        }
    })
    .catch(error => showError('Upload failed: ' + error.message))
    .finally(() => {
        document.getElementById('fileInput').value = '';
    });
}

// Refresh
function refreshFiles() {
    if (currentPath) {
        loadFiles(currentPath);
    }
}

// Dialog management
function closeDialog(dialogId) {
    document.getElementById(dialogId).classList.add('hidden');
}

// Utils
function updateStatus(message) {
    document.getElementById('statusMessage').textContent = message;
}

function showError(message) {
    updateStatus('Error: ' + message);
    alert('Error: ' + message);
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Close dialogs on Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        document.querySelectorAll('.dialog:not(.hidden)').forEach(dialog => {
            dialog.classList.add('hidden');
        });
    }
});
