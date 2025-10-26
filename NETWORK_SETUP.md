# 🌐 Network Setup Guide

This guide explains how to connect ESP32 and Orange Pi for the Piso Print system.

---

## 📊 Network Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    PISO PRINT SYSTEM                         │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   USER       │  WiFi   │   ESP32      │  HTTP   │  ORANGE PI   │
│   DEVICE     │◄───────►│   CH340      │◄───────►│   PC H3      │
│ (Phone/PC)   │         │              │         │              │
└──────────────┘         └──────────────┘         └──────────────┘
                         192.168.4.1              192.168.4.2
                         (Hotspot)                (Backend)
```

---

## 🎯 Setup Options

### **Option A: Production Setup** (Recommended for Final Kiosk)

**Network Design:**

- ESP32 creates WiFi hotspot: `PisoPrint_WiFi_v2`
- Orange Pi connects to ESP32's hotspot
- Users connect to ESP32's hotspot
- All communication stays within local network

**Configuration:**

#### **Step 1: Configure ESP32**

In `PisoPrint_ESP32.ino.ino`:

```cpp
const char* FLASK_SERVER = "http://192.168.4.2:5000";
```

Upload to ESP32.

#### **Step 2: Connect Orange Pi to ESP32**

```bash
# On Orange Pi, connect to ESP32's WiFi
sudo nmcli device wifi connect "PisoPrint_WiFi_v2"

# Check IP address (should be 192.168.4.x)
ip addr show wlan0

# Set static IP to 192.168.4.2
sudo nmcli con mod "PisoPrint_WiFi_v2" ipv4.addresses 192.168.4.2/24
sudo nmcli con mod "PisoPrint_WiFi_v2" ipv4.gateway 192.168.4.1
sudo nmcli con mod "PisoPrint_WiFi_v2" ipv4.dns 8.8.8.8
sudo nmcli con mod "PisoPrint_WiFi_v2" ipv4.method manual
sudo nmcli con up "PisoPrint_WiFi_v2"

# Verify connection
ping 192.168.4.1  # Should ping ESP32
```

#### **Step 3: Start Flask Server**

```bash
cd /root/piso-print
source venv/bin/activate
python app.py
```

**Network Layout:**

```
ESP32 (192.168.4.1) ← WiFi → Orange Pi (192.168.4.2)
        ↑
        │ WiFi
        ↓
   User Devices
```

**Pros:**

- ✅ Self-contained system
- ✅ No external network needed
- ✅ Fast local communication
- ✅ Production-ready

**Cons:**

- ❌ No internet access (unless ESP32 has internet sharing)
- ❌ Can't remotely manage Orange Pi

---

### **Option B: Testing Setup** (Development/Debugging)

**Network Design:**

- Both devices on your existing WiFi network
- Easy to access both for debugging
- Not the final production setup

**Configuration:**

#### **Step 1: Keep Orange Pi on Current Network**

Orange Pi stays on your home/office WiFi:

- Current IP: `10.66.229.242`
- Flask running on: `http://10.66.229.242:5000`

#### **Step 2: Update ESP32 to Use Orange Pi IP**

In `PisoPrint_ESP32.ino.ino`:

```cpp
const char* FLASK_SERVER = "http://10.66.229.242:5000";  // Your Orange Pi IP
```

Upload to ESP32.

#### **Step 3: Ensure ESP32 Can Reach Orange Pi**

**Either:**

**A) Connect ESP32 to same WiFi** (Station Mode):

```cpp
// In ESP32 code, add WiFi client connection:
const char* STA_SSID = "YourWiFiName";
const char* STA_PASS = "YourWiFiPassword";

void setup() {
  // Add this before starting AP
  WiFi.begin(STA_SSID, STA_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  // Then continue with AP setup...
}
```

**Or:**

**B) Keep ESP32 as AP** and connect from same network (users need to be on your WiFi)

**Network Layout:**

```
       Your WiFi Router
              ↑
    ┌─────────┴─────────┐
    │                   │
ESP32 (DHCP)      Orange Pi (10.66.229.242)
```

**Pros:**

- ✅ Easy debugging
- ✅ Internet access on both devices
- ✅ Can update/manage remotely

**Cons:**

- ❌ Not production setup
- ❌ Users need WiFi credentials
- ❌ More complex network

---

### **Option C: Dual Network** (Advanced)

**Network Design:**

- Orange Pi has 2 network interfaces
- One for internet (Ethernet or WiFi)
- One for ESP32 connection (WiFi)

**Configuration:**

