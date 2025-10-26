#!/bin/bash

# ============================================
# Piso Print Orange Pi Setup Script
# ============================================

echo "============================================"
echo "🖨️  Piso Print - Orange Pi Setup"
echo "============================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
  echo -e "${RED}Please run as root (use sudo)${NC}"
  exit 1
fi

echo ""
echo "Step 1: Updating system..."
apt update
apt upgrade -y

echo ""
echo "Step 2: Installing Python and dependencies..."
apt install -y python3 python3-pip python3-venv python3-dev

echo ""
echo "Step 3: Installing CUPS (printing system)..."
apt install -y cups printer-driver-all libcups2-dev

echo ""
echo "Step 4: Installing system utilities..."
apt install -y git sqlite3 htop build-essential

echo ""
echo "Step 5: Creating project directory..."
mkdir -p /home/pisoprint/uploads
cd /home/pisoprint

echo ""
echo "Step 6: Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo ""
echo "Step 7: Installing Python packages..."
pip install --upgrade pip
pip install Flask==3.0.0
pip install Flask-CORS==4.0.0
pip install pycups==2.0.1
pip install PyPDF2==3.0.1
pip install python-docx==1.1.0
pip install Pillow==10.1.0
pip install Werkzeug==3.0.1

echo ""
echo "Step 8: Configuring CUPS..."
# Add current user to lpadmin group
usermod -a -G lpadmin root

# Backup original config
cp /etc/cups/cupsd.conf /etc/cups/cupsd.conf.backup

# Configure CUPS to listen on all interfaces
sed -i 's/Listen localhost:631/Listen 0.0.0.0:631/' /etc/cups/cupsd.conf

# Allow access from local network
sed -i '/<Location \/>/a\  Allow @LOCAL' /etc/cups/cupsd.conf
sed -i '/<Location \/admin>/a\  Allow @LOCAL' /etc/cups/cupsd.conf

# Restart CUPS
systemctl restart cups
systemctl enable cups

echo ""
echo "Step 9: Setting up permissions..."
chmod -R 755 /home/pisoprint
chown -R root:root /home/pisoprint

echo ""
echo "Step 10: Creating systemd service..."
cat > /etc/systemd/system/pisoprint.service << 'EOF'
[Unit]
Description=Piso Print Flask Server
After=network.target cups.service

[Service]
Type=simple
User=root
WorkingDirectory=/home/pisoprint
Environment="PATH=/home/pisoprint/venv/bin"
ExecStart=/home/pisoprint/venv/bin/python /home/pisoprint/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable pisoprint.service

echo ""
echo "============================================"
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Copy app.py to /home/pisoprint/"
echo "2. Connect your USB printer"
echo "3. Add printer via CUPS web interface:"
echo "   http://$(hostname -I | awk '{print $1}'):631"
echo "4. Start the service:"
echo "   sudo systemctl start pisoprint.service"
echo "5. Check status:"
echo "   sudo systemctl status pisoprint.service"
echo ""
echo "View logs:"
echo "   sudo journalctl -u pisoprint.service -f"
echo ""
echo "Test the server:"
echo "   curl http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "============================================"
