#!/bin/bash
# Quick Printer Fix Script

echo "🖨️  PISO PRINT - Quick Printer Fix"
echo "===================================="
echo ""

# Check if printer exists
if lpstat -p PisoPrinter &> /dev/null; then
    echo "✅ Printer 'PisoPrinter' found"
    
    # Check printer state
    STATUS=$(lpstat -p PisoPrinter)
    echo "📊 Status: $STATUS"
    
    # Enable if disabled
    if echo "$STATUS" | grep -q "disabled"; then
        echo "⚠️  Printer is disabled. Enabling..."
        cupsenable PisoPrinter
        echo "✅ Printer enabled"
    fi
    
    # Accept jobs if not accepting
    if ! lpstat -a | grep -q "PisoPrinter accepting"; then
        echo "⚠️  Printer not accepting jobs. Fixing..."
        cupsaccept PisoPrinter
        echo "✅ Printer now accepting jobs"
    fi
else
    echo "❌ Printer 'PisoPrinter' not found!"
    echo "   Run setup again or check TROUBLESHOOTING.md"
    exit 1
fi

echo ""
echo "🔌 Checking USB connection..."
if lsusb | grep -qi canon; then
    echo "✅ Canon printer detected on USB"
    lsusb | grep -i canon
else
    echo "❌ Canon printer NOT detected!"
    echo "   Check USB cable and power"
    exit 1
fi

echo ""
echo "📝 Checking recent print jobs..."
lpstat -W completed -o | tail -5

echo ""
echo "🧪 Running test print..."
echo "Test Print - $(date)" | lp -d PisoPrinter
RESULT=$?

if [ $RESULT -eq 0 ]; then
    echo "✅ Test print submitted!"
    echo "   Check if printer prints the test page"
    echo "   If it does, your app should work too"
else
    echo "❌ Test print failed!"
    echo "   Exit code: $RESULT"
fi

echo ""
echo "📋 Recent CUPS errors (if any):"
sudo tail -n 10 /var/log/cups/error_log | grep -i error

echo ""
echo "===================================="
echo "✅ Quick fix complete!"
echo ""
echo "If printer still doesn't work:"
echo "1. Check PRINTER_TROUBLESHOOTING.md"
echo "2. Try: sudo systemctl restart cups"
echo "3. Power cycle the printer"
echo "===================================="
