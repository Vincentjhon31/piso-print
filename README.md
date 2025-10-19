# 🖨️ Piso Print System

**A coin-operated printing system using ESP32 and Orange Pi - inspired by Piso WiFi**

---

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [Features](#-features)
3. [System Architecture](#-system-architecture)
4. [Hardware Requirements](#-hardware-requirements)
5. [Hardware Setup & Wiring](#-hardware-setup--wiring)
6. [Software Requirements](#-software-requirements)
7. [ESP32 Setup](#-esp32-setup)
8. [Orange Pi Setup](#-orange-pi-setup)
9. [Database Schema](#-database-schema)
10. [System Workflow](#-system-workflow)
11. [Testing Instructions](#-testing-instructions)
12. [API Documentation](#-api-documentation)
13. [Troubleshooting](#-troubleshooting)
14. [Project Structure](#-project-structure)
15. [Future Enhancements](#-future-enhancements)
16. [License](#-license)

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

```bash
# Add printer (example for HP printer)
lpadmin -p PisoPrinter -E -v usb://HP/DeskJet%202130%20series -m everywhere

# Set as default
lpoptions -d PisoPrinter

# Test print
echo "Test print from Piso Print System" | lp
```

**Or use CUPS Web Interface:**
1. Open browser: `http://192.168.1.100:631`
2. Go to **Administration** → **Add Printer**
3. Select your USB printer
4. Follow the wizard

### Step 8: Create Flask Application

Create the main Flask server file:

```bash
cd /home/pisoprint
nano app.py
```

**Flask Server Code (`app.py`):**

```python
#!/usr/bin/env python3
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import cups
import sqlite3
import os
import hashlib
from datetime import datetime
from werkzeug.utils import secure_filename
import PyPDF2
from docx import Document
from PIL import Image

# ============================================
# Configuration
# ============================================
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = '/home/pisoprint/uploads'
DATABASE = '/home/pisoprint/pisoprint.db'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'txt'}
PRICE_PER_PAGE = 1  # ₱1 per page

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# CUPS connection
conn_cups = cups.Connection()

# ============================================
# Database Setup
# ============================================
def init_db():
    """Initialize SQLite database with tables"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Users/Sessions table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT UNIQUE NOT NULL,
        credits INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Files table
    c.execute('''CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        filename TEXT NOT NULL,
        original_filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_size INTEGER,
        pages INTEGER,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES users(session_id)
    )''')
    
    # Transactions table
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        type TEXT NOT NULL,
        amount INTEGER,
        description TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES users(session_id)
    )''')
    
    # Print jobs table
    c.execute('''CREATE TABLE IF NOT EXISTS print_jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        file_id INTEGER NOT NULL,
        pages INTEGER,
        cost INTEGER,
        status TEXT DEFAULT 'pending',
        cups_job_id INTEGER,
        printed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES users(session_id),
        FOREIGN KEY (file_id) REFERENCES files(id)
    )''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# ============================================
# Helper Functions
# ============================================
def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_or_create_user(session_id):
    """Get user or create if doesn't exist"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT * FROM users WHERE session_id = ?', (session_id,))
    user = cursor.fetchone()
    
    if not user:
        cursor.execute('INSERT INTO users (session_id, credits) VALUES (?, 0)', (session_id,))
        db.commit()
        cursor.execute('SELECT * FROM users WHERE session_id = ?', (session_id,))
        user = cursor.fetchone()
    
    db.close()
    return dict(user)

def count_pdf_pages(filepath):
    """Count pages in PDF file"""
    try:
        with open(filepath, 'rb') as f:
            pdf = PyPDF2.PdfReader(f)
            return len(pdf.pages)
    except Exception as e:
        print(f"Error counting PDF pages: {e}")
        return 1

def count_docx_pages(filepath):
    """Estimate pages in DOCX (rough estimate)"""
    try:
        doc = Document(filepath)
        # Rough estimate: 500 words per page
        word_count = sum(len(para.text.split()) for para in doc.paragraphs)
        pages = max(1, word_count // 500)
        return pages
    except Exception as e:
        print(f"Error counting DOCX pages: {e}")
        return 1

def count_image_pages(filepath):
    """Images are always 1 page"""
    return 1

def count_file_pages(filepath, extension):
    """Count pages based on file type"""
    if extension == 'pdf':
        return count_pdf_pages(filepath)
    elif extension in ['doc', 'docx']:
        return count_docx_pages(filepath)
    elif extension in ['jpg', 'jpeg', 'png']:
        return count_image_pages(filepath)
    else:
        return 1

def log_transaction(session_id, trans_type, amount, description):
    """Log transaction to database"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''INSERT INTO transactions (session_id, type, amount, description)
                      VALUES (?, ?, ?, ?)''', (session_id, trans_type, amount, description))
    db.commit()
    db.close()

# ============================================
# API Routes
# ============================================

@app.route('/')
def index():
    """Home page"""
    return jsonify({
        'status': 'online',
        'message': 'Piso Print Server Running',
        'version': '1.0.0',
        'endpoints': {
            'upload': '/upload (POST)',
            'print': '/print (POST)',
            'credits': '/api/credits (POST)',
            'status': '/api/status (GET)',
            'history': '/api/history (GET)'
        }
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload from ESP32"""
    
    # Check if file exists in request
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'File type not allowed'}), 400
    
    # Get session ID from form or generate new one
    session_id = request.form.get('session_id', f'USER_{datetime.now().timestamp()}')
    
    # Ensure user exists
    user = get_or_create_user(session_id)
    
    # Secure filename and save
    original_filename = secure_filename(file.filename)
    extension = original_filename.rsplit('.', 1)[1].lower()
    
    # Generate unique filename
    file_hash = hashlib.md5(f"{session_id}{datetime.now().isoformat()}".encode()).hexdigest()
    filename = f"{file_hash}.{extension}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    file.save(filepath)
    file_size = os.path.getsize(filepath)
    
    # Count pages
    pages = count_file_pages(filepath, extension)
    cost = pages * PRICE_PER_PAGE
    
    # Save to database
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''INSERT INTO files 
                      (session_id, filename, original_filename, file_path, file_size, pages)
                      VALUES (?, ?, ?, ?, ?, ?)''',
                   (session_id, filename, original_filename, filepath, file_size, pages))
    file_id = cursor.lastrowid
    db.commit()
    db.close()
    
    # Log transaction
    log_transaction(session_id, 'upload', 0, f'Uploaded {original_filename}')
    
    return jsonify({
        'success': True,
        'file_id': file_id,
        'filename': original_filename,
        'pages': pages,
        'cost': cost,
        'message': f'{pages} pages = ₱{cost}'
    })

@app.route('/print', methods=['POST'])
def print_file():
    """Handle print request from ESP32"""
    
    data = request.get_json()
    session_id = data.get('session_id')
    credits = data.get('credits', 0)
    
    if not session_id:
        return jsonify({'success': False, 'message': 'Session ID required'}), 400
    
    # Get user
    user = get_or_create_user(session_id)
    
    # Get latest uploaded file
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''SELECT * FROM files 
                      WHERE session_id = ? 
                      ORDER BY uploaded_at DESC LIMIT 1''', (session_id,))
    file_record = cursor.fetchone()
    
    if not file_record:
        db.close()
        return jsonify({'success': False, 'message': 'No file uploaded'}), 400
    
    file_record = dict(file_record)
    pages = file_record['pages']
    cost = pages * PRICE_PER_PAGE
    
    # Check if user has enough credits
    if credits < cost:
        db.close()
        return jsonify({
            'success': False,
            'message': f'Insufficient credits. Need ₱{cost}, have ₱{credits}'
        }), 400
    
    # Print the file using CUPS
    try:
        printers = conn_cups.getPrinters()
        if not printers:
            db.close()
            return jsonify({'success': False, 'message': 'No printer available'}), 500
        
        # Get default printer or first available
        printer_name = list(printers.keys())[0]
        
        # Send print job
        cups_job_id = conn_cups.printFile(
            printer_name,
            file_record['file_path'],
            file_record['original_filename'],
            {}
        )
        
        # Update user credits
        new_credits = credits - cost
        cursor.execute('UPDATE users SET credits = ? WHERE session_id = ?',
                      (new_credits, session_id))
        
        # Log print job
        cursor.execute('''INSERT INTO print_jobs 
                          (session_id, file_id, pages, cost, status, cups_job_id)
                          VALUES (?, ?, ?, ?, 'printing', ?)''',
                      (session_id, file_record['id'], pages, cost, cups_job_id))
        
        db.commit()
        db.close()
        
        # Log transaction
        log_transaction(session_id, 'print', -cost, 
                       f'Printed {file_record["original_filename"]} ({pages} pages)')
        
        return jsonify({
            'success': True,
            'message': 'Printing started',
            'pages': pages,
            'cost': cost,
            'remaining_credits': new_credits,
            'job_id': cups_job_id
        })
        
    except Exception as e:
        db.close()
        return jsonify({'success': False, 'message': f'Print error: {str(e)}'}), 500

@app.route('/api/credits', methods=['POST'])
def add_credits():
    """Add credits when coins are inserted"""
    
    data = request.get_json()
    session_id = data.get('session_id')
    amount = data.get('amount', 0)
    
    if not session_id or amount <= 0:
        return jsonify({'success': False, 'message': 'Invalid request'}), 400
    
    # Get or create user
    user = get_or_create_user(session_id)
    
    # Update credits
    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE users SET credits = credits + ? WHERE session_id = ?',
                  (amount, session_id))
    db.commit()
    
    # Get new balance
    cursor.execute('SELECT credits FROM users WHERE session_id = ?', (session_id,))
    new_balance = cursor.fetchone()['credits']
    db.close()
    
    # Log transaction
    log_transaction(session_id, 'credit', amount, f'Added ₱{amount} credits')
    
    return jsonify({
        'success': True,
        'credits': new_balance,
        'added': amount
    })

@app.route('/api/check_credits', methods=['GET'])
def check_credits():
    """Check user credits"""
    
    session_id = request.args.get('session_id')
    
    if not session_id:
        return jsonify({'success': False, 'message': 'Session ID required'}), 400
    
    user = get_or_create_user(session_id)
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'credits': user['credits']
    })

@app.route('/api/status', methods=['GET'])
def system_status():
    """Get system status"""
    
    try:
        printers = conn_cups.getPrinters()
        printer_status = []
        
        for name, info in printers.items():
            printer_status.append({
                'name': name,
                'state': info.get('printer-state-message', 'Unknown'),
                'accepting_jobs': info.get('printer-is-accepting-jobs', False)
            })
        
        # Get database stats
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('SELECT COUNT(*) as total FROM users')
        total_users = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM print_jobs')
        total_jobs = cursor.fetchone()['total']
        
        cursor.execute('SELECT SUM(cost) as revenue FROM print_jobs WHERE status = "printing"')
        total_revenue = cursor.fetchone()['revenue'] or 0
        
        db.close()
        
        return jsonify({
            'success': True,
            'printers': printer_status,
            'stats': {
                'total_users': total_users,
                'total_jobs': total_jobs,
                'total_revenue': total_revenue
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get print history"""
    
    session_id = request.args.get('session_id')
    limit = request.args.get('limit', 10, type=int)
    
    db = get_db()
    cursor = db.cursor()
    
    if session_id:
        cursor.execute('''SELECT pj.*, f.original_filename 
                          FROM print_jobs pj
                          JOIN files f ON pj.file_id = f.id
                          WHERE pj.session_id = ?
                          ORDER BY pj.printed_at DESC
                          LIMIT ?''', (session_id, limit))
    else:
        cursor.execute('''SELECT pj.*, f.original_filename 
                          FROM print_jobs pj
                          JOIN files f ON pj.file_id = f.id
                          ORDER BY pj.printed_at DESC
                          LIMIT ?''', (limit,))
    
    history = [dict(row) for row in cursor.fetchall()]
    db.close()
    
    return jsonify({
        'success': True,
        'history': history
    })

# ============================================
# Run Server
# ============================================
if __name__ == '__main__':
    print("🖨️  Piso Print Server Starting...")
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print(f"💾 Database: {DATABASE}")
    print("🌐 Server running on http://0.0.0.0:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### Step 9: Create Systemd Service

Create a service file to auto-start Flask on boot:

```bash
sudo nano /etc/systemd/system/pisoprint.service
```

Add this content:

```ini
[Unit]
Description=Piso Print Flask Server
After=network.target

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
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable pisoprint.service
sudo systemctl start pisoprint.service

# Check status
sudo systemctl status pisoprint.service
```

### Step 10: Test Orange Pi Server

```bash
# Check if Flask is running
curl http://localhost:5000

# Expected output:
# {
#   "status": "online",
#   "message": "Piso Print Server Running",
#   ...
# }
```

---

## 🗄️ Database Schema

The system uses SQLite with 4 main tables:

### Table: `users`
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    credits INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Table: `files`
```sql
CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    pages INTEGER,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES users(session_id)
);
```

### Table: `transactions`
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    type TEXT NOT NULL,           -- 'credit', 'print', 'refund'
    amount INTEGER,
    description TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES users(session_id)
);
```

### Table: `print_jobs`
```sql
CREATE TABLE print_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    file_id INTEGER NOT NULL,
    pages INTEGER,
    cost INTEGER,
    status TEXT DEFAULT 'pending',  -- 'pending', 'printing', 'completed', 'failed'
    cups_job_id INTEGER,
    printed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES users(session_id),
    FOREIGN KEY (file_id) REFERENCES files(id)
);
```

### Database Queries

**View all users:**
```bash
sqlite3 /home/pisoprint/pisoprint.db "SELECT * FROM users;"
```

**View print history:**
```bash
sqlite3 /home/pisoprint/pisoprint.db "SELECT * FROM print_jobs ORDER BY printed_at DESC LIMIT 10;"
```

**Calculate total revenue:**
```bash
sqlite3 /home/pisoprint/pisoprint.db "SELECT SUM(cost) FROM print_jobs WHERE status='printing';"
```

---

## 🔄 System Workflow

### Complete Transaction Flow

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: User Connects to Wi-Fi                             │
├─────────────────────────────────────────────────────────────┤
│ - User scans for Wi-Fi                                      │
│ - Sees "PisoPrint_WiFi"                                     │
│ - Connects (no password required)                           │
│ - ESP32 assigns IP: 192.168.4.X                            │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Captive Portal Redirect                            │
├─────────────────────────────────────────────────────────────┤
│ - User opens any website                                    │
│ - ESP32 DNS intercepts ALL requests                         │
│ - Redirects to: http://192.168.4.1                         │
│ - Upload page loads automatically                           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: File Upload                                        │
├─────────────────────────────────────────────────────────────┤
│ - User selects PDF/DOCX/Image                               │
│ - Clicks "Upload File"                                      │
│ - File sent to: http://192.168.4.2:5000/upload            │
│ - Orange Pi receives file                                   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Page Counting                                      │
├─────────────────────────────────────────────────────────────┤
│ - Orange Pi analyzes file                                   │
│ - PDF: PyPDF2 counts pages                                  │
│ - DOCX: Word count / 500 = pages                           │
│ - Image: Always 1 page                                      │
│ - Calculates cost: pages × ₱1                              │
│ - Returns JSON: {"pages": 5, "cost": 5}                   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: Display Cost                                       │
├─────────────────────────────────────────────────────────────┤
│ - Web page shows: "5 pages = ₱5"                           │
│ - Shows current credits: "₱0"                              │
│ - Message: "Please insert coins"                            │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 6: Coin Insertion                                     │
├─────────────────────────────────────────────────────────────┤
│ - User inserts ₱5 coin                                      │
│ - Coin acceptor sends 5 pulses to GPIO32                    │
│ - ESP32 interrupt handler counts pulses                     │
│ - LED blinks once (feedback)                                │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 7: Credit Update                                      │
├─────────────────────────────────────────────────────────────┤
│ - ESP32 sends POST /api/credits                             │
│   {"session_id": "USER_123", "amount": 5}                  │
│ - Orange Pi updates database                                │
│ - Returns: {"credits": 5}                                  │
│ - Web page updates: "Credits: ₱5"                          │
│ - "Print Now" button enabled                                │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 8: Print Request                                      │
├─────────────────────────────────────────────────────────────┤
│ - User clicks "Print Now"                                   │
│ - ESP32 sends POST /print                                   │
│   {"session_id": "USER_123", "credits": 5}                 │
│ - Orange Pi validates:                                      │
│   ✓ File exists                                            │
│   ✓ Credits sufficient (₱5 >= ₱5)                          │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 9: CUPS Printing                                      │
├─────────────────────────────────────────────────────────────┤
│ - Orange Pi calls CUPS API                                  │
│ - conn_cups.printFile(printer, file, title, {})            │
│ - CUPS queues job                                           │
│ - Sends to USB printer                                      │
│ - Printer starts printing                                   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 10: Transaction Logging                               │
├─────────────────────────────────────────────────────────────┤
│ - Deduct credits: ₱5 - ₱5 = ₱0                             │
│ - Save to print_jobs table                                  │
│ - Save to transactions table                                │
│ - Web page shows: "✅ Printing..."                          │
│ - Page reloads after 2 seconds                              │
└─────────────────────────────────────────────────────────────┘
                          ↓
                   ✅ COMPLETE!
```

---

## 🧪 Testing Instructions

### Test 1: ESP32 Hotspot

```bash
# On your phone/laptop:
1. Search for Wi-Fi networks
2. Connect to "PisoPrint_WiFi"
3. Open browser → should auto-redirect
4. If not, manually go to: http://192.168.4.1
```

**Expected Result:** Upload page loads

### Test 2: File Upload

```bash
1. Click "Choose File"
2. Select a PDF (test.pdf)
3. Click "Upload File"
4. Wait for response
```

**Expected Result:**
```json
{
  "success": true,
  "pages": 3,
  "cost": 3,
  "message": "3 pages = ₱3"
}
```

### Test 3: Coin Detection

```bash
# Without real coin acceptor, test manually:
1. Short GPIO32 to GND 3 times (simulates 3 pulses)
2. Check Serial Monitor
```

**Expected Serial Output:**
```
Credits: ₱3
Credit update response: 200
```

### Test 4: Orange Pi API

```bash
# From Orange Pi terminal or any device on same network:

# Test 1: Check server status
curl http://192.168.1.100:5000/

# Test 2: Add credits manually
curl -X POST http://192.168.1.100:5000/api/credits \
  -H "Content-Type: application/json" \
  -d '{"session_id":"TEST_USER","amount":10}'

# Test 3: Check credits
curl "http://192.168.1.100:5000/api/check_credits?session_id=TEST_USER"

# Test 4: System status
curl http://192.168.1.100:5000/api/status
```

### Test 5: CUPS Printing

```bash
# Check printer status
lpstat -p -d

# Test print
echo "Hello from Piso Print" | lp

# Check print queue
lpq

# Check printer jobs
lpstat -o
```

### Test 6: End-to-End Test

```
1. ✅ Connect to PisoPrint_WiFi
2. ✅ Upload a 2-page PDF
3. ✅ Insert ₱2 (or simulate 2 pulses)
4. ✅ Click "Print Now"
5. ✅ Verify printer starts printing
6. ✅ Check database for transaction record
```

**Verify in database:**
```bash
sqlite3 /home/pisoprint/pisoprint.db

SELECT * FROM print_jobs ORDER BY printed_at DESC LIMIT 1;
SELECT * FROM transactions ORDER BY timestamp DESC LIMIT 5;
```

---

## 📡 API Documentation

### Base URL
```
http://192.168.1.100:5000
```

### Endpoints

#### `GET /`
**Description:** Server health check

**Response:**
```json
{
  "status": "online",
  "message": "Piso Print Server Running",
  "version": "1.0.0"
}
```

---

#### `POST /upload`
**Description:** Upload file for printing

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body:
  - `file`: File data (PDF/DOCX/Image)
  - `session_id`: User session ID (optional)

**Response:**
```json
{
  "success": true,
  "file_id": 123,
  "filename": "document.pdf",
  "pages": 5,
  "cost": 5,
  "message": "5 pages = ₱5"
}
```

---

#### `POST /print`
**Description:** Trigger print job

**Request:**
```json
{
  "session_id": "USER_123456",
  "credits": 10
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Printing started",
  "pages": 5,
  "cost": 5,
  "remaining_credits": 5,
  "job_id": 42
}
```

**Response (Insufficient Credits):**
```json
{
  "success": false,
  "message": "Insufficient credits. Need ₱5, have ₱3"
}
```

---

#### `POST /api/credits`
**Description:** Add credits to user account

**Request:**
```json
{
  "session_id": "USER_123456",
  "amount": 5
}
```

**Response:**
```json
{
  "success": true,
  "credits": 15,
  "added": 5
}
```

---

#### `GET /api/check_credits`
**Description:** Check user credit balance

**Parameters:**
- `session_id` (query parameter)

**Example:**
```
GET /api/check_credits?session_id=USER_123456
```

**Response:**
```json
{
  "success": true,
  "session_id": "USER
  _123456",
  "credits": 15
}
```

---

#### `GET /api/status`
**Description:** Get system status and statistics

**Response:**
```json
{
  "success": true,
  "printers": [
    {
      "name": "PisoPrinter",
      "state": "idle",
      "accepting_jobs": true
    }
  ],
  "stats": {
    "total_users": 42,
    "total_jobs": 156,
    "total_revenue": 780
  }
}
```

---

#### `GET /api/history`
**Description:** Get print history

**Parameters:**
- `session_id` (optional): Filter by user
- `limit` (optional, default=10): Number of records

**Example:**
```
GET /api/history?session_id=USER_123456&limit=5
```

**Response:**
```json
{
  "success": true,
  "history": [
    {
      "id": 156,
      "session_id": "USER_123456",
      "original_filename": "document.pdf",
      "pages": 5,
      "cost": 5,
      "status": "printing",
      "printed_at": "2025-10-19 14:30:00"
    }
  ]
}
```

---

## 🐛 Troubleshooting

### ESP32 Issues

#### Problem: ESP32 not creating hotspot
**Solution:**
```cpp
// Check Serial Monitor for errors
// Verify WiFi.softAP() returns true

// Try this code to debug:
bool result = WiFi.softAP(AP_SSID, AP_PASS);
Serial.print("AP Status: ");
Serial.println(result ? "SUCCESS" : "FAILED");
Serial.println(WiFi.softAPIP());
```

#### Problem: Captive portal not redirecting
**Solution:**
```cpp
// Ensure DNS server is running
dnsServer.start(53, "*", WiFi.softAPIP());

// Add this in loop():
dnsServer.processNextRequest();

// Test DNS manually from phone terminal:
nslookup google.com 192.168.4.1
```

#### Problem: Coin pulses not detected
**Solution:**
```bash
# Check wiring
# Test with multimeter: White wire should pulse LOW when coin inserted

# Add debug code:
void IRAM_ATTR coinInserted() {
  coinPulses++;
  Serial.println("COIN PULSE!");
}

# Test manually: Touch GPIO32 to GND
```

#### Problem: HTTP requests failing
**Solution:**
```cpp
// Check Orange Pi IP is correct
// Ping Orange Pi from ESP32:

WiFiClient client;
if (client.connect("192.168.4.2", 5000)) {
  Serial.println("Connection OK");
} else {
  Serial.println("Connection FAILED");
}
```

---

### Orange Pi Issues

#### Problem: Flask not starting
**Solution:**
```bash
# Check service status
sudo systemctl status pisoprint.service

# View logs
sudo journalctl -u pisoprint.service -f

# Test manually
cd /home/pisoprint
source venv/bin/activate
python app.py

# Check port 5000
sudo netstat -tulpn | grep 5000
```

#### Problem: CUPS not printing
**Solution:**
```bash
# Check printer status
lpstat -p -d

# Check if printer is accepting jobs
cupsenable PisoPrinter
cupsaccept PisoPrinter

# View CUPS error log
sudo tail -f /var/log/cups/error_log

# Restart CUPS
sudo systemctl restart cups

# Test print directly
echo "test" | lp -d PisoPrinter
```

#### Problem: Printer not detected
**Solution:**
```bash
# List USB devices
lsusb

# Check if printer driver installed
lpinfo -m | grep -i "your_printer_brand"

# Reinstall drivers
sudo apt install --reinstall printer-driver-all

# Add printer manually
sudo lpadmin -p PisoPrinter -E -v usb://YOUR/PRINTER/URI -m everywhere
```

#### Problem: Permission denied errors
**Solution:**
```bash
# Fix file permissions
sudo chown -R root:root /home/pisoprint
sudo chmod -R 755 /home/pisoprint

# Fix database permissions
sudo chmod 666 /home/pisoprint/pisoprint.db

# Add user to lpadmin group
sudo usermod -a -G lpadmin root
```

#### Problem: Database locked
**Solution:**
```bash
# Check if database is being accessed
lsof /home/pisoprint/pisoprint.db

# Kill blocking process
sudo kill -9 <PID>

# Or recreate database
cd /home/pisoprint
mv pisoprint.db pisoprint.db.backup
# Restart Flask (will auto-create new DB)
sudo systemctl restart pisoprint.service
```

---

### Network Issues

#### Problem: ESP32 and Orange Pi can't communicate
**Solution:**
```bash
# From Orange Pi, ping ESP32:
ping 192.168.4.1

# From ESP32 Serial Monitor:
# Add this to setup():
WiFi.mode(WIFI_AP_STA);
WiFi.softAP(AP_SSID, AP_PASS);
// Connect Orange Pi to ESP32 Wi-Fi

# Or use Ethernet:
# Connect both devices to same router
# Set static IPs on both
```

#### Problem: Captive portal not working on iOS
**Solution:**
```cpp
// iOS requires specific captive portal detection
// Add these routes to ESP32:

server.on("/hotspot-detect.html", handleRoot);
server.on("/generate_204", handleRoot);
server.on("/gen_204", handleRoot);
server.on("/ncsi.txt", handleRoot);
server.on("/success.txt", handleRoot);
```

#### Problem: Uploads failing
**Solution:**
```bash
# Check file size limit
# In Flask app.py:
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

# Check disk space
df -h

# Check upload folder permissions
ls -la /home/pisoprint/uploads/
sudo chmod 777 /home/pisoprint/uploads/
```

---

### Hardware Issues

#### Problem: Coin acceptor not working
**Troubleshooting Steps:**
```bash
1. Test coin acceptor voltage:
   - Red wire: Should have 5V
   - White wire: Should pulse LOW (0V) when coin inserted

2. Verify coin acceptor settings:
   - Check DIP switches inside coin acceptor
   - Set to correct coin denominations

3. Test with multimeter:
   - Set to continuity mode
   - Insert coin
   - White wire should beep/show connection to GND

4. ESP32 test code:
void loop() {
  int state = digitalRead(COIN_PIN);
  Serial.print("Coin Pin: ");
  Serial.println(state);  // Should be HIGH normally, LOW when coin pulse
  delay(100);
}
```

#### Problem: Power issues
**Solution:**
```bash
# ESP32 power:
- Minimum: 5V 500mA
- Recommended: 5V 1A
- With coin acceptor: 5V 1.5A

# Orange Pi power:
- Minimum: 5V 2A
- Recommended: 5V 3A
- Check voltage with multimeter (should be 5.0-5.2V)

# If voltage drops below 4.8V, system will be unstable
```

---

## 📁 Project Structure

```
pisoprint/
│
├── esp32/
│   ├── PisoPrint_ESP32.ino          # Main ESP32 sketch
│   ├── credentials.h                 # Wi-Fi credentials (optional)
│   └── README.md                     # ESP32 setup instructions
│
├── orangepi/
│   ├── app.py                        # Flask web server
│   ├── requirements.txt              # Python dependencies
│   ├── uploads/                      # Uploaded files directory
│   ├── pisoprint.db                  # SQLite database
│   └── README.md                     # Orange Pi setup instructions
│
├── docs/
│   ├── wiring_diagram.png            # Hardware connections
│   ├── architecture.png              # System architecture
│   ├── api_documentation.md          # API reference
│   └── troubleshooting.md            # Common issues
│
├── scripts/
│   ├── install_orangepi.sh           # Auto-install script for Orange Pi
│   ├── backup_database.sh            # Database backup script
│   └── monitor_system.sh             # System monitoring script
│
├── tests/
│   ├── test_esp32.ino                # ESP32 unit tests
│   ├── test_flask.py                 # Flask API tests
│   └── test_coins.ino                # Coin acceptor test
│
├── README.md                         # This file
├── LICENSE                           # MIT License
└── .gitignore                        # Git ignore rules
```

### File Contents

#### `requirements.txt`
```txt
flask==3.0.0
flask-cors==4.0.0
pycups==2.0.1
PyPDF2==3.0.1
python-docx==1.1.0
pillow==10.1.0
werkzeug==3.0.1
```

#### `.gitignore`
```
# Python
__pycache__/
*.py[cod]
*$py.class
venv/
env/

# Database
*.db
*.sqlite3

# Uploads
uploads/*
!uploads/.gitkeep

# Logs
*.log

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
```

---

## 🚀 Future Enhancements

### Phase 1: Basic Improvements (1-2 weeks)

#### 1.1 LCD Display
```cpp
// Add 16x2 LCD to show status
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

void displayStatus(String line1, String line2) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(line1);
  lcd.setCursor(0, 1);
  lcd.print(line2);
}

// Usage:
displayStatus("Insert Coins", "Need: P5");
```

#### 1.2 Multiple Printers
```python
# Flask: Add printer selection
@app.route('/printers', methods=['GET'])
def list_printers():
    printers = conn_cups.getPrinters()
    return jsonify({
        'printers': [
            {'name': name, 'info': info}
            for name, info in printers.items()
        ]
    })

@app.route('/print', methods=['POST'])
def print_file():
    data = request.get_json()
    printer_name = data.get('printer', 'default')
    # ... rest of code
```

#### 1.3 Print Preview
```python
# Convert PDF to images for preview
from pdf2image import convert_from_path

@app.route('/preview/<file_id>')
def preview_file(file_id):
    # Get file from database
    # Convert first page to image
    # Return as base64 or image URL
    pass
```

---

### Phase 2: Payment Integration (2-4 weeks)

#### 2.1 QR Code Payments (GCash/Maya)
```python
# Install: pip install qrcode paymongo

import qrcode
from paymongo import PayMongo

@app.route('/payment/qr', methods=['POST'])
def create_qr_payment():
    amount = request.json.get('amount')
    
    # Create PayMongo payment intent
    payment = PayMongo.create_payment_intent(
        amount=amount * 100,  # Convert to centavos
        currency='PHP',
        description='Piso Print Payment'
    )
    
    # Generate QR code
    qr = qrcode.make(payment['attributes']['payment_url'])
    
    return jsonify({
        'qr_image': qr_to_base64(qr),
        'payment_id': payment['id']
    })
```

#### 2.2 Bill Acceptor Support
```cpp
// ESP32: Add bill acceptor on different GPIO
const int BILL_PIN = 33;

void IRAM_ATTR billInserted() {
  // Bills typically send different pulse patterns
  // 20 peso = 20 pulses
  // 50 peso = 50 pulses
  billPulses++;
}
```

---

### Phase 3: Web Dashboard (3-4 weeks)

#### 3.1 Admin Panel
```python
# Flask: Add admin routes
from flask import render_template

@app.route('/admin')
def admin_dashboard():
    return render_template('admin.html')

@app.route('/admin/stats')
def admin_stats():
    db = get_db()
    
    # Daily revenue
    daily = db.execute('''
        SELECT DATE(printed_at) as date, SUM(cost) as revenue
        FROM print_jobs
        GROUP BY DATE(printed_at)
        ORDER BY date DESC
        LIMIT 30
    ''').fetchall()
    
    # Popular files
    popular = db.execute('''
        SELECT original_filename, COUNT(*) as prints
        FROM print_jobs
        JOIN files ON print_jobs.file_id = files.id
        GROUP BY original_filename
        ORDER BY prints DESC
        LIMIT 10
    ''').fetchall()
    
    return jsonify({
        'daily_revenue': [dict(row) for row in daily],
        'popular_files': [dict(row) for row in popular]
    })
```

#### 3.2 React Frontend
```jsx
// Create React admin dashboard
import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis } from 'recharts';

function AdminDashboard() {
  const [stats, setStats] = useState(null);
  
  useEffect(() => {
    fetch('/admin/stats')
      .then(r => r.json())
      .then(setStats);
  }, []);
  
  return (
    <div className="dashboard">
      <h1>Piso Print Admin</h1>
      <LineChart data={stats?.daily_revenue}>
        <Line dataKey="revenue" stroke="#8884d8" />
        <XAxis dataKey="date" />
        <YAxis />
      </LineChart>
    </div>
  );
}
```

---

### Phase 4: Cloud Integration (4-6 weeks)

#### 4.1 Remote Monitoring
```python
# Add Firebase or AWS IoT integration
import firebase_admin

@app.route('/api/cloud_sync', methods=['POST'])
def sync_to_cloud():
    # Upload daily stats to cloud
    db = get_db()
    stats = get_daily_stats()
    
    firebase_admin.db.reference('/stats').push(stats)
    
    return jsonify({'success': True})
```

#### 4.2 Mobile App
```javascript
// React Native app for users
import React from 'react';
import { View, Text, Button } from 'react-native';

function PrintScreen() {
  const uploadFile = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('http://192.168.1.100:5000/upload', {
      method: 'POST',
      body: formData
    });
    
    return response.json();
  };
  
  return (
    <View>
      <Text>Piso Print</Text>
      <Button title="Upload Document" onPress={() => {}} />
    </View>
  );
}
```

---

### Phase 5: Advanced Features (6+ weeks)

#### 5.1 Double-Sided Printing
```python
# CUPS: Enable duplex printing
@app.route('/print', methods=['POST'])
def print_file():
    options = {
        'sides': 'two-sided-long-edge',
        'media': 'A4',
        'print-color-mode': 'monochrome'
    }
    
    cups_job_id = conn_cups.printFile(
        printer_name,
        filepath,
        filename,
        options
    )
```

#### 5.2 Print Job Scheduling
```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

@app.route('/schedule_print', methods=['POST'])
def schedule_print():
    data = request.json
    scheduled_time = data['scheduled_time']
    
    scheduler.add_job(
        func=print_document,
        trigger='date',
        run_date=scheduled_time,
        args=[data['file_id']]
    )
    
    return jsonify({'success': True})
```

#### 5.3 Membership System
```sql
-- Add membership table
CREATE TABLE memberships (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    tier TEXT,  -- 'basic', 'silver', 'gold'
    discount_percent INTEGER,
    valid_until DATE
);
```

#### 5.4 Print Templates
```python
# Predefined templates (certificates, forms, etc.)
@app.route('/templates')
def list_templates():
    templates = [
        {'id': 1, 'name': 'Certificate', 'price': 5},
        {'id': 2, 'name': 'Resume', 'price': 3},
        {'id': 3, 'name': 'ID Picture', 'price': 10}
    ]
    return jsonify(templates)
```

---

## 📊 Performance Optimization

### ESP32 Optimization
```cpp
// Reduce memory usage
#define MAX_CLIENTS 4  // Limit simultaneous connections

// Use PROGMEM for large strings
const char html_template[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
...
)rawliteral";

// Optimize Wi-Fi
WiFi.setTxPower(WIFI_POWER_19_5dBm);  // Max power
WiFi.setSleep(false);  // Disable sleep
```

### Orange Pi Optimization
```bash
# Use Gunicorn for production
pip install gunicorn

# Run with multiple workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Use nginx as reverse proxy
sudo apt install nginx

# Configure nginx
sudo nano /etc/nginx/sites-available/pisoprint
```

Nginx config:
```nginx
server {
    listen 80;
    server_name pisoprint.local;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🔐 Security Considerations

### ESP32 Security
```cpp
// Add password to Wi-Fi (optional)
const char* AP_PASS = "print1234";

// Rate limiting
unsigned long lastUpload = 0;
const unsigned long UPLOAD_COOLDOWN = 5000;  // 5 seconds

if (millis() - lastUpload < UPLOAD_COOLDOWN) {
  server.send(429, "text/plain", "Too many requests");
  return;
}
```

### Flask Security
```python
# Add API key authentication
API_KEY = "your_secret_key_here"

@app.before_request
def check_api_key():
    if request.endpoint != 'index':
        key = request.headers.get('X-API-Key')
        if key != API_KEY:
            return jsonify({'error': 'Unauthorized'}), 401

# Sanitize filenames
from werkzeug.utils import secure_filename

filename = secure_filename(file.filename)

# Validate file content
import magic

def is_valid_pdf(filepath):
    mime = magic.from_file(filepath, mime=True)
    return mime == 'application/pdf'
```

---

## 📝 License

```
MIT License

Copyright (c) 2025 Piso Print Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
4. **Push to branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**

---

## 📞 Support

- **GitHub Issues:** [github.com/yourrepo/pisoprint/issues](https://github.com)
- **Email:** support@pisoprint.local
- **Discord:** [discord.gg/pisoprint](https://discord.com)

---

## 🎉 Acknowledgments

- **Espressif** - ESP32 development platform
- **Armbian** - Orange Pi OS
- **Flask** - Python web framework
- **CUPS** - Printing system
- **Arduino Community** - Libraries and support

---

## 📸 Screenshots

### User Interface
```
[Captive Portal]  [Upload Screen]  [Credit Display]  [Printing Status]
```

### Admin Dashboard
```
[Revenue Chart]   [Print History]  [System Status]   [User Analytics]
```

---

## 🏁 Quick Start Summary

```bash
# 1. ESP32
- Upload PisoPrint_ESP32.ino
- Connect coin acceptor to GPIO32

# 2. Orange Pi
sudo apt update
cd /home/pisoprint
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py

# 3. Test
- Connect to "PisoPrint_WiFi"
- Upload a PDF
- Insert coins
- Click Print!
```

---

**🎊 Congratulations! Your Piso Print System is now complete! 🎊**

---

**README Version:** 1.0.0  
**Last Updated:** October 19, 2025  
**Tested On:** ESP32-WROOM-32, Orange Pi PC H3, Armbian Ubuntu 22.04
