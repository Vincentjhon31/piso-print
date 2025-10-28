"""
PisoPrint Admin Dashboard
Simple web interface to manage files, database, and view statistics
"""
from flask import Flask, render_template_string, jsonify, request, send_file
import sqlite3
import os
from datetime import datetime
import shutil

app = Flask(__name__)

# Configuration
DATABASE = 'pisoprint.db'
UPLOAD_FOLDER = 'uploads'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

# Admin Dashboard HTML Template
ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PisoPrint Admin Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, #f0f4ff 0%, #e8f0fe 100%);
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #667eea;
            text-align: center;
        }
        .stat-card h3 {
            color: #667eea;
            font-size: 1em;
            margin-bottom: 10px;
        }
        .stat-card .value {
            font-size: 2.5em;
            font-weight: bold;
            color: #764ba2;
        }
        .section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .section h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.5em;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            background: white;
            border-radius: 5px;
            overflow: hidden;
        }
        th {
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        td {
            padding: 10px 12px;
            border-bottom: 1px solid #e0e0e0;
        }
        tr:hover {
            background: #f0f4ff;
        }
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            margin: 5px;
        }
        .btn-danger {
            background: #f44336;
            color: white;
        }
        .btn-danger:hover {
            background: #d32f2f;
            transform: translateY(-2px);
        }
        .btn-warning {
            background: #ff9800;
            color: white;
        }
        .btn-warning:hover {
            background: #f57c00;
            transform: translateY(-2px);
        }
        .btn-success {
            background: #4CAF50;
            color: white;
        }
        .btn-success:hover {
            background: #45a049;
            transform: translateY(-2px);
        }
        .btn-primary {
            background: #667eea;
            color: white;
        }
        .btn-primary:hover {
            background: #5568d3;
            transform: translateY(-2px);
        }
        .status {
            padding: 8px 12px;
            border-radius: 5px;
            display: inline-block;
            margin-top: 10px;
        }
        .status.success {
            background: #d4edda;
            color: #155724;
        }
        .status.error {
            background: #f8d7da;
            color: #721c24;
        }
        .actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 15px;
        }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.85em;
            font-weight: 600;
        }
        .badge-success {
            background: #d4edda;
            color: #155724;
        }
        .badge-danger {
            background: #f8d7da;
            color: #721c24;
        }
        #message { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 PisoPrint Admin Dashboard</h1>
        <p class="subtitle">Manage files, database, and system settings</p>
        
        <div id="message" class="status"></div>
        
        <!-- Statistics -->
        <div class="stats">
            <div class="stat-card">
                <h3>📄 Total Files</h3>
                <div class="value" id="totalFiles">{{ stats.total_files }}</div>
            </div>
            <div class="stat-card">
                <h3>💾 Disk Usage</h3>
                <div class="value" id="diskUsage">{{ stats.disk_usage_mb }} MB</div>
            </div>
            <div class="stat-card">
                <h3>👥 Total Users</h3>
                <div class="value" id="totalUsers">{{ stats.total_users }}</div>
            </div>
            <div class="stat-card">
                <h3>💰 Total Revenue</h3>
                <div class="value" id="totalRevenue">₱{{ stats.total_revenue }}</div>
            </div>
        </div>
        
        <!-- Quick Actions -->
        <div class="section">
            <h2>⚡ Quick Actions</h2>
            <div class="actions">
                <button class="btn btn-warning" onclick="cleanOrphanedRecords()">
                    🧹 Clean Orphaned Records
                </button>
                <button class="btn btn-danger" onclick="deleteOldFiles()">
                    🗑️ Delete Files Older Than 7 Days
                </button>
                <button class="btn btn-danger" onclick="if(confirm('⚠️ This will delete ALL files and records! Continue?')) clearAllData()">
                    💣 Clear All Data
                </button>
                <button class="btn btn-success" onclick="location.reload()">
                    🔄 Refresh Stats
                </button>
            </div>
        </div>
        
        <!-- Recent Files -->
        <div class="section">
            <h2>📁 Recent Files (Last 20)</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Filename</th>
                        <th>User</th>
                        <th>Size</th>
                        <th>Pages</th>
                        <th>Status</th>
                        <th>Uploaded</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for file in files %}
                    <tr>
                        <td>{{ file.file_id }}</td>
                        <td>{{ file.filename }}</td>
                        <td>{{ file.session_id }}</td>
                        <td>{{ (file.file_size / 1024) | round(1) }} KB</td>
                        <td>{{ file.pages }}</td>
                        <td>
                            {% if file.file_exists %}
                            <span class="badge badge-success">✅ Exists</span>
                            {% else %}
                            <span class="badge badge-danger">❌ Missing</span>
                            {% endif %}
                        </td>
                        <td>{{ file.created_at }}</td>
                        <td>
                            <button class="btn btn-danger" onclick="deleteFile({{ file.file_id }})">Delete</button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <!-- User Activity -->
        <div class="section">
            <h2>👥 User Activity</h2>
            <table>
                <thead>
                    <tr>
                        <th>User ID</th>
                        <th>Session ID</th>
                        <th>Credits</th>
                        <th>Files Uploaded</th>
                        <th>Last Active</th>
                    </tr>
                </thead>
                <tbody>
                    {% for user in users %}
                    <tr>
                        <td>{{ user.user_id }}</td>
                        <td>{{ user.session_id }}</td>
                        <td>₱{{ user.credits }}</td>
                        <td>{{ user.file_count }}</td>
                        <td>{{ user.last_active }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        function showMessage(msg, type) {
            const el = document.getElementById('message');
            el.textContent = msg;
            el.className = 'status ' + type;
            el.style.display = 'block';
            setTimeout(() => { el.style.display = 'none'; }, 5000);
        }
        
        function cleanOrphanedRecords() {
            if (!confirm('Remove database records for missing files?')) return;
            
            fetch('/admin/clean-orphaned', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    showMessage(data.message, 'success');
                    setTimeout(() => location.reload(), 2000);
                })
                .catch(err => {
                    showMessage('Error: ' + err, 'error');
                });
        }
        
        function deleteOldFiles() {
            if (!confirm('Delete files older than 7 days?')) return;
            
            fetch('/admin/delete-old', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    showMessage(data.message, 'success');
                    setTimeout(() => location.reload(), 2000);
                })
                .catch(err => {
                    showMessage('Error: ' + err, 'error');
                });
        }
        
        function clearAllData() {
            fetch('/admin/clear-all', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    showMessage(data.message, 'success');
                    setTimeout(() => location.reload(), 2000);
                })
                .catch(err => {
                    showMessage('Error: ' + err, 'error');
                });
        }
        
        function deleteFile(fileId) {
            if (!confirm('Delete this file?')) return;
            
            fetch('/admin/delete-file/' + fileId, { method: 'DELETE' })
                .then(r => r.json())
                .then(data => {
                    showMessage(data.message, 'success');
                    setTimeout(() => location.reload(), 1000);
                })
                .catch(err => {
                    showMessage('Error: ' + err, 'error');
                });
        }
    </script>
