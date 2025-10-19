# 🖨️ Piso Print System

**A coin-operated printing system using ESP32 and Orange Pi - inspired by Piso WiFi**

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [System Architecture](#system-architecture)
4. [Hardware Requirements](#hardware-requirements)
5. [Hardware Setup & Wiring](#hardware-setup--wiring)
6. [Software Requirements](#software-requirements)
7. [ESP32 Setup](#esp32-setup)
8. [Orange Pi Setup](#orange-pi-setup)
9. [Database Schema](#database-schema)
10. [System Workflow](#system-workflow)
11. [Testing Instructions](#testing-instructions)
12. [API Documentation](#api-documentation)
13. [Troubleshooting](#troubleshooting)
14. [Project Structure](#project-structure)
15. [Future Enhancements](#future-enhancements)
16. [License](#license)

---

## 🎯 Project Overview

**Piso Print** is a coin-operated printing kiosk system that allows users to:
- Connect to a Wi-Fi hotspot (ESP32)
- Upload documents via captive portal
- Insert coins to purchase printing credits
- Print documents automatically

This system is perfect for:
- Internet cafes
- Libraries
- Print shops
- Community centers
- Schools

**Similar to Piso WiFi, but for printing!**

---

## ✨ Features

### Core Features
- ✅ **Captive Portal** - Auto-redirect users to upload page
- ✅ **Wi-Fi Hotspot** - ESP32 acts as access point
- ✅ **Coin Payment System** - ₱1/₱5/₱10 coin acceptor support
- ✅ **Multi-format Support** - PDF, DOCX, images
- ✅ **Credit Tracking** - Real-time credit balance
- ✅ **Transaction Logging** - Full audit trail
- ✅ **Page Counting** - Auto-calculate printing cost
- ✅ **CUPS Integration** - Professional print management

### Advanced Features
- 📊 Admin dashboard (coming soon)
- 💳 QR payment support (future)
- 📱 Mobile app (future)
- ☁️ Cloud backup (future)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                       USER DEVICE                        │
│              (Phone/Laptop/Tablet)                       │
└────────────────────┬────────────────────────────────────┘
                     │ Wi-Fi Connection
                     │
┌────────────────────▼────────────────────────────────────┐
│                    ESP32 CH340                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │  - Wi-Fi Access Point (192.168.4.1)              │   │
│  │  - Captive Portal (Auto-redirect)                │   │
│  │  - File Upload Interface                         │   │
│  │  - Credit Display                                │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Coin Acceptor Reader                            │   │
│  │  - GPIO pulse detection                          │   │
│  │  - ₱1, ₱5, ₱10 coin recognition                  │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP API (POST/GET)
                     │ LAN/Wi-Fi
┌────────────────────▼────────────────────────────────────┐
│                  ORANGE PI PC H3                         │
│                  (Armbian OS)                            │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Flask Web Server (Port 5000)                    │   │
│  │  - /upload (receive files)                       │   │
│  │  - /print (trigger print job)                    │   │
│  │  - /api/credits (update credits)                 │   │
│  │  - /api/check_credits (verify balance)           │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  CUPS Print Server                               │   │
│  │  - Manages print queue                           │   │
│  │  - Supports USB/Network printers                 │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  SQLite/MySQL Database                           │   │
│  │  - Users, Credits, Files, Transactions           │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │ USB/Network
                     │
┌────────────────────▼────────────────────────────────────┐
│                      PRINTER                             │
│              (USB or Network Printer)                    │
└──────────────────────────────────────────────────────────┘
```

### Communication Flow

```
1. User connects to "PisoPrint_WiFi"
2. ESP32 → Captive portal redirect → Upload page
3. User uploads PDF → HTTP POST → Orange Pi Flask server
4. Flask counts pages → Returns "5 pages = ₱5"
5. ESP32 displays: "Insert ₱5"
6. User inserts coins → ESP32 GPIO detects pulses
7. ESP32 → POST /api/credits → Orange Pi updates balance
8. User clicks "Print" button
9. ESP32 → POST /print → Orange Pi validates credits
10. Orange Pi → CUPS → Printer prints document
11. Transaction saved to database
```

---

## 🛠️ Hardware Requirements

### Required Components

| Component | Specification | Quantity | Estimated Price (PHP) |
|-----------|--------------|----------|----------------------|
| ESP32 Development Board | ESP32-WROOM-32 (CH340 USB) | 1 | ₱250-400 |
| Orange Pi PC | H3 Quad-core, 1GB RAM | 1 | ₱1,500-2,000 |
| MicroSD Card | 16GB Class 10 (for Orange Pi) | 1 | ₱200-300 |
| Coin Acceptor | 3-coin type (₱1/₱5/₱10) | 1 | ₱800-1,200 |
| USB Printer | Any USB-compatible printer | 1 | ₱3,000+ |
| Power Supply | 5V 3A for Orange Pi | 1 | ₱200-300 |
| Micro USB Cable | For ESP32 power | 1 | ₱50-100 |
| Jumper Wires | Male-to-Female | 10 pcs | ₱50 |
| Enclosure | Project box | 1 | ₱300-500 |

### Optional Components

| Component | Purpose | Price (PHP) |
|-----------|---------|-------------|
| Old PLDT Modem | Ethernet connectivity | Free (reuse) |
| LCD Display 16x2 | Show credits/status | ₱150-250 |
| Buzzer | Audio feedback | ₱20-50 |
| LED Indicators | Status lights | ₱10-30 |

**Total Estimated Cost: ₱6,500 - ₱8,500**

---

## 🔌 Hardware Setup & Wiring

### ESP32 Pin Connections

```
ESP32 Pin Layout:
┌─────────────────────────────────────┐
│  ESP32-WROOM-32 (CH340)             │
│                                     │
│  3V3  ●                         ● GND
│  EN   ●                         ● GPIO23
│  GPIO36●                        ● GPIO22
│  GPIO39●                        ● TX0
│  GPIO34●                        ● RX0
│  GPIO35●                        ● GPIO21
│  GPIO32● ← Coin Pulse           ● GND
│  GPIO33●                        ● GPIO19
│  GPIO25●                        ● GPIO18
│  GPIO26●                        ● GPIO5
│  GPIO27● ← Status LED           ● GPIO17
│  GPIO14●                        ● GPIO16
│  GPIO12●                        ● GPIO4
│  GND   ●                        ● GPIO0
│  GPIO13●                        ● GPIO2
│  GPIO9 ●                        ● GPIO15
│  GPIO10●                        ● GND
│  GPIO11●                        ● 5V
│  5V    ●                        ● 3V3
│                                     │
└─────────────────────────────────────┘
```

### Coin Acceptor Wiring

```
Coin Acceptor → ESP32

Red Wire    (VCC)    → 5V (ESP32)
Black Wire  (GND)    → GND (ESP32)
White Wire  (COIN)   → GPIO32 (ESP32)
```

**Coin Acceptor Settings:**
- ₱1 coin = 1 pulse
- ₱5 coin = 5 pulses
- ₱10 coin = 10 pulses

### Orange Pi Connections

```
Orange Pi PC:
- Power: 5V/3A DC adapter
- Ethernet: Connect to router/switch (optional)
- USB: Connect printer via USB port
- MicroSD: Insert Armbian OS card
```

### Complete System Wiring Diagram

```
                    ┌──────────────┐
                    │  Coin Slot   │
                    └──────┬───────┘
                           │ (3 wires)
                           │
┌──────────────────────────▼───────────────────────┐
│                    ESP32 CH340                    │
│  GPIO32 ← Coin Pulse                             │
│  GPIO27 → Status LED                             │
│  5V/GND ← USB Power (5V 1A)                      │
│                                                   │
│  Wi-Fi: Hotspot Mode (192.168.4.1)              │
└───────────────────┬───────────────────────────────┘
                    │ HTTP over Wi-Fi/Ethernet
                    │
┌───────────────────▼───────────────────────────────┐
│              Orange Pi PC (Armbian)               │
│  Ethernet: 192.168.1.100 (static IP)             │
│  Flask Server: Port 5000                          │
│  CUPS: Port 631                                   │
└───────────────────┬───────────────────────────────┘
                    │ USB Cable
                    │
┌───────────────────▼───────────────────────────────┐
│                USB Printer                        │
│  (e.g., HP, Canon, Epson)                        │
└───────────────────────────────────────────────────┘
```

### Power Supply Setup

```
Power Distribution:

Wall Outlet (220V)
    │
    ├── USB Adapter (5V 1A) → ESP32 (Micro USB)
    │
    └── DC Adapter (5V 3A) → Orange Pi (DC Jack)

Coin Acceptor Power:
    - Powered from ESP32 5V pin
    - Total current: ~100mA
```

---

## 💻 Software Requirements

### ESP32 Software

- **Arduino IDE** (1.8.19 or later)
- **ESP32 Board Support** (via Board Manager)
- **Required Libraries:**
  ```
  - WiFi.h (built-in)
  - WebServer.h (built-in)
  - DNSServer.h (built-in)
  - HTTPClient.h (built-in)
  - SPIFFS.h (built-in)
  - ArduinoJson (install via Library Manager)
  ```

### Orange Pi Software

- **Armbian OS** (Ubuntu-based, latest stable)
- **Python 3.8+**
- **Flask** (Python web framework)
- **CUPS** (Common Unix Printing System)
- **SQLite3** or **MySQL**
- **System packages:**
  ```
  - python3-pip
  - python3-venv
  - cups
  - printer-driver-all
  - git
  ```

---

## 🔧 ESP32 Setup

### Step 1: Install Arduino IDE

```bash
# Download from: https://www.arduino.cc/en/software
# Or use command line (Linux):
sudo snap install arduino
```

### Step 2: Add ESP32 Board Support

1. Open Arduino IDE
2. Go to **File → Preferences**
3. Add this URL to "Additional Board Manager URLs":
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Go to **Tools → Board → Board Manager**
5. Search "ESP32" and install **"esp32 by Espressif Systems"**

### Step 3: Install Required Libraries

1. Go to **Sketch → Include Library → Manage Libraries**
2. Install:
   - `ArduinoJson` by Benoit Blanchon

### Step 4: ESP32 Code

Create a new sketch: `PisoPrint_ESP32.ino`

```cpp
#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ============================================
// Configuration
// ============================================
const char* AP_SSID = "PisoPrint_WiFi";
const char* AP_PASS = ""; // Open network

// Orange Pi Flask Server
const char* FLASK_SERVER = "http://192.168.4.2:5000"; // Change to your Orange Pi IP

// Pin Definitions
const int COIN_PIN = 32;  // Coin acceptor pulse input
const int LED_PIN = 27;   // Status LED

// DNS Server for Captive Portal
DNSServer dnsServer;
WebServer server(80);

// Variables
volatile int coinPulses = 0;
int userCredits = 0;
String currentSessionID = "";
String uploadedFileName = "";

// ============================================
// Coin Acceptor Interrupt
// ============================================
void IRAM_ATTR coinInserted() {
  coinPulses++;
}

// ============================================
// Setup
// ============================================
void setup() {
  Serial.begin(115200);
  
  // Pin modes
  pinMode(COIN_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
  
  // Attach interrupt for coin detection
  attachInterrupt(digitalPinToInterrupt(COIN_PIN), coinInserted, FALLING);
  
  // Create Wi-Fi Access Point
  WiFi.mode(WIFI_AP);
  WiFi.softAP(AP_SSID, AP_PASS);
  
  Serial.println("Access Point Started");
  Serial.print("IP Address: ");
  Serial.println(WiFi.softAPIP());
  
  // Start DNS server for captive portal
  dnsServer.start(53, "*", WiFi.softAPIP());
  
  // Web server routes
  server.on("/", handleRoot);
  server.on("/upload", HTTP_POST, handleUploadResponse, handleFileUpload);
  server.on("/status", handleStatus);
  server.on("/print", handlePrint);
  server.onNotFound(handleRoot); // Redirect all to captive portal
  
  server.begin();
  Serial.println("Web Server Started");
  
  // Generate session ID
  currentSessionID = generateSessionID();
  
  // LED blink to indicate ready
  blinkLED(3);
}

// ============================================
// Main Loop
// ============================================
void loop() {
  dnsServer.processNextRequest();
  server.handleClient();
  
  // Check for coin insertions
  if (coinPulses > 0) {
    noInterrupts();
    int pulses = coinPulses;
    coinPulses = 0;
    interrupts();
    
    // Add credits (₱1 per pulse)
    userCredits += pulses;
    Serial.print("Credits: ₱");
    Serial.println(userCredits);
    
    // Send credits to Orange Pi
    sendCreditsToServer(pulses);
    
    // LED feedback
    blinkLED(1);
  }
}

// ============================================
// Web Server Handlers
// ============================================
void handleRoot() {
  String html = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Piso Print</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .container {
      background: white;
      border-radius: 20px;
      padding: 40px;
      max-width: 500px;
      width: 100%;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    h1 {
      color: #667eea;
      text-align: center;
      margin-bottom: 10px;
      font-size: 2.5em;
    }
    .subtitle {
      text-align: center;
      color: #666;
      margin-bottom: 30px;
    }
    .credits {
      background: #f0f4ff;
      padding: 20px;
      border-radius: 10px;
      text-align: center;
      margin-bottom: 30px;
      border: 2px solid #667eea;
    }
    .credits h2 {
      color: #667eea;
      font-size: 1.2em;
      margin-bottom: 10px;
    }
    .credits .amount {
      font-size: 3em;
      font-weight: bold;
      color: #764ba2;
    }
    .upload-area {
      border: 3px dashed #667eea;
      border-radius: 10px;
      padding: 40px;
      text-align: center;
      margin-bottom: 20px;
      cursor: pointer;
      transition: all 0.3s;
    }
    .upload-area:hover {
      background: #f0f4ff;
      border-color: #764ba2;
    }
    .upload-area input[type="file"] {
      display: none;
    }
    .upload-icon {
      font-size: 4em;
      margin-bottom: 10px;
    }
    .btn {
      width: 100%;
      padding: 15px;
      border: none;
      border-radius: 10px;
      font-size: 1.2em;
      font-weight: bold;
      cursor: pointer;
      transition: all 0.3s;
      margin-top: 10px;
    }
    .btn-primary {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
    }
    .btn-primary:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    .btn-primary:disabled {
      background: #ccc;
      cursor: not-allowed;
      transform: none;
    }
    .status {
      text-align: center;
      margin-top: 20px;
      padding: 10px;
      border-radius: 5px;
      display: none;
    }
    .status.success {
      background: #d4edda;
      color: #155724;
      display: block;
    }
    .status.error {
      background: #f8d7da;
      color: #721c24;
      display: block;
    }
    .file-name {
      margin-top: 10px;
      padding: 10px;
      background: #e8f5e9;
      border-radius: 5px;
      display: none;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>🖨️ Piso Print</h1>
    <p class="subtitle">Upload • Insert Coins • Print</p>
    
    <div class="credits">
      <h2>Your Credits</h2>
      <div class="amount" id="credits">₱<span id="creditAmount">0</span></div>
    </div>
    
    <form id="uploadForm" enctype="multipart/form-data">
      <div class="upload-area" onclick="document.getElementById('fileInput').click()">
        <div class="upload-icon">📄</div>
        <h3>Click to Upload Document</h3>
        <p>PDF, DOCX, Images supported</p>
        <input type="file" id="fileInput" name="file" accept=".pdf,.doc,.docx,.jpg,.png" onchange="handleFileSelect(event)">
      </div>
      <div class="file-name" id="fileName"></div>
      <button type="button" class="btn btn-primary" id="uploadBtn" onclick="uploadFile()" disabled>Upload File</button>
      <button type="button" class="btn btn-primary" id="printBtn" onclick="printFile()" disabled>Print Now</button>
    </form>
    
    <div class="status" id="status"></div>
  </div>

  <script>
    let uploadedFile = null;
    let requiredCredits = 0;

    function updateCredits() {
      fetch('/status')
        .then(r => r.json())
        .then(data => {
          document.getElementById('creditAmount').textContent = data.credits;
          checkPrintButton();
        });
    }

    function handleFileSelect(event) {
      uploadedFile = event.target.files[0];
      if (uploadedFile) {
        document.getElementById('fileName').textContent = '📎 ' + uploadedFile.name;
        document.getElementById('fileName').style.display = 'block';
        document.getElementById('uploadBtn').disabled = false;
      }
    }

    function uploadFile() {
      if (!uploadedFile) return;

      const formData = new FormData();
      formData.append('file', uploadedFile);

      document.getElementById('uploadBtn').disabled = true;
      showStatus('Uploading...', 'info');

      fetch('http://192.168.4.2:5000/upload', {
        method: 'POST',
        body: formData
      })
      .then(r => r.json())
      .then(data => {
        if (data.success) {
          requiredCredits = data.pages;
          showStatus('✅ File uploaded! ' + data.pages + ' pages = ₱' + data.pages, 'success');
          document.getElementById('printBtn').disabled = false;
        } else {
          showStatus('❌ Upload failed: ' + data.error, 'error');
        }
      })
      .catch(err => {
        showStatus('❌ Upload error', 'error');
      })
      .finally(() => {
        document.getElementById('uploadBtn').disabled = false;
      });
    }

    function printFile() {
      fetch('/print')
        .then(r => r.json())
        .then(data => {
          if (data.success) {
            showStatus('✅ Printing...', 'success');
            setTimeout(() => {
              location.reload();
            }, 2000);
          } else {
            showStatus('❌ ' + data.message, 'error');
          }
        });
    }

    function checkPrintButton() {
      const credits = parseInt(document.getElementById('creditAmount').textContent);
      if (credits >= requiredCredits && requiredCredits > 0) {
        document.getElementById('printBtn').disabled = false;
      }
    }

    function showStatus(message, type) {
      const status = document.getElementById('status');
      status.textContent = message;
      status.className = 'status ' + type;
      status.style.display = 'block';
    }

    setInterval(updateCredits, 1000);
    updateCredits();
  </script>
</body>
</html>
  )rawliteral";
  
  server.send(200, "text/html", html);
}

void handleFileUpload() {
  HTTPUpload& upload = server.upload();
  
  if (upload.status == UPLOAD_FILE_START) {
    uploadedFileName = upload.filename;
    Serial.print("Upload Start: ");
    Serial.println(uploadedFileName);
  }
}

void handleUploadResponse() {
  server.send(200, "application/json", "{\"success\":true}");
}

void handleStatus() {
  String json = "{\"credits\":" + String(userCredits) + 
                ",\"session\":\"" + currentSessionID + "\"}";
  server.send(200, "application/json", json);
}

void handlePrint() {
  // Send print request to Orange Pi
  HTTPClient http;
  http.begin(String(FLASK_SERVER) + "/print");
  http.addHeader("Content-Type", "application/json");
  
  StaticJsonDocument<200> doc;
  doc["session_id"] = currentSessionID;
  doc["credits"] = userCredits;
  
  String requestBody;
  serializeJson(doc, requestBody);
  
  int httpCode = http.POST(requestBody);
  String response = http.getString();
  
  http.end();
  
  if (httpCode == 200) {
    // Parse response
    StaticJsonDocument<200> responseDoc;
    deserializeJson(responseDoc, response);
    
    if (responseDoc["success"]) {
      int pagesDeducted = responseDoc["pages"];
      userCredits -= pagesDeducted;
      server.send(200, "application/json", "{\"success\":true,\"message\":\"Printing...\"}");
    } else {
      server.send(200, "application/json", "{\"success\":false,\"message\":\"" + String(responseDoc["message"].as<const char*>()) + "\"}");
    }
  } else {
    server.send(200, "application/json", "{\"success\":false,\"message\":\"Server error\"}");
  }
}

// ============================================
// Helper Functions
// ============================================
String generateSessionID() {
  return "USER_" + String(random(100000, 999999));
}

void sendCreditsToServer(int amount) {
  HTTPClient http;
  http.begin(String(FLASK_SERVER) + "/api/credits");
  http.addHeader("Content-Type", "application/json");
  
  StaticJsonDocument<200> doc;
  doc["session_id"] = currentSessionID;
  doc["amount"] = amount;
  
  String requestBody;
  serializeJson(doc, requestBody);
  
  int httpCode = http.POST(requestBody);
  Serial.print("Credit update response: ");
  Serial.println(httpCode);
  
  http.end();
}

void blinkLED(int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(100);
    digitalWrite(LED_PIN, LOW);
    delay(100);
  }
}
```

### Step 5: Upload Code to ESP32

1. Connect ESP32 to computer via USB
2. Select **Tools → Board → ESP32 Dev Module**
3. Select **Tools → Port → (your COM port)**
4. Click **Upload** button
5. Wait for "Done uploading" message

### Step 6: Testing ESP32

1. Open **Serial Monitor** (115200 baud)
2. You should see:
   ```
   Access Point Started
   IP Address: 192.168.4.1
   Web Server Started
   ```
3. Connect your phone to "PisoPrint_WiFi"
4. Browser should auto-open to upload page

---

## 🍊 Orange Pi Setup

### Step 1: Install Armbian OS

1. **Download Armbian:**
   ```
   https://www.armbian.com/orange-pi-pc/
   Download: Armbian_*_Orangepipc_*_Ubuntu_*.img.xz
   ```

2. **Flash to MicroSD Card:**
   ```bash
   # Linux/Mac
   sudo dd if=Armbian*.img of=/dev/sdX bs=4M status=progress
   
   # Or use Balena Etcher (GUI): https://www.balena.io/etcher/
   ```

3. **First Boot:**
   - Insert SD card into Orange Pi
   - Connect HDMI monitor + USB keyboard
   - Connect Ethernet cable (optional)
   - Connect power adapter
   - Wait for boot (~2 minutes)

4. **Initial Setup:**
   ```
   Default login:
   Username: root
   Password: 1234
   
   You'll be prompted to:
   - Change root password
   - Create a new user
   ```

### Step 2: Configure Network

```bash
# Set static IP (optional but recommended)
sudo nano /etc/network/interfaces
```

Add:
```
auto eth0
iface eth0 inet static
    address 192.168.1.100
    netmask 255.255.255.0
    gateway 192.168.1.1
    dns-nameservers 8.8.8.8
```

Or use DHCP (dynamic):
```
auto eth0
iface eth0 inet dhcp
```

Restart networking:
```bash
sudo systemctl restart networking
```

### Step 3: Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### Step 4: Install Required Packages

```bash
# Python and pip
sudo apt install -y python3 python3-pip python3-venv

# CUPS (printing system)
sudo apt install -y cups printer-driver-all

# Other utilities
sudo apt install -y git sqlite3 htop
```

### Step 5: Install Python Dependencies

```bash
# Create project directory
mkdir -p /home/pisoprint
cd /home/pisoprint

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Flask and libraries
pip install flask flask-cors pycups PyPDF2 python-docx pillow
```

### Step 6: Configure CUPS

```bash
# Add your user to lpadmin group
sudo usermod -a -G lpadmin $USER

# Edit CUPS config
sudo nano /etc/cups/cupsd.conf
```

Change these lines:
```
Listen localhost:631
↓ to ↓
Listen 0.0.0.0:631

<Location />
  Order allow,deny
  Allow @LOCAL  # Add this line
</Location>

<Location /admin>
  Order allow,deny
  Allow @LOCAL  # Add this line
</Location>
```

Restart CUPS:
```bash
sudo systemctl restart cups
sudo systemctl enable cups
```

### Step 7: Add Printer to CUPS

```bash
# Connect your USB printer

# List detected printers
lpinfo -v
