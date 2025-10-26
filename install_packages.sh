#!/bin/bash
# Installation script for Piso Print Python packages
# Run this on Orange Pi after cloning the repository

echo "╔══════════════════════════════════════════════════╗"
echo "║   📦 Installing Python Packages for Piso Print  ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found!"
    echo "Please run this script from the piso-print directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📁 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install essential packages
echo ""
echo "📦 Installing Flask and core dependencies..."
pip install flask==3.0.0 || { echo "❌ Flask installation failed"; exit 1; }
pip install flask-cors==4.0.0 || { echo "⚠️  flask-cors installation failed"; }
pip install werkzeug==3.0.1 || { echo "⚠️  werkzeug installation failed"; }

# Install document processing libraries
echo ""
echo "📦 Installing document processing libraries..."
pip install PyPDF2==3.0.1 || { echo "⚠️  PyPDF2 installation failed - PDF support disabled"; }
pip install python-docx==1.1.0 || { echo "⚠️  python-docx installation failed - DOCX support disabled"; }
pip install pillow==10.1.0 || { echo "⚠️  Pillow installation failed - Image support limited"; }

# Install CUPS support
echo ""
echo "📦 Installing printer (CUPS) support..."
echo "   (This may require system packages - installing them first...)"

# Check if libcups2-dev is installed
if ! dpkg -l | grep -q libcups2-dev; then
    echo "   Installing CUPS development headers..."
    sudo apt-get update --fix-missing
    sudo apt-get install -y libcups2-dev build-essential python3-dev
fi

# Try installing pycups
pip install pycups==2.0.1 || {
    echo "⚠️  pycups installation failed"
    echo "   Printer functionality will be limited"
    echo "   The server will still work, but won't be able to communicate with CUPS"
}

# Display installed packages
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║          ✅ Installation Complete!               ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
echo "📋 Installed packages:"
pip list | grep -E "Flask|flask-cors|Werkzeug|PyPDF2|python-docx|Pillow|pycups" | sed 's/^/   /'

echo ""
echo "🚀 Next steps:"
echo "   1. Test the server: python app.py"
echo "   2. Check for errors in the output"
echo "   3. If CUPS warnings appear, install printer drivers"
echo "   4. Configure your printer in CUPS: http://localhost:631"
echo ""

# Check if Flask imports work
echo "🧪 Testing imports..."
python -c "from flask import Flask; print('   ✅ Flask: OK')" || echo "   ❌ Flask: FAILED"
python -c "import PyPDF2; print('   ✅ PyPDF2: OK')" 2>/dev/null || echo "   ⚠️  PyPDF2: Not available"
python -c "from docx import Document; print('   ✅ python-docx: OK')" 2>/dev/null || echo "   ⚠️  python-docx: Not available"
python -c "from PIL import Image; print('   ✅ Pillow: OK')" 2>/dev/null || echo "   ⚠️  Pillow: Not available"
python -c "import cups; print('   ✅ pycups: OK')" 2>/dev/null || echo "   ⚠️  pycups: Not available (optional)"

echo ""
echo "💡 Tip: If any warnings appear, the server will still run"
echo "    Missing libraries only disable specific features"
echo ""
