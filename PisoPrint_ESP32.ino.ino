#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <map>

// ============================================
// Configuration
// ============================================
const char* AP_SSID = "PisoPrint_WiFi_v2";
const char* AP_PASS = ""; // Open network

// WiFi Station Mode - Connect to your router (where Orange Pi is connected)
const char* STA_SSID = "HomeUltera_E73DD4";      // Change this to your router's WiFi name
const char* STA_PASS = "Ultera9wiid2";   // Change this to your router's password

// Orange Pi Flask Server
const char* FLASK_SERVER = "http://192.168.22.2:5000";  // Orange Pi IP on your network

// Pin Definitions
const int COIN_PIN = 32;  // D32 - Coin acceptor (NO mode)
#define BUZZER_PIN 25     // D25 - Buzzer

// DNS Server for Captive Portal
DNSServer dnsServer;
WebServer server(80);

// ============================================
// Variables - Optimized for MEDIUM speed
// ============================================
volatile int pulseCount = 0;
volatile unsigned long lastPulseTime = 0;

// Timing adjusted for MEDIUM speed + NO mode
const unsigned long COIN_TIMEOUT = 500;      // 500ms timeout (medium speed)
const unsigned long DEBOUNCE_TIME = 50;      // 50ms debounce (filter noise)
const unsigned long MIN_PULSE_WIDTH = 20;    // Minimum 20ms pulse width
const unsigned long NOISE_FILTER_TIME = 2000; // Ignore pulses in first 2 seconds after startup

// ============================================
// Session Management - Per-User Credits
// ============================================
volatile int pendingCredits = 0;  // Credits not yet claimed by any user
std::map<String, int> userCredits;  // SessionID → Credits
std::map<String, String> sessionIPs;  // IP → SessionID
std::map<String, String> userFiles;  // SessionID → Uploaded filename (NEW!)
std::map<String, int> userFileIDs;  // SessionID → File ID from Orange Pi
String uploadedFileName = "";  // Current uploaded file name


// Buzzer state machine
enum BuzzerState {
  BUZZER_IDLE,
  BUZZER_BEEP_ON,
  BUZZER_BEEP_OFF,
  BUZZER_HOLD
};

BuzzerState buzzerState = BUZZER_IDLE;
unsigned long buzzerStartTime = 0;
int buzzerBeatsRemaining = 0;
const unsigned long BUZZER_BEEP_DURATION = 100;
const unsigned long BUZZER_BEEP_INTERVAL = 150;
const unsigned long BUZZER_HOLD_DURATION = 500;

// Coin detection state
bool coinDetectionActive = false;
unsigned long coinDetectionStartTime = 0;
unsigned long systemStartTime = 0;  // Track when system started

// ============================================
// Buzzer Functions
// ============================================
void playBuzzer(int beats) {
  if (buzzerState != BUZZER_IDLE) return;
  
  buzzerBeatsRemaining = beats;
  buzzerState = BUZZER_BEEP_ON;
  digitalWrite(BUZZER_PIN, HIGH);
  buzzerStartTime = millis();
  
  Serial.print("🔊 Buzzer: ");
  Serial.print(beats);
  Serial.println(" beat(s)");
}

void updateBuzzer() {
  if (buzzerState == BUZZER_IDLE) return;
  
  unsigned long currentTime = millis();
  unsigned long elapsed = currentTime - buzzerStartTime;
  
  switch (buzzerState) {
    case BUZZER_BEEP_ON:
      if (elapsed >= BUZZER_BEEP_DURATION) {
        digitalWrite(BUZZER_PIN, LOW);
        buzzerBeatsRemaining--;
        
        if (buzzerBeatsRemaining > 0) {
          buzzerState = BUZZER_BEEP_OFF;
          buzzerStartTime = currentTime;
        } else {
          buzzerState = BUZZER_HOLD;
          digitalWrite(BUZZER_PIN, HIGH);
          buzzerStartTime = currentTime;
        }
      }
      break;
      
    case BUZZER_BEEP_OFF:
      if (elapsed >= BUZZER_BEEP_INTERVAL) {
        digitalWrite(BUZZER_PIN, HIGH);
        buzzerState = BUZZER_BEEP_ON;
        buzzerStartTime = currentTime;
      }
      break;
      
    case BUZZER_HOLD:
      if (elapsed >= BUZZER_HOLD_DURATION) {
        digitalWrite(BUZZER_PIN, LOW);
        buzzerState = BUZZER_IDLE;
        Serial.println("🔊 Ready for next coin");
      }
      break;
      
    default:
      buzzerState = BUZZER_IDLE;
      digitalWrite(BUZZER_PIN, LOW);
      break;
  }
}

