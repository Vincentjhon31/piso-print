#!/bin/bash
# Printer Diagnostic Script for Orange Pi

echo "=================================="
echo "PISO PRINT - PRINTER DIAGNOSTICS"
echo "=================================="
echo ""

echo "1. Checking CUPS Service Status:"
systemctl status cups | grep -E "(Active|Loaded)"
echo ""

echo "2. Checking Printer Status:"
lpstat -p -d
echo ""

echo "3. Checking Print Jobs:"
lpstat -o
echo ""

echo "4. Checking CUPS Error Log (last 20 lines):"
sudo tail -n 20 /var/log/cups/error_log
echo ""

echo "5. Checking USB Printer Connection:"
lsusb | grep -i canon
echo ""

echo "6. Checking Printer Configuration:"
lpstat -v
echo ""

echo "7. Testing Printer with Test Page:"
echo "Would you like to print a test page? (This will help diagnose)"
echo "Run: echo 'Test Print' | lp -d PisoPrinter"
echo ""

echo "8. Checking Recent Print Jobs Status:"
lpstat -W completed -o
echo ""

echo "=================================="
echo "COMMON ISSUES & SOLUTIONS:"
echo "=================================="
echo ""
echo "Issue 1: Printer is 'paused' or 'disabled'"
echo "  Fix: cupsenable PisoPrinter"
echo "       cupsaccept PisoPrinter"
echo ""
echo "Issue 2: USB cable disconnected"
echo "  Fix: Check USB cable connection"
echo "       Restart printer"
echo ""
echo "Issue 3: Wrong printer driver"
echo "  Fix: Reinstall printer with correct PPD"
echo ""
echo "Issue 4: CUPS service stopped"
echo "  Fix: sudo systemctl restart cups"
echo ""
echo "Issue 5: Permission issues"
echo "  Fix: sudo usermod -a -G lpadmin $USER"
echo ""
