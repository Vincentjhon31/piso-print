#!/bin/bash
# Safe shutdown script for PisoPrint system

echo "=========================================="
echo "🛑 PisoPrint Safe Shutdown"
echo "=========================================="
echo ""

# Stop Flask service
echo "1️⃣ Stopping Flask service..."
sudo systemctl stop pisoprint
echo "   ✅ Flask stopped"
sleep 1

# Stop admin dashboard if running
echo ""
echo "2️⃣ Checking for admin dashboard..."
if pgrep -f "admin.py" > /dev/null; then
    pkill -f "admin.py"
    echo "   ✅ Admin dashboard stopped"
else
    echo "   ℹ️  Admin dashboard not running"
fi
sleep 1

# Show disk sync
echo ""
echo "3️⃣ Syncing disk writes..."
sync
echo "   ✅ Disk synced"
sleep 1

# Final message
echo ""
echo "=========================================="
echo "✅ All services stopped safely"
echo "🔌 Shutting down Orange Pi in 3 seconds..."
echo "⏳ Wait for LED to stop blinking"
echo "   Then you can unplug the power."
echo "=========================================="
sleep 3

# Shutdown
sudo shutdown -h now