// ============================================
// Coin Interrupt - Optimized for NO mode with noise filtering
// ============================================
void IRAM_ATTR coinInserted() {
  unsigned long currentTime = millis();
  
  // Ignore pulses in first 2 seconds (power-on noise)
  if (currentTime < NOISE_FILTER_TIME) {
    return;
  }
  
  // Debounce check
  if (currentTime - lastPulseTime < DEBOUNCE_TIME) {
    return; // Too soon, ignore
  }
  
  // Valid pulse detected
  pulseCount++;
  lastPulseTime = currentTime;
  
  // Mark that we're in coin detection phase
  if (!coinDetectionActive) {
    coinDetectionActive = true;
    coinDetectionStartTime = currentTime;
  }
}

// ============================================
// Setup
// ============================================
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n=================================");
  Serial.println("🖨️ PISO PRINT SYSTEM v2.0");
  Serial.println("=================================");
  
  // Pin setup
  pinMode(COIN_PIN, INPUT_PULLUP);  // For NO (Normally Open) mode
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);
  
  // Coin acceptor interrupt (FALLING edge for NO mode)
  attachInterrupt(digitalPinToInterrupt(COIN_PIN), coinInserted, FALLING);

  // Wi-Fi AP+STA Mode (Dual mode: Hotspot + Connect to router)
  WiFi.mode(WIFI_AP_STA);  // Enable both AP and Station modes
  
  // Start Access Point for users
  WiFi.softAP(AP_SSID, AP_PASS);
  Serial.println("📶 Hotspot: " + String(AP_SSID));
  Serial.print("🔗 Hotspot IP: ");
  Serial.println(WiFi.softAPIP());
  
  // Connect to router (where Orange Pi is)
  Serial.print("🔌 Connecting to router: ");
  Serial.println(STA_SSID);
  WiFi.begin(STA_SSID, STA_PASS);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ Connected to router!");
    Serial.print("🌐 Station IP: ");
    Serial.println(WiFi.localIP());
    Serial.print("🖨️  Can reach Orange Pi at: ");
    Serial.println(FLASK_SERVER);
  } else {
    Serial.println("\n⚠️  Router connection failed!");
    Serial.println("   ESP32 will work in AP-only mode");
    Serial.println("   Upload feature will not work");
  }

  // DNS server
  dnsServer.start(53, "*", WiFi.softAPIP());

  // Web routes
  server.on("/", handleRoot);
  server.on("/upload", HTTP_POST, handleUploadResponse, handleFileUpload);
  server.on("/upload_proxy", HTTP_POST, handleUploadProxy, handleFileUploadProxy);  // NEW: File proxy
  server.on("/status", handleStatus);
  server.on("/claim", handleClaimCredits);  // NEW: Claim pending credits
  server.on("/print", handlePrint);
  server.onNotFound(handleRoot);

  server.begin();
  Serial.println("🌐 Web server started");
  
  Serial.println("=================================");
  Serial.println("⚙️  Coin Acceptor Settings:");
  Serial.println("   Speed: MEDIUM");
  Serial.println("   Mode: NO (Normally Open)");
  Serial.println("   Wire: COUNTER (Gray) → Pin 32");
  Serial.println("   Pin: GPIO 32");
  Serial.println("   Noise Filter: 2 seconds");
  Serial.println("=================================");
  
  // Startup beeps
  playBuzzer(2);
  
  // Record startup time for noise filtering
  systemStartTime = millis();
  
  Serial.println("✅ System Ready!");
  Serial.println("⏳ Waiting 2 seconds for coin acceptor to stabilize...");
  Serial.println("=================================\n");
}

// ============================================
// Main Loop
// ============================================
void loop() {
  dnsServer.processNextRequest();
  server.handleClient();
  updateBuzzer();
  checkCoinType();
}