</body>
</html>
"""

@app.route('/admin')
def admin_dashboard():
    """Admin dashboard page"""
    db = get_db()
    
    # Get statistics
    stats = {}
    stats['total_files'] = db.execute('SELECT COUNT(*) as count FROM files').fetchone()['count']
    stats['total_users'] = db.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
    
    # Calculate disk usage
    disk_usage = 0
    if os.path.exists(UPLOAD_FOLDER):
        for file in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, file)
            if os.path.isfile(filepath):
                disk_usage += os.path.getsize(filepath)
    stats['disk_usage_mb'] = round(disk_usage / 1024 / 1024, 2)
    
    # Calculate total revenue
    result = db.execute('SELECT SUM(pages) as total FROM files').fetchone()
    stats['total_revenue'] = result['total'] if result['total'] else 0
    
    # Get recent files
    files = []
    for row in db.execute('SELECT * FROM files ORDER BY file_id DESC LIMIT 20').fetchall():
        file_dict = dict(row)
        # Check if file exists
        file_dict['file_exists'] = os.path.exists(row['file_path']) if row['file_path'] else False
        files.append(file_dict)
    
    # Get users with activity
    users = db.execute('''
        SELECT u.*, COUNT(f.file_id) as file_count, MAX(f.created_at) as last_active
        FROM users u
        LEFT JOIN files f ON u.session_id = f.session_id
        GROUP BY u.user_id
        ORDER BY last_active DESC
        LIMIT 10
    ''').fetchall()
    
    db.close()
    
    return render_template_string(ADMIN_TEMPLATE, stats=stats, files=files, users=[dict(u) for u in users])

@app.route('/admin/clean-orphaned', methods=['POST'])
def clean_orphaned():
    """Remove database records for files that don't exist"""
    db = get_db()
    
    # Get all files
    files = db.execute('SELECT file_id, file_path FROM files').fetchall()
    deleted_count = 0
    
    for file in files:
        if not os.path.exists(file['file_path']):
            db.execute('DELETE FROM files WHERE file_id = ?', (file['file_id'],))
            deleted_count += 1
    
    db.commit()
    db.close()
    
    return jsonify({
        'success': True,
        'message': f'✅ Cleaned {deleted_count} orphaned records'
    })

@app.route('/admin/delete-old', methods=['POST'])
def delete_old_files():
    """Delete files older than 7 days"""
    db = get_db()
    
    # Get files older than 7 days
    seven_days_ago = datetime.now().timestamp() - (7 * 24 * 60 * 60)
    
    files = db.execute('''
        SELECT file_id, file_path 
        FROM files 
        WHERE strftime('%s', created_at) < ?
    ''', (seven_days_ago,)).fetchall()
    
    deleted_count = 0
    for file in files:
        # Delete physical file
        if os.path.exists(file['file_path']):
            os.remove(file['file_path'])
        
        # Delete database record
        db.execute('DELETE FROM files WHERE file_id = ?', (file['file_id'],))
        deleted_count += 1
    
    db.commit()
    db.close()
    
    return jsonify({
        'success': True,
        'message': f'✅ Deleted {deleted_count} old files'
    })

@app.route('/admin/clear-all', methods=['POST'])
def clear_all():
    """Clear all files and database records"""
    db = get_db()
    
    # Delete all physical files
    if os.path.exists(UPLOAD_FOLDER):
        for file in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, file)
            if os.path.isfile(filepath):
                os.remove(filepath)
    
    # Clear database
    db.execute('DELETE FROM files')
    db.execute('DELETE FROM users')
    db.execute("DELETE FROM sqlite_sequence WHERE name IN ('files', 'users')")
    db.commit()
    db.close()
    
    return jsonify({
        'success': True,
        'message': '✅ All data cleared!'
    })

@app.route('/admin/delete-file/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Delete a specific file"""
    db = get_db()
    
    # Get file info
    file = db.execute('SELECT file_path FROM files WHERE file_id = ?', (file_id,)).fetchone()
    
    if file:
        # Delete physical file
        if os.path.exists(file['file_path']):
            os.remove(file['file_path'])
        
        # Delete database record
        db.execute('DELETE FROM files WHERE file_id = ?', (file_id,))
        db.commit()
    
    db.close()
    
    return jsonify({
        'success': True,
        'message': f'✅ File {file_id} deleted'
    })

if __name__ == '__main__':
    # Run on port 5001 (different from main app)
    app.run(host='0.0.0.0', port=5001, debug=True)
