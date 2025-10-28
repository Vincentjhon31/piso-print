#!/bin/bash
# Check PisoPrint service status on Orange Pi

echo "=========================================="
echo "🔍 Checking PisoPrint Service Status"
echo "=========================================="
echo ""

# Check if service file exists
echo "1️⃣ Service file exists?"
if [ -f "/etc/systemd/system/pisoprint.service" ]; then
    echo "   ✅ YES - Service is installed"
    echo ""
    echo "   📄 Service configuration:"
    cat /etc/systemd/system/pisoprint.service
else
    echo "   ❌ NO - Service not installed yet"
fi

echo ""
echo "=========================================="
echo "2️⃣ Service status:"
echo "=========================================="
sudo systemctl status pisoprint.service

echo ""
echo "=========================================="
echo "3️⃣ Is service enabled to auto-start?"
echo "=========================================="
sudo systemctl is-enabled pisoprint.service

echo ""
echo "=========================================="
echo "4️⃣ Flask process running?"
echo "=========================================="
ps aux | grep "app.py" | grep -v grep

echo ""
echo "=========================================="
echo "5️⃣ Port 5000 in use?"
echo "=========================================="
sudo netstat -tlnp | grep :5000 || sudo ss -tlnp | grep :5000

echo ""
echo "=========================================="
echo "✅ Status check complete!"
echo "=========================================="