// ============================================
// Enhanced Coin Detection for MEDIUM speed
// ============================================
void checkCoinType() {
  unsigned long now = millis();

  // Check if we're in detection phase and timeout passed
  if (coinDetectionActive && (now - lastPulseTime > COIN_TIMEOUT)) {
    coinDetectionActive = false;
    
    int detectedPulses = pulseCount;
    pulseCount = 0; // Reset immediately
    
    // Ignore very short pulses (likely noise)
    if (detectedPulses == 0) return;

    int coinValue = 0;
    int buzzerBeats = 0;
    String coinName = "";
    
    // Coin identification with tolerance
    if (detectedPulses == 1) {
      coinValue = 1;
      buzzerBeats = 1;
      coinName = "₱1";
    } 
    else if (detectedPulses >= 4 && detectedPulses <= 6) {
      coinValue = 5;
      buzzerBeats = 2;
      coinName = "₱5";
    } 
    else if (detectedPulses >= 9 && detectedPulses <= 12) {
      coinValue = 10;
      buzzerBeats = 3;
      coinName = "₱10";
    }

    if (coinValue > 0) {
      pendingCredits += coinValue;

      Serial.println("\n╔═════════════════════════════════╗");
      Serial.print("║ 💰 COIN ACCEPTED: ");
      Serial.print(coinName);
      Serial.println("              ║");
      Serial.print("║ 📊 Pulses: ");
      Serial.print(detectedPulses);
      Serial.println("                     ║");
      Serial.print("║ 💵 Pending Credits: ₱");
      Serial.print(pendingCredits);
      Serial.println("             ║");
      Serial.println("║ 👉 User must CLAIM credits      ║");
      Serial.println("╚═════════════════════════════════╝\n");

      playBuzzer(buzzerBeats);
    } 
    else {
      Serial.println("\n⚠️  INVALID COIN DETECTED");
      Serial.print("   Pulses: ");
      Serial.println(detectedPulses);
      Serial.println("   Expected: 1 (₱1), 5 (₱5), or 10 (₱10)");
      Serial.println("");
      Serial.println("   � TROUBLESHOOTING:");
      Serial.println("   1. Use COUNTER (Gray wire) → Pin 32");
      Serial.println("   2. Check coin acceptor is set to NO mode");
      Serial.println("   3. Try different coins (clean ones)");
      Serial.println("   4. Check if coin path is clear");
      Serial.println("");
      
      // Error beep
      if (buzzerState == BUZZER_IDLE) {
        for (int i = 0; i < 5; i++) {
          digitalWrite(BUZZER_PIN, HIGH);
          delay(50);
          digitalWrite(BUZZER_PIN, LOW);
          delay(50);
        }
      }
    }
  }
}

