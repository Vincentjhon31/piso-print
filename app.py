#!/usr/bin/env python3
"""
Piso Print Flask Server
Runs on Orange Pi PC H3 with Armbian OS
Handles file uploads, printing, and credit management
"""

# Import required modules with error handling
try:
    from flask import Flask, request, jsonify, send_from_directory
    from flask_cors import CORS
    from werkzeug.utils import secure_filename
except ImportError as e:
    print("❌ Error: Flask is not installed!")
    print("📦 Please install required packages:")
    print("   pip install flask flask-cors werkzeug")
    print(f"\nDetails: {e}")
    exit(1)

import sqlite3
import os
import hashlib
from datetime import datetime
import logging
import subprocess

# Optional imports - gracefully handle if not available
try:
    import cups
    CUPS_AVAILABLE = True
except ImportError:
    CUPS_AVAILABLE = False
    cups = None
    print("⚠️  Warning: pycups not available - printer functionality limited")

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    print("⚠️  Warning: PyPDF2 not available - PDF page counting disabled")

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("⚠️  Warning: python-docx not available - DOCX support disabled")

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️  Warning: Pillow not available - image support limited")

# ============================================
# Configuration
# ============================================
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = '/home/pisoprint/uploads'
DATABASE = '/home/pisoprint/pisoprint.db'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'txt'}
PRICE_PER_PAGE = 1  # ₱1 per page
DEFAULT_PRINTER = 'PisoPrinter'  # Change to your CUPS printer name

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# Database Setup
# ============================================
def init_db():
    """Initialize SQLite database with tables"""
    logger.info("Initializing database...")
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            credits INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Files table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER,
            pages INTEGER,
            file_type TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES users(session_id)
        )
    ''')
    
    # Transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            type TEXT NOT NULL,
            amount INTEGER NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES users(session_id)
        )
    ''')
    
    # Print jobs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS print_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            file_id INTEGER NOT NULL,
            pages INTEGER NOT NULL,
            cost INTEGER NOT NULL,
            status TEXT DEFAULT 'printing',
            printed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES users(session_id),
            FOREIGN KEY (file_id) REFERENCES files(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

# Initialize database on startup
init_db()

# ============================================
# CUPS Connection
# ============================================
if CUPS_AVAILABLE:
    try:
        conn_cups = cups.Connection()
        printers = conn_cups.getPrinters()
        logger.info(f"CUPS connected. Available printers: {list(printers.keys())}")
    except Exception as e:
        logger.error(f"CUPS connection failed: {e}")
        conn_cups = None
else:
    conn_cups = None
    logger.warning("CUPS not available - printer functionality disabled")

# ============================================
# Helper Functions
# ============================================
def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_or_create_user(session_id):
    """Get user or create if doesn't exist"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT * FROM users WHERE session_id = ?', (session_id,))
    user = cursor.fetchone()
    
    if not user:
        cursor.execute(
            'INSERT INTO users (session_id, credits) VALUES (?, 0)',
            (session_id,)
        )
        db.commit()
        cursor.execute('SELECT * FROM users WHERE session_id = ?', (session_id,))
        user = cursor.fetchone()
        logger.info(f"Created new user: {session_id}")
    
    db.close()
    return dict(user)

def count_pdf_pages(filepath):
    """Count pages in PDF file"""
    if not PYPDF2_AVAILABLE:
        logger.warning("PyPDF2 not available, returning 1 page")
        return 1
    
    try:
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            return len(pdf_reader.pages)
    except Exception as e:
        logger.error(f"PDF page count error: {e}")
        return 1

def count_docx_pages(filepath):
    """Estimate pages in DOCX (rough estimate based on word count)"""
    if not DOCX_AVAILABLE:
        logger.warning("python-docx not available, returning 1 page")
        return 1
    
    try:
        doc = Document(filepath)
        total_words = sum(len(paragraph.text.split()) for paragraph in doc.paragraphs)
        # Rough estimate: 500 words per page
        estimated_pages = max(1, round(total_words / 500))
        return estimated_pages
    except Exception as e:
        logger.error(f"DOCX page count error: {e}")
        return 1

def count_image_pages(filepath):
    """Images are always 1 page"""
    return 1

def count_txt_pages(filepath):
    """Estimate pages in TXT file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            # Rough estimate: 50 lines per page
            estimated_pages = max(1, round(len(lines) / 50))
            return estimated_pages
    except Exception as e:
        logger.error(f"TXT page count error: {e}")
        return 1

def count_file_pages(filepath, extension):
    """Count pages based on file type"""
    extension = extension.lower()
    
    if extension == 'pdf':
        return count_pdf_pages(filepath)
    elif extension in ['doc', 'docx']:
        return count_docx_pages(filepath)
    elif extension in ['jpg', 'jpeg', 'png']:
        return count_image_pages(filepath)
    elif extension == 'txt':
        return count_txt_pages(filepath)
    else:
        return 1

def convert_docx_to_pdf(docx_path):
    """Convert DOCX to PDF using LibreOffice"""
    try:
        output_dir = os.path.dirname(docx_path)
        
        # Use LibreOffice to convert DOCX to PDF
        result = subprocess.run([
            'soffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', output_dir,
            docx_path
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Generate PDF path
            pdf_path = os.path.splitext(docx_path)[0] + '.pdf'
            
            if os.path.exists(pdf_path):
                logger.info(f"✅ Converted DOCX to PDF: {pdf_path}")
                return pdf_path
            else:
                logger.error(f"PDF not created: {pdf_path}")
                return None
        else:
            logger.error(f"LibreOffice conversion failed: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        logger.error("DOCX conversion timeout (30s)")
        return None
    except FileNotFoundError:
        logger.error("LibreOffice (soffice) not found. Install: sudo apt install libreoffice-writer")
        return None
    except Exception as e:
        logger.error(f"DOCX conversion error: {e}")
        return None

def log_transaction(session_id, trans_type, amount, description):
    """Log transaction to database"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO transactions (session_id, type, amount, description) VALUES (?, ?, ?, ?)',
        (session_id, trans_type, amount, description)
    )
    db.commit()
    db.close()
    logger.info(f"Transaction logged: {session_id} - {trans_type} - ₱{amount}")

def update_user_activity(session_id):
    """Update user's last activity timestamp"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'UPDATE users SET last_activity = CURRENT_TIMESTAMP WHERE session_id = ?',
        (session_id,)
    )
    db.commit()
    db.close()

def get_printer_name():
    """Get the default printer name from CUPS"""
    try:
        if conn_cups:
            printers = conn_cups.getPrinters()
            if printers:
                # Return first available printer or DEFAULT_PRINTER if exists
                if DEFAULT_PRINTER in printers:
                    return DEFAULT_PRINTER
                return list(printers.keys())[0]
        return None
    except Exception as e:
        logger.error(f"Error getting printer: {e}")
        return None

# ============================================
# API Routes
# ============================================

@app.route('/')
def index():
    """Home page / API info"""
    return jsonify({
        'status': 'online',
        'message': 'Piso Print Server Running',
        'version': '2.0',
        'endpoints': {
            'upload': '/upload (POST)',
            'print': '/print (POST)',
            'credits': '/api/credits (POST)',
            'check_credits': '/api/check_credits (GET)',
            'status': '/api/status (GET)',
            'history': '/api/history (GET)'
        }
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload from ESP32"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            logger.warning("No file in upload request")
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            logger.warning("Empty filename in upload")
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            logger.warning(f"Invalid file type: {file.filename}")
            return jsonify({
                'success': False,
                'error': 'File type not allowed'
            }), 400
        
        # Get session ID from form data or create new one
        session_id = request.form.get('session_id', f"USER_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        
        # Secure filename and save
        original_filename = file.filename
        filename = secure_filename(file.filename)
        
        # Add timestamp to avoid conflicts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{timestamp}{ext}"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        file_size = os.path.getsize(filepath)
        file_ext = ext[1:] if ext else 'unknown'
        
        # Count pages
        pages = count_file_pages(filepath, file_ext)
        cost = pages * PRICE_PER_PAGE
        
        # Save to database
        db = get_db()
        cursor = db.cursor()
        
        # Ensure user exists
        get_or_create_user(session_id)
        
        cursor.execute('''
            INSERT INTO files (session_id, filename, original_name, file_path, file_size, pages, file_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (session_id, filename, original_filename, filepath, file_size, pages, file_ext))
        
        db.commit()
        file_id = cursor.lastrowid
        db.close()
        
        logger.info(f"File uploaded: {original_filename} ({pages} pages) - Session: {session_id}")
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'filename': filename,
            'pages': pages,
            'cost': cost,
            'message': f'{pages} page(s) = ₱{cost}'
        })
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/print', methods=['POST'])
def print_file():
    """Handle print request from ESP32"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        user_credits = data.get('credits', 0)
        filename = data.get('filename', '')  # Get filename from ESP32
        
        if not session_id:
            return jsonify({
                'success': False,
                'message': 'No session ID provided'
            }), 400
        
        logger.info(f"Print request: Session={session_id}, Credits={user_credits}, File={filename}")
        
        # Get user from database
        user = get_or_create_user(session_id)
        db_credits = user['credits']
        
        # Get the latest uploaded file for this session
        db = get_db()
        cursor = db.cursor()
        
        if filename:
            # Use the specific filename if provided
            cursor.execute('''
                SELECT * FROM files 
                WHERE session_id = ? AND filename = ?
                ORDER BY uploaded_at DESC 
                LIMIT 1
            ''', (session_id, filename))
        else:
            # Fall back to latest file
            cursor.execute('''
                SELECT * FROM files 
                WHERE session_id = ? 
                ORDER BY uploaded_at DESC 
                LIMIT 1
            ''', (session_id,))
        
        file_record = cursor.fetchone()
        
        if not file_record:
            db.close()
            logger.warning(f"No file found for session {session_id}")
            return jsonify({
                'success': False,
                'message': 'No file uploaded yet'
            }), 400
        
        file_record = dict(file_record)
        pages = file_record['pages']
        cost = pages * PRICE_PER_PAGE
        
        logger.info(f"File found: {file_record['filename']} - {pages} pages - ₱{cost}")
        
        # Check if user has enough credits (use ESP32's credit count)
        if user_credits < cost:
            db.close()
            logger.warning(f"Insufficient credits: has ₱{user_credits}, needs ₱{cost}")
            return jsonify({
                'success': False,
                'message': f'Insufficient credits. Need ₱{cost}, have ₱{user_credits}'
            }), 400
        
        # Get printer
        printer_name = get_printer_name()
        if not printer_name:
            db.close()
            return jsonify({
                'success': False,
                'message': 'No printer available'
            }), 500
        
        # Print the file using CUPS
        try:
            filepath = file_record['file_path']
            file_ext = file_record['file_type'].lower()
            
            # Convert DOCX to PDF if needed
            if file_ext in ['doc', 'docx']:
                logger.info(f"Converting DOCX to PDF: {filepath}")
                pdf_path = convert_docx_to_pdf(filepath)
                
                if pdf_path and os.path.exists(pdf_path):
                    filepath = pdf_path
                    logger.info(f"Using converted PDF: {filepath}")
                else:
                    logger.warning("DOCX conversion failed, attempting to print original file")
            
            if conn_cups:
                job_id = conn_cups.printFile(
                    printer_name,
                    filepath,
                    f"PisoPrint_{session_id}",
                    {}
                )
                logger.info(f"Print job created: ID={job_id}, Printer={printer_name}, File={filepath}")
            else:
                # Fallback: use command line
                subprocess.run(['lp', '-d', printer_name, filepath], check=True)
                job_id = 0
                logger.info(f"Print job sent via lp command: {filepath}")
            
            # Record print job
            cursor.execute('''
                INSERT INTO print_jobs (session_id, file_id, pages, cost, status)
                VALUES (?, ?, ?, ?, 'printing')
            ''', (session_id, file_record['id'], pages, cost))
            
            # Deduct credits from database
            cursor.execute('''
                UPDATE users 
                SET credits = credits - ? 
                WHERE session_id = ?
            ''', (cost, session_id))
            
            # Log transaction
            cursor.execute('''
                INSERT INTO transactions (session_id, type, amount, description)
                VALUES (?, 'deduct', ?, ?)
            ''', (session_id, cost, f'Print {pages} page(s)'))
            
            db.commit()
            db.close()
            
            logger.info(f"Print successful: {session_id} - {pages} pages - ₱{cost} deducted")
            
            return jsonify({
                'success': True,
                'job_id': job_id,
                'pages': pages,
                'cost': cost,
                'remaining_credits': user_credits - cost,
                'message': 'Printing...'
            })
            
        except Exception as print_error:
            db.close()
            logger.error(f"Print error: {print_error}")
            return jsonify({
                'success': False,
                'message': f'Print failed: {str(print_error)}'
            }), 500
        
    except Exception as e:
        logger.error(f"Print request error: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/credits', methods=['POST'])
def add_credits():
    """Add credits when coins are inserted"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        amount = data.get('amount', 0)
        
        if not session_id or amount <= 0:
            return jsonify({
                'success': False,
                'message': 'Invalid session or amount'
            }), 400
        
        # Ensure user exists
        get_or_create_user(session_id)
        
        # Add credits
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            UPDATE users 
            SET credits = credits + ?, last_activity = CURRENT_TIMESTAMP 
            WHERE session_id = ?
        ''', (amount, session_id))
        
        # Get new balance
        cursor.execute('SELECT credits FROM users WHERE session_id = ?', (session_id,))
        new_balance = cursor.fetchone()['credits']
        
        db.commit()
        db.close()
        
        # Log transaction
        log_transaction(session_id, 'add', amount, f'Coin inserted: ₱{amount}')
        
        logger.info(f"Credits added: {session_id} +₱{amount} = ₱{new_balance}")
        
        return jsonify({
            'success': True,
            'amount': amount,
            'new_balance': new_balance,
            'message': f'₱{amount} added'
        })
        
    except Exception as e:
        logger.error(f"Add credits error: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/check_credits', methods=['GET'])
def check_credits():
    """Check user credits"""
    try:
        session_id = request.args.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'message': 'No session ID provided'
            }), 400
        
        user = get_or_create_user(session_id)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'credits': user['credits']
        })
        
    except Exception as e:
        logger.error(f"Check credits error: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/check_pages', methods=['POST'])
def check_pages():
    """Check page count for a file (ESP32 sends filename, we estimate pages)"""
    try:
        data = request.get_json()
        filename = data.get('filename', '')
        session_id = data.get('session_id', '')
        
        if not filename:
            return jsonify({
                'success': False,
                'error': 'No filename provided'
            }), 400
        
        logger.info(f"Page count request: {filename} (Session: {session_id})")
        
        # Estimate pages based on file extension
        # Since we don't have the actual file content, we'll estimate
        file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        estimated_pages = 1  # Default
        
        if file_ext == 'pdf':
            # For PDF, estimate 3 pages (user can override later)
            estimated_pages = 3
        elif file_ext in ['doc', 'docx']:
            # For Word docs, estimate 2 pages
            estimated_pages = 2
        elif file_ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
            # Images are 1 page
            estimated_pages = 1
        else:
            # Unknown type, assume 1 page
            estimated_pages = 1
        
        logger.info(f"Estimated {estimated_pages} page(s) for {filename}")
        
        return jsonify({
            'success': True,
            'pages': estimated_pages,
            'filename': filename,
            'message': f'{estimated_pages} page(s) estimated'
        })
        
    except Exception as e:
        logger.error(f"Page check error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def system_status():
    """Get system status"""
    try:
        # Get printer status
        printer_status = 'offline'
        printer_name = None
        
        if conn_cups:
            printers = conn_cups.getPrinters()
            if printers:
                printer_name = get_printer_name()
                printer_status = 'online'
        
        # Get database stats
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM users')
        total_users = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM print_jobs')
        total_prints = cursor.fetchone()['count']
        
        cursor.execute('SELECT SUM(cost) as total FROM print_jobs')
        total_revenue = cursor.fetchone()['total'] or 0
        
        db.close()
        
        return jsonify({
            'status': 'online',
            'printer': {
                'status': printer_status,
                'name': printer_name
            },
            'stats': {
                'total_users': total_users,
                'total_prints': total_prints,
                'total_revenue': total_revenue
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Status error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get print history"""
    try:
        session_id = request.args.get('session_id')
        limit = request.args.get('limit', 10)
        
        db = get_db()
        cursor = db.cursor()
        
        if session_id:
            # Get history for specific session
            cursor.execute('''
                SELECT p.*, f.original_name, f.file_type
                FROM print_jobs p
                JOIN files f ON p.file_id = f.id
                WHERE p.session_id = ?
                ORDER BY p.printed_at DESC
                LIMIT ?
            ''', (session_id, limit))
        else:
            # Get all history
            cursor.execute('''
                SELECT p.*, f.original_name, f.file_type
                FROM print_jobs p
                JOIN files f ON p.file_id = f.id
                ORDER BY p.printed_at DESC
                LIMIT ?
            ''', (limit,))
        
        history = [dict(row) for row in cursor.fetchall()]
        db.close()
        
        return jsonify({
            'success': True,
            'history': history,
            'count': len(history)
        })
        
    except Exception as e:
        logger.error(f"History error: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# ============================================
# Error Handlers
# ============================================

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size is 50MB'
    }), 413

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

# ============================================
# Run Server
# ============================================
if __name__ == '__main__':
    print("\n" + "="*50)
    print("🖨️  PISO PRINT SERVER v2.0")
    print("="*50)
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print(f"🗄️  Database: {DATABASE}")
    print(f"🖨️  Printer: {get_printer_name() or 'Not configured'}")
    print(f"💰 Price: ₱{PRICE_PER_PAGE} per page")
    print("="*50)
    print("🌐 Starting server on http://0.0.0.0:5000")
    print("="*50 + "\n")
    
    # Run Flask server
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
