from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import random
import string

app = Flask(__name__)

# Dummy file system stored in memory
DUMMY_FILES = {}

def initialize_dummy_files():
    """Initialize with mock file structure"""
    global DUMMY_FILES
    
    DUMMY_FILES = {
        '/': {
            'folders': ['Documents', 'Downloads', 'Desktop', 'Pictures', 'Videos'],
            'files': [
                {'name': 'README.txt', 'size': 2048, 'modified': (datetime.now() - timedelta(days=5)).isoformat()},
                {'name': 'Notes.txt', 'size': 1024, 'modified': (datetime.now() - timedelta(days=2)).isoformat()},
            ]
        },
        '/Documents': {
            'folders': ['Work', 'Personal', 'Archived'],
            'files': [
                {'name': 'ProjectProposal.pdf', 'size': 524288, 'modified': (datetime.now() - timedelta(days=1)).isoformat()},
                {'name': 'Budget2024.xlsx', 'size': 102400, 'modified': (datetime.now() - timedelta(hours=3)).isoformat()},
                {'name': 'Report.docx', 'size': 204800, 'modified': (datetime.now() - timedelta(days=3)).isoformat()},
            ]
        },
        '/Documents/Work': {
            'folders': [],
            'files': [
                {'name': 'Meeting_Notes.txt', 'size': 3072, 'modified': (datetime.now() - timedelta(hours=2)).isoformat()},
                {'name': 'Presentation.pptx', 'size': 1048576, 'modified': (datetime.now() - timedelta(days=1)).isoformat()},
                {'name': 'Code_Review.md', 'size': 5120, 'modified': (datetime.now() - timedelta(hours=12)).isoformat()},
            ]
        },
        '/Documents/Personal': {
            'folders': [],
            'files': [
                {'name': 'Finances.xlsx', 'size': 51200, 'modified': (datetime.now() - timedelta(days=7)).isoformat()},
            ]
        },
        '/Documents/Archived': {
            'folders': [],
            'files': [
                {'name': 'old_project.zip', 'size': 5242880, 'modified': (datetime.now() - timedelta(days=30)).isoformat()},
                {'name': 'backup.tar', 'size': 10485760, 'modified': (datetime.now() - timedelta(days=60)).isoformat()},
            ]
        },
        '/Downloads': {
            'folders': [],
            'files': [
                {'name': 'installer.exe', 'size': 52428800, 'modified': (datetime.now() - timedelta(days=10)).isoformat()},
                {'name': 'document.pdf', 'size': 2097152, 'modified': (datetime.now() - timedelta(days=5)).isoformat()},
                {'name': 'image.png', 'size': 3145728, 'modified': (datetime.now() - timedelta(days=2)).isoformat()},
            ]
        },
        '/Desktop': {
            'folders': ['Projects'],
            'files': [
                {'name': 'ToDoList.txt', 'size': 512, 'modified': datetime.now().isoformat()},
                {'name': 'Shortcut.lnk', 'size': 1024, 'modified': (datetime.now() - timedelta(days=1)).isoformat()},
            ]
        },
        '/Desktop/Projects': {
            'folders': [],
            'files': [
                {'name': 'App.py', 'size': 15360, 'modified': (datetime.now() - timedelta(hours=5)).isoformat()},
                {'name': 'index.html', 'size': 8192, 'modified': (datetime.now() - timedelta(hours=6)).isoformat()},
                {'name': 'style.css', 'size': 10240, 'modified': (datetime.now() - timedelta(hours=4)).isoformat()},
            ]
        },
        '/Pictures': {
            'folders': ['Vacation', 'Screenshots'],
            'files': [
                {'name': 'family_photo.jpg', 'size': 4194304, 'modified': (datetime.now() - timedelta(days=15)).isoformat()},
            ]
        },
        '/Pictures/Vacation': {
            'folders': [],
            'files': [
                {'name': 'beach.jpg', 'size': 5242880, 'modified': (datetime.now() - timedelta(days=20)).isoformat()},
                {'name': 'sunset.png', 'size': 6291456, 'modified': (datetime.now() - timedelta(days=19)).isoformat()},
                {'name': 'mountain.jpg', 'size': 4718592, 'modified': (datetime.now() - timedelta(days=18)).isoformat()},
            ]
        },
        '/Pictures/Screenshots': {
            'folders': [],
            'files': [
                {'name': 'screen1.png', 'size': 2097152, 'modified': (datetime.now() - timedelta(days=3)).isoformat()},
                {'name': 'screen2.png', 'size': 1835008, 'modified': (datetime.now() - timedelta(days=2)).isoformat()},
            ]
        },
        '/Videos': {
            'folders': [],
            'files': [
                {'name': 'Tutorial.mp4', 'size': 157286400, 'modified': (datetime.now() - timedelta(days=10)).isoformat()},
                {'name': 'Recording.webm', 'size': 104857600, 'modified': (datetime.now() - timedelta(days=5)).isoformat()},
            ]
        },
    }