// ============================================
// Web Server Handlers (same as before)
// ============================================
void handleRoot() {
  String html = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Piso Print v2</title>
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
      animation: slideIn 0.5s ease-out;
    }
    @keyframes slideIn {
      from { opacity: 0; transform: translateY(-20px); }
      to { opacity: 1; transform: translateY(0); }
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
      background: linear-gradient(135deg, #f0f4ff 0%, #e8f0fe 100%);
      padding: 20px;
      border-radius: 10px;
      text-align: center;
      margin-bottom: 30px;
      border: 2px solid #667eea;
      transition: all 0.3s;
    }
    .credits:hover {
      transform: scale(1.02);
      box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    .credits h2 { 
      color: #667eea; 
      margin-bottom: 10px; 
      font-size: 1.2em;
    }
    .credits .amount {
      font-size: 3em;
      font-weight: bold;
      color: #764ba2;
      transition: all 0.3s;
    }
    .credits .amount.updated {
      animation: pulse 0.5s ease-out;
    }
    @keyframes pulse {
      0%, 100% { transform: scale(1); }
      50% { transform: scale(1.1); color: #4CAF50; }
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
      transform: translateY(-2px);
    }
    .upload-area input[type="file"] { display: none; }
    .upload-icon { font-size: 4em; margin-bottom: 10px; }
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
    .btn-primary:hover:not(:disabled) {
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
      animation: fadeIn 0.3s;
    }
    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    .status.success { background: #d4edda; color: #155724; display: block; }
    .status.error { background: #f8d7da; color: #721c24; display: block; }
    .status.info { background: #d1ecf1; color: #0c5460; display: block; }
    .file-name {
      margin-top: 10px;
      padding: 10px;
      background: #e8f5e9;
      border-radius: 5px;
      display: none;
      animation: slideIn 0.3s;
    }
    .loading {
      display: inline-block;
      width: 20px;
      height: 20px;
      border: 3px solid rgba(255,255,255,.3);
      border-radius: 50%;
      border-top-color: #fff;
      animation: spin 1s ease-in-out infinite;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    .pending-credits {
      background: linear-gradient(135deg, #fff3cd 0%, #ffe69c 100%);
      padding: 20px;
      border-radius: 10px;
      text-align: center;
      margin-bottom: 20px;
      border: 2px solid #ffc107;
      display: none;
      animation: slideIn 0.3s;
    }
    .pending-credits h3 {
      color: #856404;
      margin-bottom: 10px;
    }
    .pending-amount {
      font-size: 2em;
      font-weight: bold;
      color: #ff6b6b;
      margin-bottom: 15px;
    }
    .btn-claim {
      background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
      color: white;
      padding: 12px 30px;
      border: none;
      border-radius: 10px;
      font-size: 1.1em;
      font-weight: bold;
      cursor: pointer;
      transition: all 0.3s;
    }
    .btn-claim:hover {
      transform: translateY(-2px);
      box-shadow: 0 5px 15px rgba(255, 193, 7, 0.4);
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>🖨️ Piso Print</h1>
    <p class="subtitle">Upload • Insert Coins • Print</p>
    
    <div class="pending-credits" id="pendingCredits">
      <h3>💵 Pending Credits Available!</h3>
      <div class="pending-amount">₱<span id="pendingAmount">0</span></div>
      <button class="btn-claim" onclick="claimCredits()">Claim These Credits</button>
    </div>
    
    <div class="credits">
      <h2>Your Credits</h2>
      <div class="amount" id="credits">₱<span id="creditAmount">0</span></div>
    </div>
    
    <form id="uploadForm" enctype="multipart/form-data">
      <div class="upload-area" onclick="document.getElementById('fileInput').click()">
        <div class="upload-icon">📄</div>
        <h3>Click to Upload Document</h3>
        <p>PDF files recommended (max 50KB)</p>
        <p style="font-size: 0.9em; color: #999; margin-top: 5px;">DOCX/Images: May have printing issues</p>
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
    let lastKnownCredits = 0;

    function updateCredits() {
      fetch('/status')
        .then(r => r.json())
        .then(data => {
          const creditElement = document.getElementById('creditAmount');
          const newCredits = data.credits;
          
          // Update user credits display
          if (newCredits !== lastKnownCredits) {
            creditElement.parentElement.classList.add('updated');
            setTimeout(() => {
              creditElement.parentElement.classList.remove('updated');
            }, 500);
            lastKnownCredits = newCredits;
          }
          
          creditElement.textContent = newCredits;
          
          // Update pending credits display
          const pendingDiv = document.getElementById('pendingCredits');
          const pendingAmount = document.getElementById('pendingAmount');
          
          if (data.pending && data.pending > 0) {
            pendingAmount.textContent = data.pending;
            pendingDiv.style.display = 'block';
          } else {
            pendingDiv.style.display = 'none';
          }
          
          checkPrintButton();
        })
        .catch(err => console.error('Credit update error:', err));
    }

    function claimCredits() {
      fetch('/claim', { method: 'POST' })
        .then(r => r.json())
        .then(data => {
          if (data.success) {
            showStatus('✅ Claimed ₱' + data.claimed + '!', 'success');
            updateCredits();
          } else {
            showStatus('❌ ' + data.message, 'error');
          }
        })
        .catch(err => {
          showStatus('❌ Claim failed', 'error');
          console.error(err);
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

      // Get session ID first
      fetch('/status')
        .then(r => r.json())
        .then(statusData => {
          const sessionId = statusData.session;
          
          const formData = new FormData();
          formData.append('file', uploadedFile);
          formData.append('session_id', sessionId);

          const uploadBtn = document.getElementById('uploadBtn');
          uploadBtn.disabled = true;
          uploadBtn.innerHTML = '<div class="loading"></div>';
          showStatus('Uploading to server...', 'info');

          // Upload to ESP32 first (phone can reach this)
          // ESP32 will forward to Orange Pi
          fetch('/upload_proxy', {
            method: 'POST',
            body: formData
          })
          .then(r => r.json())
          .then(data => {
            if (data.success) {
              requiredCredits = data.pages;
              showStatus('✅ File uploaded! ' + data.pages + ' pages = ₱' + data.cost, 'success');
              document.getElementById('printBtn').disabled = false;
              checkPrintButton();
            } else {
              showStatus('❌ Upload failed: ' + data.error, 'error');
            }
          })
          .catch(err => {
            showStatus('❌ Upload error - Check connection', 'error');
            console.error(err);
          })
          .finally(() => {
            uploadBtn.disabled = false;
            uploadBtn.textContent = 'Upload File';
          });
        })
        .catch(err => {
          showStatus('❌ Session error', 'error');
          console.error(err);
        });
    }

    function printFile() {
      const printBtn = document.getElementById('printBtn');
      printBtn.disabled = true;
      printBtn.innerHTML = '<div class="loading"></div>';
      
      fetch('/print')
        .then(r => r.json())
        .then(data => {
          if (data.success) {
            showStatus('✅ Printing...', 'success');
            setTimeout(() => { location.reload(); }, 2000);
          } else {
            showStatus('❌ ' + data.message, 'error');
            printBtn.disabled = false;
            printBtn.textContent = 'Print Now';
          }
        })
        .catch(err => {
          showStatus('❌ Print error', 'error');
          console.error(err);
          printBtn.disabled = false;
          printBtn.textContent = 'Print Now';
        });
    }

    function checkPrintButton() {
      const credits = parseInt(document.getElementById('creditAmount').textContent);
      const printBtn = document.getElementById('printBtn');
      
      if (credits >= requiredCredits && requiredCredits > 0) {
        printBtn.disabled = false;
        printBtn.style.background = 'linear-gradient(135deg, #4CAF50 0%, #45a049 100%)';
      } else {
        printBtn.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
      }
    }

    function showStatus(message, type) {
      const status = document.getElementById('status');
      status.textContent = message;
      status.className = 'status ' + type;
      status.style.display = 'block';
      
      if (type === 'info') {
        setTimeout(() => { status.style.display = 'none'; }, 3000);
      }
    }

    setInterval(updateCredits, 1500);
    updateCredits();
    checkPrintButton();
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
    Serial.println("\n📤 Upload: " + uploadedFileName);
  }
}

void handleUploadResponse() {
  String clientIP = server.client().remoteIP().toString();
  String sessionID = sessionIPs[clientIP];
  
  if (sessionID == "") {
    server.send(400, "application/json", "{\"success\":false,\"error\":\"No session\"}");
    return;
  }
  
  userFiles[sessionID] = uploadedFileName;
  
  // Send filename to Orange Pi for page counting
  HTTPClient http;
  http.setTimeout(10000);
  http.begin(String(FLASK_SERVER) + "/api/check_pages");
  http.addHeader("Content-Type", "application/json");
  
  StaticJsonDocument<200> doc;
  doc["filename"] = uploadedFileName;
  doc["session_id"] = sessionID;
  
  String requestBody;
  serializeJson(doc, requestBody);
  
  Serial.println("📡 Requesting page count from Orange Pi...");
  int httpCode = http.POST(requestBody);
  
  if (httpCode == 200) {
    String response = http.getString();
    Serial.println("✅ Page count received: " + response);
    server.send(200, "application/json", response);
  } else {
    Serial.println("⚠️ Orange Pi unreachable, using default 1 page");
    Serial.print("   HTTP Code: ");
    Serial.println(httpCode);
    // Fallback to 1 page if Orange Pi is unreachable
    server.send(200, "application/json", "{\"success\":true,\"pages\":1,\"warning\":\"Using default page count\"}");
  }
  
  http.end();
}

// NEW: Proxy upload handlers - Forward file from phone to Orange Pi
String proxyUploadedFile = "";
size_t proxyFileSize = 0;
#define PROXY_BUFFER_SIZE 100000  // 100KB buffer (safe for ESP32)
uint8_t* proxyFileBuffer = nullptr;

void handleFileUploadProxy() {
  HTTPUpload& upload = server.upload();
  
  if (upload.status == UPLOAD_FILE_START) {
    proxyUploadedFile = upload.filename;
    proxyFileSize = 0;
    Serial.println("\n📤 Proxying file: " + proxyUploadedFile);
    
    // Allocate smaller buffer that ESP32 can handle
    if (proxyFileBuffer != nullptr) {
      free(proxyFileBuffer);
      proxyFileBuffer = nullptr;
    }
    
    proxyFileBuffer = (uint8_t*)malloc(PROXY_BUFFER_SIZE);
    
    if (proxyFileBuffer == nullptr) {
      Serial.println("❌ Memory allocation failed!");
      Serial.print("   Free heap: ");
      Serial.println(ESP.getFreeHeap());
    } else {
      Serial.print("✅ Buffer allocated: ");
      Serial.print(PROXY_BUFFER_SIZE / 1024);
      Serial.println(" KB");
    }
    
  } else if (upload.status == UPLOAD_FILE_WRITE) {
    // Accumulate file data
    if (proxyFileBuffer != nullptr && (proxyFileSize + upload.currentSize) < PROXY_BUFFER_SIZE) {
      memcpy(proxyFileBuffer + proxyFileSize, upload.buf, upload.currentSize);
      proxyFileSize += upload.currentSize;
      Serial.print(".");
    } else if (proxyFileBuffer != nullptr) {
      Serial.println("\n⚠️  File too large! Max 100KB");
      Serial.print("   Current size: ");
      Serial.print(proxyFileSize / 1024);
      Serial.println(" KB");
    }
    
  } else if (upload.status == UPLOAD_FILE_END) {
    Serial.println();
    Serial.print("📦 File size: ");
    Serial.print(proxyFileSize);
    Serial.print(" bytes (");
    Serial.print(proxyFileSize / 1024);
    Serial.println(" KB)");
  }
}

void handleUploadProxy() {
  String clientIP = server.client().remoteIP().toString();
  String sessionID = sessionIPs[clientIP];
  
  if (sessionID == "") {
    server.send(400, "application/json", "{\"success\":false,\"error\":\"No session\"}");
    if (proxyFileBuffer != nullptr) {
      free(proxyFileBuffer);
      proxyFileBuffer = nullptr;
    }
    return;
  }
  
  if (proxyFileBuffer == nullptr || proxyFileSize == 0) {
    server.send(400, "application/json", "{\"success\":false,\"error\":\"No file data\"}");
    return;
  }
  
  // Forward to Orange Pi
  Serial.println("📡 Forwarding file to Orange Pi...");
  Serial.print("   Session: ");
  Serial.println(sessionID);
  Serial.print("   File: ");
  Serial.println(proxyUploadedFile);
  
  HTTPClient http;
  http.setTimeout(30000);  // 30 second timeout for file upload
  http.begin(String(FLASK_SERVER) + "/upload");
  
  // Create multipart form data
  String boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW";
  String contentType = "multipart/form-data; boundary=" + boundary;
  http.addHeader("Content-Type", contentType);
  
  // Build multipart body header
  String header = "--" + boundary + "\r\n";
  header += "Content-Disposition: form-data; name=\"session_id\"\r\n\r\n";
  header += sessionID + "\r\n";
  header += "--" + boundary + "\r\n";
  header += "Content-Disposition: form-data; name=\"file\"; filename=\"" + proxyUploadedFile + "\"\r\n";
  header += "Content-Type: application/octet-stream\r\n\r\n";
  
  String footer = "\r\n--" + boundary + "--\r\n";
  
  // Calculate total size
  size_t totalSize = header.length() + proxyFileSize + footer.length();
  
  Serial.print("📊 Building POST body: ");
  Serial.print(totalSize);
  Serial.print(" bytes (");
  Serial.print(totalSize / 1024);
  Serial.println(" KB)");
  Serial.print("   Free heap before: ");
  Serial.println(ESP.getFreeHeap());
  Serial.print("   Largest free block: ");
  Serial.println(ESP.getMaxAllocHeap());
  
  // Check if we can allocate this much memory
  if (totalSize > ESP.getMaxAllocHeap()) {
    Serial.println("❌ File too large for available memory block");
    Serial.print("   Need: ");
    Serial.print(totalSize);
    Serial.print(" bytes, Max block: ");
    Serial.println(ESP.getMaxAllocHeap());
    
    server.send(500, "application/json", "{\"success\":false,\"error\":\"File too large (memory fragmented)\"}");
    free(proxyFileBuffer);
    proxyFileBuffer = nullptr;
    return;
  }
  
  // Allocate buffer for complete POST body
  uint8_t* postBody = (uint8_t*)malloc(totalSize);
  if (postBody == nullptr) {
    Serial.println("❌ Memory allocation failed for POST body");
    Serial.print("   Needed: ");
    Serial.print(totalSize);
    Serial.println(" bytes");
    Serial.print("   Free heap: ");
    Serial.println(ESP.getFreeHeap());
    Serial.print("   Largest block: ");
    Serial.println(ESP.getMaxAllocHeap());
    
    server.send(500, "application/json", "{\"success\":false,\"error\":\"File too large for ESP32 memory\"}");
    free(proxyFileBuffer);
    proxyFileBuffer = nullptr;
    return;
  }
  
  // Assemble complete POST body
  size_t offset = 0;
  memcpy(postBody + offset, header.c_str(), header.length());
  offset += header.length();
  memcpy(postBody + offset, proxyFileBuffer, proxyFileSize);
  offset += proxyFileSize;
  memcpy(postBody + offset, footer.c_str(), footer.length());
  
  // Send POST request
  Serial.print("📤 Sending ");
  Serial.print(totalSize);
  Serial.println(" bytes to Orange Pi...");
  
  int httpCode = http.POST(postBody, totalSize);
  
  // Cleanup
  free(postBody);
  free(proxyFileBuffer);
  proxyFileBuffer = nullptr;
  
  Serial.print("   HTTP Code: ");
  Serial.println(httpCode);
  
  // Handle response
  if (httpCode == 200) {
    String response = http.getString();
    Serial.println("✅ Orange Pi response: " + response);
    
    // Parse response to get page count
    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, response);
    
    if (!error && doc["success"] == true) {
      int pages = doc["pages"] | 1;
      int cost = pages;  // ₱1 per page
      int fileId = doc["file_id"] | 0;  // Get file_id from Orange Pi
      
      // Store file_id for this session (for printing later)
      if (fileId > 0) {
        userFileIDs[sessionID] = fileId;
      }
      
      // Send success response with page count
      String successResponse = "{\"success\":true,\"pages\":" + String(pages) + 
                              ",\"cost\":" + String(cost) + 
                              ",\"file_id\":" + String(fileId) +
                              ",\"filename\":\"" + proxyUploadedFile + "\"}";
      server.send(200, "application/json", successResponse);
      
      Serial.println("✅ Upload complete!");
      Serial.print("   File ID: ");
      Serial.println(fileId);
      Serial.print("   Pages: ");
      Serial.println(pages);
      Serial.print("   Cost: ₱");
      Serial.println(cost);
    } else {
      server.send(200, "application/json", response);
    }
  } else {
    Serial.print("❌ Orange Pi error! HTTP code: ");
    Serial.println(httpCode);
    String errorMsg = http.getString();
    Serial.println("   Error: " + errorMsg);
    
    // Send error response
    String errorResponse = "{\"success\":false,\"error\":\"Orange Pi connection failed\",\"http_code\":" + 
                          String(httpCode) + "}";
    server.send(500, "application/json", errorResponse);
  }
  
  http.end();
}

void handleStatus() {
  // Get client IP address
  String clientIP = server.client().remoteIP().toString();
  
  // Get or create session ID for this IP
  String sessionID = sessionIPs[clientIP];
  if (sessionID == "") {
    sessionID = generateSessionID();
    sessionIPs[clientIP] = sessionID;
    
    Serial.println("📱 New user connected:");
    Serial.print("   IP: ");
    Serial.println(clientIP);
    Serial.print("   Session: ");
    Serial.println(sessionID);
  }
  
  // Get credits for this session
  int credits = userCredits[sessionID];
  
  String json = "{\"credits\":" + String(credits) + 
                ",\"pending\":" + String(pendingCredits) +
                ",\"session\":\"" + sessionID + "\"}";
  server.send(200, "application/json", json);
}

void handleClaimCredits() {
  String clientIP = server.client().remoteIP().toString();
  String sessionID = sessionIPs[clientIP];
  
  // Check if session exists and there are pending credits
  if (sessionID == "" || pendingCredits == 0) {
    server.send(400, "application/json", 
                "{\"success\":false,\"message\":\"No credits to claim\"}");
    return;
  }
  
  // Transfer pending credits to this user's session
  int claimed = pendingCredits;
  userCredits[sessionID] += claimed;
  pendingCredits = 0;
  
  Serial.println("\n╔═════════════════════════════════╗");
  Serial.println("║ ✅ CREDITS CLAIMED              ║");
  Serial.print("║ Session: ");
  Serial.print(sessionID);
  Serial.println("         ║");
  Serial.print("║ Amount: ₱");
  Serial.print(claimed);
  Serial.println("                      ║");
  Serial.print("║ Total Credits: ₱");
  Serial.print(userCredits[sessionID]);
  Serial.println("              ║");
  Serial.println("╚═════════════════════════════════╝\n");
  
  // Send credits to Orange Pi server
  sendCreditsToServer(sessionID, claimed);
  
  // Success beep
  playBuzzer(1);
  
  server.send(200, "application/json", 
              "{\"success\":true,\"claimed\":" + String(claimed) + "}");
}

void handlePrint() {
  String clientIP = server.client().remoteIP().toString();
  String sessionID = sessionIPs[clientIP];
  
  if (sessionID == "") {
    server.send(400, "application/json", "{\"success\":false,\"message\":\"No session found\"}");
    return;
  }
  
  // Check if user has uploaded a file
  int fileId = userFileIDs[sessionID];
  if (fileId == 0) {
    server.send(400, "application/json", "{\"success\":false,\"message\":\"No file uploaded\"}");
    return;
  }
  
  Serial.println("\n📡 Sending print request to Orange Pi...");
  Serial.print("   Session: ");
  Serial.println(sessionID);
  Serial.print("   File ID: ");
  Serial.println(fileId);
  Serial.print("   Credits: ₱");
  Serial.println(userCredits[sessionID]);
  
  HTTPClient http;
  http.setTimeout(10000);
  http.begin(String(FLASK_SERVER) + "/print");
  http.addHeader("Content-Type", "application/json");
  
  StaticJsonDocument<300> doc;
  doc["session_id"] = sessionID;
  doc["file_id"] = fileId;  // Send file_id instead of filename
  doc["credits"] = userCredits[sessionID];
  
  String requestBody;
  serializeJson(doc, requestBody);
  
  int httpCode = http.POST(requestBody);
  
  Serial.print("   HTTP Response Code: ");
  Serial.println(httpCode);
  
  if (httpCode > 0) {
    String response = http.getString();
    Serial.print("   Response: ");
    Serial.println(response);
    
    StaticJsonDocument<200> responseDoc;
    deserializeJson(responseDoc, response);
    
    if (responseDoc["success"]) {
      int pagesDeducted = responseDoc["pages"];
      userCredits[sessionID] -= pagesDeducted;
      
      Serial.println("\n🖨️  PRINTING...");
      Serial.print("   Pages: ");
      Serial.println(pagesDeducted);
      Serial.print("   Remaining: ₱");
      Serial.println(userCredits[sessionID]);
      
      if (buzzerState == BUZZER_IDLE) {
        for (int i = 0; i < 3; i++) {
          digitalWrite(BUZZER_PIN, HIGH);
          delay(100);
          digitalWrite(BUZZER_PIN, LOW);
          delay(100);
        }
      }
      
      server.send(200, "application/json", "{\"success\":true,\"message\":\"Printing...\"}");
    } else {
      String errorMsg = String(responseDoc["message"].as<const char*>());
      Serial.print("❌ Print failed: ");
      Serial.println(errorMsg);
      server.send(200, "application/json", "{\"success\":false,\"message\":\"" + errorMsg + "\"}");
      
      if (buzzerState == BUZZER_IDLE) {
        digitalWrite(BUZZER_PIN, HIGH);
        delay(500);
        digitalWrite(BUZZER_PIN, LOW);
      }
    }
  } else {
    Serial.println("❌ Connection error - Cannot reach Orange Pi");
    Serial.println("   Check: ");
    Serial.println("   1. Is Orange Pi running? (python3 app.py)");
    Serial.println("   2. Is Orange Pi at 192.168.22.2?");
    Serial.println("   3. Is ESP32 connected to router?");
    
    server.send(500, "application/json", "{\"success\":false,\"message\":\"Connection error - Check Orange Pi\"}");
    
    if (buzzerState == BUZZER_IDLE) {
      digitalWrite(BUZZER_PIN, HIGH);
      delay(500);
      digitalWrite(BUZZER_PIN, LOW);
    }
  }
  
  http.end();
}

String generateSessionID() {
  randomSeed(analogRead(0) + micros());
  return "USER_" + String(random(100000, 999999));
}

void sendCreditsToServer(String sessionID, int amount) {
  HTTPClient http;
  http.setTimeout(5000);
  http.begin(String(FLASK_SERVER) + "/api/credits");
  http.addHeader("Content-Type", "application/json");
  
  StaticJsonDocument<200> doc;
  doc["session_id"] = sessionID;
  doc["amount"] = amount;
  
  String requestBody;
  serializeJson(doc, requestBody);
  
  int httpCode = http.POST(requestBody);
  
  Serial.print("📡 Sync to server: ");
  Serial.print(httpCode == 200 ? "OK" : "FAILED");
  Serial.print(" (Session: ");
  Serial.print(sessionID);
  Serial.println(")");
  
  http.end();
}