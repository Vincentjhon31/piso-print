# 🔧 Troubleshooting Guide - Orange Pi Setup

This guide helps you fix common issues when setting up Piso Print on Orange Pi.

---

## ❌ Error: "No module named 'flask'"

**Problem:** Flask is not installed in the virtual environment.

**Solution:**

```bash
cd /root/piso-print
source venv/bin/activate
pip install -r requirements.txt
```

Or run the installation script:

```bash
chmod +x install_packages.sh
./install_packages.sh
```

---

## ❌ Error: "Unable to access GitHub repository"

**Problem:** Network connectivity or SSL certificate issues.

**Solutions:**

### Option 1: Fix SSL Certificates
```bash
sudo apt-get install -y ca-certificates
sudo update-ca-certificates
```

### Option 2: Download ZIP Instead
```bash
# On your computer, download:
# https://github.com/Vincentjhon31/piso-print/archive/refs/heads/main.zip

# Copy to USB drive, then on Orange Pi:
sudo mount /dev/sda1 /mnt
cp /mnt/piso-print-main.zip /root/
cd /root
unzip piso-print-main.zip
mv piso-print-main piso-print
```

### Option 3: Clone Without SSL Verification (Temporary)
```bash
git config --global http.sslVerify false
git clone https://github.com/Vincentjhon31/piso-print.git
git config --global http.sslVerify true
```

---

## ⚠️ Warning: "pycups not available"

**Problem:** CUPS development headers not installed.

**Solution:**

```bash
sudo apt-get update
sudo apt-get install -y libcups2-dev build-essential python3-dev
source venv/bin/activate
pip install pycups
```

**Note:** The server will still work without pycups, but printer functionality will be limited.

---

## ❌ Error: "Failed to fetch" during apt update

**Problem:** Armbian repository connectivity issues.

**Solutions:**

### Option 1: Skip Failed Repositories
```bash
sudo apt-get update --fix-missing
sudo apt-get install -y python3 python3-pip python3-venv
```

### Option 2: Comment Out Problem Repos
```bash
sudo nano /etc/apt/sources.list.d/armbian.list

# Add # at the start of lines with errors
#deb https://github.armbian.com/ focal main

# Save: Ctrl+O, Enter, Ctrl+X
sudo apt-get update
```

### Option 3: Use Force IPv4
```bash
sudo apt-get update -o Acquire::ForceIPv4=true
```

---

## ❌ Error: "Permission denied" when running scripts

**Solution:**

```bash
chmod +x install_packages.sh
chmod +x setup_orangepi.sh

# Or fix all permissions
sudo chmod -R 755 /root/piso-print
```

---

## ❌ Error: "Database is locked"

**Problem:** Multiple instances of app.py running.

**Solution:**

```bash
# Find running Python processes
ps aux | grep app.py

# Kill them
sudo killall python3

# Or kill specific PID
sudo kill -9 <PID>

# Restart
python app.py
```

---

## ⚠️ Warning: "CUPS connection failed"

**Problem:** CUPS service not running or not installed.

**Solution:**

```bash
# Install CUPS
sudo apt-get install -y cups printer-driver-all

# Start CUPS service
sudo systemctl enable cups
sudo systemctl start cups

# Check status
sudo systemctl status cups

# Add user to lpadmin group
sudo usermod -aG lpadmin $USER
```

---

## 🖨️ Printer Not Showing Up

**Solution:**

```bash
# List printers
lpstat -p -d

# If no printers:
# 1. Connect USB printer
# 2. Open CUPS web interface: http://localhost:631
# 3. Go to Administration > Add Printer
# 4. Follow the wizard

# Update printer name in app.py if needed
nano /root/piso-print/app.py
# Change: DEFAULT_PRINTER = 'YourPrinterName'
```

---

## 🌐 Can't Access Server from ESP32

**Problem:** Firewall blocking port 5000.

**Solution:**

```bash
# Check if server is running
netstat -tulpn | grep 5000

# Allow port 5000 through firewall
sudo ufw allow 5000

# Or disable firewall temporarily for testing
sudo ufw disable

# Find Orange Pi IP address
ip addr show

# Test from ESP32 or another device
curl http://<orange-pi-ip>:5000
```

---

## 🐍 Virtual Environment Not Activating

**Solution:**

```bash
# Delete and recreate
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# You should see (venv) in prompt
```

---

## 📦 Pip Install Fails with "externally-managed-environment"

**Problem:** Debian/Ubuntu preventing system-wide pip installs.

**Solution:** Always use virtual environment:

```bash
cd /root/piso-print
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🔄 Service Won't Start on Boot

**Problem:** Systemd service not configured correctly.

**Solution:**

```bash
# Check service status
sudo systemctl status pisoprint.service

# View logs
sudo journalctl -u pisoprint.service -n 50

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl enable pisoprint.service
sudo systemctl restart pisoprint.service
```

---

## 💾 Database Errors

**Solution:**

```bash
# Backup database
cp /root/piso-print/pisoprint.db /root/piso-print/pisoprint.db.backup

# Reset database (CAUTION: deletes all data)
rm /root/piso-print/pisoprint.db

# Restart server (will recreate database)
python app.py
```

---

## 🧪 Testing Commands

```bash
# Test server is running
curl http://localhost:5000

# Test upload endpoint
curl -X POST http://localhost:5000/upload

# Test status
curl http://localhost:5000/api/status

# Run automated tests
cd /root/piso-print
source venv/bin/activate
python test_server.py
```

---

## 📋 Useful Diagnostic Commands

```bash
# Check Python version
python3 --version

# Check installed packages
pip list

# Check system info
cat /etc/armbian-release

# Check network
ip addr show
ping google.com

# Check disk space
df -h

# Check memory
free -h

# View server logs
tail -f /root/piso-print/logs/server.log

# View error logs
tail -f /root/piso-print/logs/error.log
```

---

## 🆘 Still Having Issues?

1. **Check the full error message** - Copy the entire error output
2. **Check system logs**: `dmesg | tail -n 50`
3. **Verify all prerequisites are installed**
4. **Try running with verbose output**: `python app.py 2>&1 | tee debug.log`
5. **Check GitHub issues**: https://github.com/Vincentjhon31/piso-print/issues

---

## 📞 Common Error Messages and Quick Fixes

| Error | Quick Fix |
|-------|-----------|
| `ModuleNotFoundError: No module named 'flask'` | `pip install flask` |
| `Permission denied` | `sudo chmod +x script.sh` |
| `Address already in use` | `sudo killall python3` |
| `Database is locked` | `sudo killall python3` |
| `CUPS connection failed` | `sudo systemctl start cups` |
| `Unable to access GitHub` | Download ZIP instead |
| `SSL certificate problem` | `sudo update-ca-certificates` |

---