def get_file_size(size_bytes):
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"

def get_file_icon(filename, is_dir):
    """Get icon class based on file type"""
    if is_dir:
        return "folder"
    
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    icon_map = {
        'pdf': 'file-pdf',
        'doc': 'file-word', 'docx': 'file-word',
        'xls': 'file-excel', 'xlsx': 'file-excel',
        'ppt': 'file-powerpoint', 'pptx': 'file-powerpoint',
        'jpg': 'file-image', 'jpeg': 'file-image', 'png': 'file-image', 'gif': 'file-image',
        'mp4': 'file-video', 'avi': 'file-video', 'mov': 'file-video', 'webm': 'file-video',
        'mp3': 'file-audio', 'wav': 'file-audio', 'flac': 'file-audio',
        'zip': 'file-archive', 'rar': 'file-archive', '7z': 'file-archive', 'tar': 'file-archive',
        'txt': 'file-text', 'md': 'file-text', 'py': 'file-code', 'js': 'file-code', 'html': 'file-code',
    }
    return icon_map.get(ext, 'file')

def path_exists(path):
    """Check if path exists in dummy files"""
    return path in DUMMY_FILES or path == '/'

def get_parent_path(path):
    """Get parent directory path"""
    if path == '/':
        return None
    parts = path.rstrip('/').split('/')
    return '/' + '/'.join(parts[1:-1]) if len(parts) > 2 else '/'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/list', methods=['GET'])
