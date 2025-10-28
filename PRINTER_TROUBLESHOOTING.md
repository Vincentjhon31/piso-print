# Printer Not Printing - Troubleshooting Guide

## Current Status

✅ File uploaded successfully  
✅ Flask receives print request  
✅ CUPS job created (Job ID: 2)  
❌ **Printer not actually printing**

---

## Step 1: Run Diagnostics on Orange Pi

```bash
cd ~/piso-print
chmod +x check_printer.sh
./check_printer.sh
```

This will show you the printer status and any errors.

---

## Step 2: Common Issues & Quick Fixes

### Issue A: Printer is Paused or Disabled

**Check:**

```bash
lpstat -p PisoPrinter
```

**If you see "disabled" or "paused":**

```bash
cupsenable PisoPrinter
cupsaccept PisoPrinter
```

### Issue B: USB Cable Disconnected

**Check:**

```bash
lsusb | grep -i canon
```

**Should see something like:**

```
Bus 001 Device 004: ID 04a9:xxxx Canon, Inc. G3000 series
```

**If NOT visible:**

- Check USB cable connection
- Try different USB port
- Power cycle the printer
- Run: `sudo systemctl restart cups`

### Issue C: Wrong Printer Driver (Most Common!)

The generic PPD driver might not work with Canon G3000. Let's install the proper driver:

```bash
# Install Canon driver dependencies
sudo apt update
sudo apt install -y cups libcups2 libcupsimage2

# Download Canon G3000 driver (if available)
# OR use gutenprint driver which supports many Canon printers
sudo apt install -y printer-driver-gutenprint

# Remove old printer
lpadmin -x PisoPrinter

# Re-add with gutenprint driver
sudo lpadmin -p PisoPrinter \
  -E \
  -v "usb://Canon/G3000%20series" \
  -m "gutenprint.5.3://canon-pixma_mg3500/expert" \
  -o printer-is-shared=false

# Enable and accept jobs
cupsenable PisoPrinter
cupsaccept PisoPrinter
```

### Issue D: Test Print to Verify Printer Works

```bash
# Simple text test
echo "Test Print from Orange Pi" | lp -d PisoPrinter

# PDF test page
lp -d PisoPrinter /usr/share/cups/data/testprint
```

**If test print works but app doesn't:**

- Check file permissions in `/home/orangepi/piso-print/uploads/`
- Verify Flask has access to the files

### Issue E: Check CUPS Error Logs

```bash
sudo tail -f /var/log/cups/error_log
```

Then try printing from the app again and watch for errors in real-time.

### Issue F: Check Flask Logs

While Flask is running:

```bash
# In the Flask terminal, you should see:
# INFO - Print job created: ID=2, Printer=PisoPrinter, File=/path/to/file.pdf
```

---

## Step 3: Verify Print Job Status

```bash
# Check current print jobs
lpstat -o

# Check completed jobs
lpstat -W completed -o

# Check failed jobs
lpstat -W completed -o | grep -i error
```

---

## Step 4: Manual Print Test

Try printing your uploaded file manually:

```bash
# Find your uploaded file
ls -lh ~/piso-print/uploads/

# Print it manually
lp -d PisoPrinter ~/piso-print/uploads/SAMPLESmall_20251026_221046.pdf
```

**If manual print works:**

- Problem is in Flask/CUPS connection
- Check if Flask user has printer permissions

**If manual print fails:**

- Problem is with CUPS/printer setup
- Follow Issue C above to reinstall printer with proper driver

---

## Step 5: Check Flask/CUPS Connection

In your Flask code, we use `pycups`. Verify it's working:

```bash
cd ~/piso-print
source venv/bin/activate
python3 << EOF
import cups
conn = cups.Connection()
printers = conn.getPrinters()
print("Available printers:", list(printers.keys()))
print("Default printer:", conn.getDefault())
for printer in printers:
    print(f"\nPrinter: {printer}")
    print(f"State: {printers[printer]['printer-state']}")
    print(f"Status: {printers[printer]['printer-state-message']}")
EOF
```

Expected output:

```
Available printers: ['PisoPrinter']
Default printer: PisoPrinter
Printer: PisoPrinter
State: 3
Status: idle
```

---

## Step 6: Permission Issues

Ensure the user running Flask has printer access:

```bash
# Add user to lpadmin group
sudo usermod -a -G lpadmin orangepi

# Verify
groups orangepi

# Restart Flask after adding to group
```

---

## Step 7: Restart Everything

Sometimes a full restart fixes things:

```bash
# Stop Flask (Ctrl+C in Flask terminal)

# Restart CUPS
sudo systemctl restart cups

# Power cycle printer (turn off, wait 10 seconds, turn on)

# Check USB reconnection
lsusb | grep -i canon

# Start Flask again
cd ~/piso-print
source venv/bin/activate
python3 app.py
```

---

## Step 8: Enable CUPS Web Interface (Advanced)

Access CUPS admin panel from your computer:

1. On Orange Pi:

```bash
sudo cupsctl --remote-admin --remote-any --share-printers
sudo systemctl restart cups
```

2. On your computer, open browser:

```
http://192.168.22.2:631
```

3. Go to "Administration" → "Printers" → "PisoPrinter"
4. Check printer status and settings

---

## Most Likely Solution

Based on your output (Job ID created but nothing prints), the issue is usually:

**Wrong printer driver** - The generic driver doesn't work with Canon G3000.

Run these commands on Orange Pi:

```bash
# Install proper Canon/Gutenprint drivers
sudo apt install -y printer-driver-gutenprint cups-filters

# Remove and re-add printer
lpadmin -x PisoPrinter

# Add with better driver
sudo lpadmin -p PisoPrinter \
  -E \
  -v "usb://Canon/G3000%20series" \
  -m "gutenprint.5.3://canon-pixma_mg3500/expert" \
  -o printer-is-shared=false

# Enable
cupsenable PisoPrinter
cupsaccept PisoPrinter

# Test
echo "Test" | lp -d PisoPrinter
```

---

## Still Not Working?

Share the output of these commands:

```bash
# 1. Printer status
lpstat -p -v PisoPrinter

# 2. Recent error log
sudo tail -n 50 /var/log/cups/error_log

# 3. Job history
lpstat -W completed -o

# 4. USB device
lsusb | grep -i canon
```

Paste the output and I'll help debug further!
