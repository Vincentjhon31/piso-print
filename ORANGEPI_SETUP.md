# 🍊 Orange Pi Quick Start Guide

## Prerequisites

- Orange Pi PC H3 with Armbian OS installed
- MicroSD card (32GB recommended)
- USB Printer connected
- Network connection (Ethernet or Wi-Fi)

## Step 1: Transfer Files to Orange Pi

### Option A: Using USB Drive

1. Copy these files to a USB drive:

   - `app.py`
   - `requirements.txt`
   - `setup_orangepi.sh`

2. Insert USB drive into Orange Pi
3. Mount and copy files:

```bash
sudo mkdir /mnt/usb
sudo mount /dev/sda1 /mnt/usb
sudo cp /mnt/usb/app.py /home/pisoprint/
sudo cp /mnt/usb/setup_orangepi.sh /home/
```

### Option B: Using SCP (if you have network)

```bash
# From your computer
scp app.py root@<orangepi-ip>:/home/pisoprint/
scp setup_orangepi.sh root@<orangepi-ip>:/home/
```

### Option C: Using Git

```bash
ssh root@<orangepi-ip>
cd /home/pisoprint
git clone https://github.com/Vincentjhon31/piso-print.git
cd piso-print
```

## Step 2: Run Setup Script

```bash
ssh root@<orangepi-ip>
cd /home
chmod +x setup_orangepi.sh
sudo ./setup_orangepi.sh
```

This will:

- Update the system
- Install Python, Flask, CUPS
- Create virtual environment
- Install all dependencies
- Configure CUPS
- Create systemd service

**Installation takes ~15-20 minutes**

## Step 3: Configure Printer

### A. Using CUPS Web Interface (Recommended)

1. Open browser and go to:

   ```
   http://<orangepi-ip>:631
   ```

2. Click **Administration** → **Add Printer**

3. Select your USB printer (e.g., "Canon Pixma G3000")

4. Follow the wizard:

   - Name: `PisoPrinter`
   - Share: ✅ Check "Share This Printer"
   - Location: `Piso Print Kiosk`

5. Select driver (use recommended or generic)

6. Click **Set Default Options**

### B. Using Command Line

```bash
# List available printers
lpinfo -v

# Example output:
# usb://Canon/Pixma%20G3000?serial=ABC123

# Add printer
sudo lpadmin -p PisoPrinter -E -v "usb://Canon/Pixma%20G3000?serial=ABC123" -m everywhere

# Set as default
sudo lpoptions -d PisoPrinter

# Test print
echo "Test from Piso Print" | lp
```

## Step 4: Update app.py Configuration

Edit `/home/pisoprint/app.py` and update:

```python
DEFAULT_PRINTER = 'PisoPrinter'  # Change to your printer name
```

## Step 5: Start the Service

```bash
# Copy app.py to correct location (if not already there)
sudo cp app.py /home/pisoprint/

# Start the service
sudo systemctl start pisoprint.service

# Check status
sudo systemctl status pisoprint.service

# Should show: Active: active (running)
```

## Step 6: Test the Server

```bash
# Test from Orange Pi
curl http://localhost:5000

# Should return:
# {
#   "status": "online",
#   "message": "Piso Print Server Running",
#   ...
# }
```

## Step 7: Connect ESP32

1. Update ESP32 code with Orange Pi IP:

```cpp
const char* FLASK_SERVER = "http://192.168.4.2:5000";
```

2. Connect ESP32 to same network as Orange Pi

3. Test upload:
   - Connect phone to ESP32 WiFi
   - Upload a test PDF
   - Check Orange Pi logs:
     ```bash
     sudo journalctl -u pisoprint.service -f
     ```

## Troubleshooting

### Server won't start

```bash
# Check logs
sudo journalctl -u pisoprint.service -n 50

# Common issues:
# 1. Port 5000 already in use
sudo netstat -tulpn | grep 5000

# 2. Python packages missing
source /home/pisoprint/venv/bin/activate
pip list

# 3. Permission issues
sudo chmod -R 755 /home/pisoprint
sudo chown -R root:root /home/pisoprint
```

### Printer not detected

```bash
# Check if printer is connected
lsusb

# Check CUPS status
sudo systemctl status cups

# Restart CUPS
sudo systemctl restart cups

# Check printer queue
lpstat -p -d
```

### Database issues

```bash
# Check database
sqlite3 /home/pisoprint/pisoprint.db

# In SQLite prompt:
.tables
SELECT * FROM users;
.quit
```

### Network issues

```bash
# Check IP address
ip addr show

# Test connectivity
ping 192.168.4.1  # ESP32
ping 8.8.8.8      # Internet

# Check firewall
sudo ufw status
sudo ufw allow 5000/tcp
```

## Useful Commands

```bash
# View real-time logs
sudo journalctl -u pisoprint.service -f

# Restart service
sudo systemctl restart pisoprint.service

# Stop service
sudo systemctl stop pisoprint.service

# Check printer queue
lpstat -o

# Cancel all print jobs
cancel -a

# Check disk space
df -h

# Check uploads folder
ls -lh /home/pisoprint/uploads/

# View database
sqlite3 /home/pisoprint/pisoprint.db "SELECT * FROM print_jobs ORDER BY printed_at DESC LIMIT 5;"

# System resources
htop

# Network connections
sudo netstat -tulpn | grep :5000
```

## Success Indicators

✅ **Server is running:**

```bash
sudo systemctl status pisoprint.service
# Active: active (running)
```

✅ **Printer is ready:**

```bash
lpstat -p
# printer PisoPrinter is idle
```

✅ **API responds:**

```bash
curl http://localhost:5000
# {"status": "online", ...}
```

✅ **Database exists:**

```bash
ls -lh /home/pisoprint/pisoprint.db
# -rw-r--r-- 1 root root 12K ...
```

## Next Steps

1. ✅ Orange Pi setup complete
2. ✅ Flask server running
3. ✅ Printer configured
4. 🔄 Test full workflow:

   - Connect phone to ESP32
   - Upload file
   - Insert coins
   - Print document

5. 📊 Monitor the system:
   - Check logs regularly
   - Monitor disk space
   - Test printer daily

## Support

If you encounter issues:

1. Check logs: `sudo journalctl -u pisoprint.service -f`
2. Verify printer: `lpstat -p -d`
3. Test manually: `curl http://localhost:5000`
4. Check README.md for detailed troubleshooting

---

**Your Orange Pi is now ready to handle print jobs from the ESP32!** 🎉