def list_files():
    try:
        current_path = request.args.get('path', '/')
        current_path = '/' + current_path.strip('/') if current_path != '/' else '/'
        
        # Check if path exists
        if not path_exists(current_path):
            return jsonify({'error': 'Invalid directory'}), 400
        
        items = []
        dir_data = DUMMY_FILES.get(current_path, {'folders': [], 'files': []})
        
        # Add folders
        for folder_name in sorted(dir_data.get('folders', [])):
            items.append({
                'name': folder_name,
                'path': current_path.rstrip('/') + '/' + folder_name,
                'is_dir': True,
                'size': '-',
                'modified': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d %H:%M:%S'),
                'icon': get_file_icon(folder_name, True)
            })
        
        # Add files
        for file_info in sorted(dir_data.get('files', []), key=lambda x: x['name']):
            modified_str = datetime.fromisoformat(file_info['modified']).strftime('%Y-%m-%d %H:%M:%S')
            items.append({
                'name': file_info['name'],
                'path': current_path.rstrip('/') + '/' + file_info['name'],
                'is_dir': False,
                'size': get_file_size(file_info['size']),
                'modified': modified_str,
                'icon': get_file_icon(file_info['name'], False)
            })
        
        return jsonify({
            'items': items,
            'current_path': current_path,
            'parent_path': get_parent_path(current_path)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete', methods=['POST'])
def delete_file():
    try:
        path = request.json.get('path', '').rstrip('/')
        
        if not path:
            return jsonify({'error': 'Invalid path'}), 403
        
        # Parse path
        parts = path.split('/')
        parent_path = '/' + '/'.join(parts[1:-1]) if len(parts) > 2 else '/'
        name = parts[-1]
        
        if not path_exists(parent_path):
            return jsonify({'error': 'Parent path not found'}), 404
        
        dir_data = DUMMY_FILES.get(parent_path, {'folders': [], 'files': []})
        
        # Try to delete folder
        if name in dir_data.get('folders', []):
            dir_data['folders'].remove(name)
            # Remove the folder from DUMMY_FILES
            if path in DUMMY_FILES:
                del DUMMY_FILES[path]
            return jsonify({'success': True})
        
        # Try to delete file
        files = dir_data.get('files', [])
        for i, file_info in enumerate(files):
            if file_info['name'] == name:
                files.pop(i)
                return jsonify({'success': True})
        
        return jsonify({'error': 'File not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rename', methods=['POST'])
def rename_file():
    try:
        old_path = request.json.get('path', '').rstrip('/')
        new_name = request.json.get('new_name', '').strip()
        
        if not old_path or not new_name:
            return jsonify({'error': 'Invalid input'}), 400
        
        # Parse path
        parts = old_path.split('/')
        parent_path = '/' + '/'.join(parts[1:-1]) if len(parts) > 2 else '/'
        old_name = parts[-1]
        
        if not path_exists(parent_path):
            return jsonify({'error': 'Parent path not found'}), 404
        
        dir_data = DUMMY_FILES.get(parent_path, {'folders': [], 'files': []})
        
        # Rename folder
        if old_name in dir_data.get('folders', []):
            idx = dir_data['folders'].index(old_name)
            dir_data['folders'][idx] = new_name
            
            # Update in DUMMY_FILES
            old_full_path = old_path
            new_full_path = parent_path.rstrip('/') + '/' + new_name
            if old_full_path in DUMMY_FILES:
                DUMMY_FILES[new_full_path] = DUMMY_FILES.pop(old_full_path)
            
            return jsonify({'success': True, 'new_path': new_full_path})
        
        # Rename file
        files = dir_data.get('files', [])
        for file_info in files:
            if file_info['name'] == old_name:
                file_info['name'] = new_name
                return jsonify({'success': True, 'new_path': parent_path.rstrip('/') + '/' + new_name})
        
        return jsonify({'error': 'File not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mkdir', methods=['POST'])
def create_dir():
    try:
        parent_path = request.json.get('path', '/').rstrip('/')
        folder_name = request.json.get('name', 'New Folder').strip()
        
        if not folder_name:
            return jsonify({'error': 'Invalid folder name'}), 400
        
        if not path_exists(parent_path):
            return jsonify({'error': 'Parent path not found'}), 404
        
        dir_data = DUMMY_FILES.get(parent_path, {'folders': [], 'files': []})
        
        # Check if folder already exists
        if folder_name in dir_data.get('folders', []):
            return jsonify({'error': 'Folder already exists'}), 400
        
        dir_data['folders'].append(folder_name)
        
        # Add new folder to DUMMY_FILES
        new_path = parent_path.rstrip('/') + '/' + folder_name
        DUMMY_FILES[new_path] = {'folders': [], 'files': []}
        
        return jsonify({'success': True, 'path': new_path})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        current_path = request.form.get('path', '/').rstrip('/')
        
        if not path_exists(current_path):
            return jsonify({'error': 'Access denied'}), 403
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        dir_data = DUMMY_FILES.get(current_path, {'folders': [], 'files': []})
        
        # Check if file already exists
        for file_info in dir_data.get('files', []):
            if file_info['name'] == file.filename:
                return jsonify({'error': 'File already exists'}), 400
        
        # Add file to dummy system (don't actually save it)
        file_size = len(file.read())
        file.seek(0)
        
        dir_data['files'].append({
            'name': file.filename,
            'size': file_size if file_size > 0 else 1024,
            'modified': datetime.now().isoformat()
        })
        
        filepath = current_path.rstrip('/') + '/' + file.filename
        return jsonify({'success': True, 'path': filepath})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    initialize_dummy_files()
    app.run(debug=True, port=5000)