```bash
# On Orange Pi with Ethernet + WiFi

# Ethernet for internet
sudo nmcli con add type ethernet ifname eth0 con-name internet
sudo nmcli con mod internet ipv4.method auto

# WiFi for ESP32
sudo nmcli device wifi connect "PisoPrint_WiFi_v2" ifname wlan0
sudo nmcli con mod "PisoPrint_WiFi_v2" ipv4.addresses 192.168.4.2/24
sudo nmcli con mod "PisoPrint_WiFi_v2" ipv4.gateway 192.168.4.1
sudo nmcli con mod "PisoPrint_WiFi_v2" ipv4.method manual
```

**Network Layout:**

```
Internet ← Ethernet → Orange Pi ← WiFi → ESP32
                    (192.168.4.2)     (192.168.4.1)
```

**Pros:**

- ✅ Production setup + internet
- ✅ Best for development
- ✅ Remote management possible

**Cons:**

- ❌ Requires 2 network interfaces

---

## 🧪 Testing Connection

### **1. Test from ESP32 Serial Monitor:**

Upload code and check Serial output:

```
Connecting to Flask server...
HTTP Response code: 200
```

### **2. Test from Orange Pi:**

```bash
# Check if Flask is accessible
curl http://localhost:5000

# Check from ESP32 IP (if using Option A)
curl http://192.168.4.2:5000
```

### **3. Test ESP32 to Orange Pi:**

```bash
# On Orange Pi, monitor logs
tail -f /root/piso-print/logs/server.log

# Then insert coin in ESP32 or upload file
# You should see requests in logs
```

---

## 🔧 Troubleshooting

### **ESP32 Can't Connect to Orange Pi**

```
Error: Connection refused
Error: Host unreachable
```

**Fixes:**

```bash
# On Orange Pi, check Flask is running
ps aux | grep app.py

# Check firewall
sudo ufw status
sudo ufw allow 5000

# Check Flask is listening on all interfaces
netstat -tulpn | grep 5000
# Should show: 0.0.0.0:5000 (not 127.0.0.1:5000)
```

### **Orange Pi Can't Connect to ESP32 WiFi**

```bash
# Check ESP32 WiFi is broadcasting
# On phone/laptop, look for "PisoPrint_WiFi_v2"

# On Orange Pi
sudo nmcli device wifi list

# Force rescan
sudo nmcli device wifi rescan

# Try manual connection with more details
sudo nmcli device wifi connect "PisoPrint_WiFi_v2" password "" ifname wlan0
```

### **Wrong IP Address**

```bash
# Check current IP
ip addr show

# Release current IP
sudo dhclient -r wlan0

# Get new IP
sudo dhclient wlan0

# Or set static IP
sudo nmcli con mod "PisoPrint_WiFi_v2" ipv4.addresses 192.168.4.2/24
sudo nmcli con up "PisoPrint_WiFi_v2"
```

---

## 📋 Quick Reference

### **ESP32 Configuration**

| Setup               | FLASK_SERVER Value             |
| ------------------- | ------------------------------ |
| Production          | `http://192.168.4.2:5000`      |
| Testing (Same WiFi) | `http://YOUR_ORANGEPI_IP:5000` |
| Testing (Ethernet)  | `http://YOUR_ORANGEPI_IP:5000` |

### **Orange Pi Network Commands**

```bash
# Show network interfaces
ip link show

# Show IP addresses
ip addr show

# Show WiFi networks
sudo nmcli device wifi list

# Connect to WiFi
sudo nmcli device wifi connect "SSID" password "PASSWORD"

# Disconnect WiFi
sudo nmcli con down "CONNECTION_NAME"

# Show active connections
nmcli con show --active

# Restart networking
sudo systemctl restart NetworkManager
```

### **Testing Commands**

```bash
# Test from Orange Pi to ESP32
ping 192.168.4.1
curl http://192.168.4.1

# Test Flask server
curl http://localhost:5000
curl http://192.168.4.2:5000

# Monitor Flask logs
tail -f /root/piso-print/logs/server.log

# Check network traffic
sudo tcpdump -i wlan0 port 5000
```

---

## 🎯 Recommended Setup Flow

### **Phase 1: Testing (Use Option B)**

1. Keep Orange Pi on your home WiFi
2. Update ESP32 with Orange Pi IP
3. Test all functionality
4. Debug and verify everything works

### **Phase 2: Production (Switch to Option A)**

1. Connect Orange Pi to ESP32 WiFi
2. Set static IP 192.168.4.2
3. Update ESP32 back to 192.168.4.2
4. Final testing
5. Deploy kiosk

---

## 🆘 Still Having Issues?

1. **Check ESP32 Serial Monitor** for connection errors
2. **Check Orange Pi Flask logs**: `tail -f logs/server.log`
3. **Verify both devices are on same network**: `ping` test
4. **Check firewall**: `sudo ufw status`
5. **Verify Flask is running**: `curl http://localhost:5000`

---
