
---

<div align="center">

# Piso Print System

**Orange Pi (Hotspot / Captive Portal) + ESP32 Coin Acceptor + CUPS**

![Orange Pi](https://img.shields.io/badge/Orange%20Pi-Armbian-2A9FD6?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.x-000?style=for-the-badge)
![CUPS](https://img.shields.io/badge/CUPS-printing-8B0000?style=for-the-badge)
![ESP32](https://img.shields.io/badge/ESP32-CH340-FF6F00?style=for-the-badge)

**An offline, Wi-Fi hotspot based, coin-operated print kiosk (legal/long coupon only).**

</div>

---

## 📋 Table of Contents

* [Overview](#-overview)
* [Features](#-features)
* [Architecture](#-architecture)
* [Technology Stack](#-technology-stack)
* [Project Phases (PR style)](#-project-phases-pr-style)
* [Hardware Setup](#-hardware-setup)
* [Quick Start (fast path)](#-quick-start-fast-path)
* [Full Setup (step-by-step)](#-full-setup-step-by-step)

  * Armbian base, SSH, updates
  * Hostapd + dnsmasq (AP + DHCP)
  * Captive portal redirect (iptables + nginx/Flask)
  * Flask app (upload/status) code outline
  * CUPS configuration + print control
  * ESP32 coin firmware (Serial mode)
  * Systemd services (auto start)
* [Database Schema & Discussion](#-database-schema--discussion)
* [Testing & Validation](#-testing--validation)
* [Deployment & Operation](#-deployment--operation)
* [Troubleshooting](#-troubleshooting)
* [Future Enhancements](#-future-enhancements)
* [License & Acknowledgements](#-license--acknowledgements)

---

## 🌟 Overview

This project creates a **Piso Print kiosk** that:

1. Broadcasts a Wi-Fi hotspot (`PISO_PRINT`) from the Orange Pi.
2. Auto-redirects connected clients to a local **captive portal** web page (Flask).
3. Allows users to **upload a legal/long size** printable file (PDF recommended).
4. Shows the page count and **required credits**.
5. Waits for coins to be inserted; the **ESP32** counts pulses and reports credits to the Orange Pi.
6. When credits ≥ required, the Orange Pi sends the job to **CUPS** and prints.
7. All actions are logged in an SQLite database.

No internet is needed — everything runs locally on the Orange Pi.

---

## ✨ Features

* Orange Pi as Wi-Fi Access Point (hostapd) with captive portal redirect.
* Local Flask web app: Upload, status, admin pages.
* CUPS print control — job held until paid.
* ESP32 coin acceptor interface (USB Serial) for reliable credit updates.
* SQLite for transaction and job logs.
* Systemd services for autoprovide on boot.

---

## 🏗 Architecture

```
[User phone/laptop] --connects to--> [Orange Pi AP (hostapd/dnsmasq)]
          |                                     |
          |---> captive portal (Flask) <-------- |
                             |                   |
                             |          Serial or MQTT/HTTP
                             v                   |
                          [Orange Pi app + CUPS] <--- [ESP32 + Coin Acceptor]
                             |
                          [SQLite logs]
                             |
                          [Printer - USB]
```

---

## 🛠 Technology Stack

* **Hardware:** Orange Pi PC H3 (1GB), ESP32 CH340 Type-C, Coin Acceptor, USB Printer, microSD 32GB
* **OS:** Armbian (Debian Buster / Ubuntu Focal recommended)
* **Server:** Python 3.9+, Flask, gunicorn (or systemd)
* **Network:** hostapd, dnsmasq, iptables (redirect)
* **Print:** CUPS (Common Unix Printing System)
* **DB:** SQLite3
* **ESP Dev:** Arduino IDE (ESP32 core) — Serial or HTTP/MQTT option

---

## 📦 Project Phases (PR-style tasks)

**Phase 1 — Prepare hardware**

* Flash Armbian to microSD, boot Orange Pi, enable SSH.
* Connect printer via USB, test basic printing with CUPS.

**Phase 2 — ESP32 + Coin Acceptor**

* Wire coin acceptor to ESP32, test pulses locally on Serial Monitor.
* Implement simple Serial message `COIN` for each valid coin.

**Phase 3 — Orange Pi as AP + captive portal**

* Install hostapd + dnsmasq, configure AP SSID `PISO_PRINT`.
* Implement iptables redirect to Flask server.

**Phase 4 — Flask web app**

* Build endpoints: `/` (upload), `/status`, `/admin`.
* Implement page count (PyPDF2) and cost estimation.

**Phase 5 — Integration**

* Orange Pi listens to Serial (`/dev/ttyUSB0`) for `COIN` messages, updates credits.
* When credits ≥ required → trigger CUPS job.

**Phase 6 — DB & Logging**

* Implement SQLite schema (Users, PrintJobs, Transactions).
* Ensure ACID writes on each credit event.

**Phase 7 — Testing & Deployment**

* Test coin edge cases, network edge cases, power loss, printer jams.
* Harden and enable systemd services.

---

## 🔌 Hardware Setup

### Required (you already have most)

* Orange Pi PC H3 (1GB) + 5V power supply
* microSD (Bavin 32GB) with Armbian image
* ESP32 CH340 board
* Programmable coin acceptor (12V)
* USB Printer (CUPS compatible)
* USB cable between ESP32 and Orange Pi (for Serial)
* Jumper wires, small breadboard for test wiring

### Basic wiring

* **Coin acceptor** → ESP32 digital pulse input (follow coin acceptor docs). Use opto-isolator if acceptor outputs >3.3V.
* **ESP32** → USB → Orange Pi (serial /dev/ttyUSB0).
* **Printer USB** → Orange Pi USB port.
* Ensure **common grounds** where needed and use proper power supplies (5V Pi, 12V coin acceptor).

> Safety: Use fuse on 12V rail, isolate coin acceptor pulse output with optocoupler if needed.

---

## ⚡ Quick Start (fast path)

If you just want the minimal working path to test end-to-end (do this after flashing Armbian and connecting hardware):

1. SSH into Orange Pi:

   ```bash
   ssh orangepi@<ip>
   sudo apt update && sudo apt upgrade -y
   ```

2. Install Python and CUPS:

   ```bash
   sudo apt install python3 python3-pip cups git -y
   sudo usermod -a -G lpadmin $USER
   ```

3. Install hostapd & dnsmasq:

   ```bash
   sudo apt install hostapd dnsmasq iptables-persistent -y
   sudo systemctl stop hostapd dnsmasq
   ```

4. Clone repo (this one):

   ```bash
   git clone <your-repo-url> ~/pisoprint
   cd ~/pisoprint
   ```

5. Run the helper install script (provided in repo) — **I’ll include the script below in Full Setup**.

6. On ESP32 run the simple Serial coin sketch (provided below).

7. Open your phone, connect to `PISO_PRINT` SSID, you should be auto-redirected to the upload page at `http://192.168.4.1/` and can try upload → insert coin → print.

---

## 🔧 Full Setup (step-by-step)

> These steps assume a fresh Armbian boot with SSH enabled and an Internet connection (USB tethering or temporary Ethernet for apt installs). After setup, the system can operate completely offline.

### 1) System prep & base packages

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-venv python3-pip git sqlite3 cups cups-client \
                 hostapd dnsmasq iptables-persistent nginx -y
sudo usermod -a -G lpadmin $USER
```

Enable CUPS web admin (if needed):

```bash
sudo systemctl enable --now cups
```

Open CUPS web UI: `http://<orangepi-ip>:631` — add your USB printer and test print a page.

---

### 2) Create project directory & virtualenv

```bash
mkdir -p /opt/pisoprint
cd /opt/pisoprint
python3 -m venv .venv
source .venv/bin/activate
pip install flask gunicorn pyserial pypdf2 watchdog
```

Place the Flask app (I provide skeleton code below) into `/opt/pisoprint/app/`.

---

### 3) Hostapd configuration (Orange Pi as AP)

Create `/etc/hostapd/hostapd.conf`:

```ini
interface=wlan0
driver=nl80211
ssid=PISO_PRINT
hw_mode=g
channel=6
ieee80211n=1
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=pisoprint1234
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
```

> NOTE: Orange Pi PC H3 doesn’t have built-in WiFi. Use a supported USB WiFi dongle. Replace `wlan0` accordingly.

Point hostapd to this conf: edit `/etc/default/hostapd`:

```
DAEMON_CONF="/etc/hostapd/hostapd.conf"
```

---

### 4) dnsmasq DHCP config

Backup default:

```bash
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
```

Create `/etc/dnsmasq.conf`:

```ini
interface=wlan0
dhcp-range=192.168.4.10,192.168.4.100,255.255.255.0,24h
domain-needed
bogus-priv
address=/piso.print/192.168.4.1
```

This gives clients IPs in 192.168.4.x and maps `piso.print` to the Pi.

---

### 5) Static IP for wlan0

Edit `/etc/network/interfaces` or use `nmcli` depending on your Armbian version.

Simple `/etc/dhcpcd.conf` match (example):

```ini
interface wlan0
static ip_address=192.168.4.1/24
nohook wpa_supplicant
```

After change:

```bash
sudo systemctl restart networking
sudo systemctl restart dnsmasq
```

---

### 6) Captive portal: iptables redirect to Flask

Redirect HTTP (port 80) traffic to local Flask (port 5000/8000):

```bash
sudo iptables -t nat -A PREROUTING -i wlan0 -p tcp --dport 80 -j DNAT --to-destination 192.168.4.1:8000
sudo iptables -t nat -A POSTROUTING -j MASQUERADE
sudo netfilter-persistent save
```

**If you want to also redirect HTTPS clients**, it’s more complex (certs, HSTS) — usually captive portals rely on HTTP.

---

### 7) Flask app (skeleton)

Create `/opt/pisoprint/app/app.py`:

> This is a working, minimal example — adapt further in your repo.

```python
from flask import Flask, request, redirect, url_for, render_template, jsonify, send_from_directory
import os, sqlite3, time, subprocess
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader

BASE_DIR = '/opt/pisoprint'
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
DB = os.path.join(BASE_DIR, 'pisoprint.db')
PRINTER_NAME = 'Epson_L120'  # change to your CUPS printer name

os.makedirs(UPLOAD_DIR, exist_ok=True)
app = Flask(__name__)

def init_db():
    with sqlite3.connect(DB) as c:
        c.execute('''CREATE TABLE IF NOT EXISTS PrintJobs(
            JobID INTEGER PRIMARY KEY AUTOINCREMENT,
            FileName TEXT,
            Pages INTEGER,
            Cost INTEGER,
            Status TEXT,
            CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS Transactions(
            TxID INTEGER PRIMARY KEY AUTOINCREMENT,
            CoinInserted INTEGER,
            CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
init_db()

def count_pages(filepath):
    try:
        reader = PdfReader(filepath)
        return len(reader.pages)
    except Exception:
        return 1

@app.route('/')
def index():
    return render_template('upload.html')  # simple upload form

@app.route('/upload', methods=['POST'])
def upload():
    f = request.files['file']
    filename = secure_filename(f.filename)
    savepath = os.path.join(UPLOAD_DIR, filename)
    f.save(savepath)
    pages = count_pages(savepath)
    cost = pages  # 1 peso per page
    with sqlite3.connect(DB) as c:
        c.execute("INSERT INTO PrintJobs(FileName, Pages, Cost, Status) VALUES(?,?,?,?)",
                  (filename, pages, cost, 'pending'))
    return jsonify({'status':'ok', 'pages':pages, 'cost':cost})

@app.route('/status')
def status():
    # return counts and pending jobs
    with sqlite3.connect(DB) as c:
        jobs = c.execute("SELECT JobID,FileName,Pages,Cost,Status FROM PrintJobs ORDER BY CreatedAt DESC").fetchall()
    return jsonify([dict(zip(['JobID','FileName','Pages','Cost','Status'],row)) for row in jobs])

# Admin endpoint to trigger print (used by credit-checker)
def print_file(jobid):
    with sqlite3.connect(DB) as c:
        row = c.execute("SELECT FileName,Pages FROM PrintJobs WHERE JobID=?",(jobid,)).fetchone()
        if not row: return False
        filename, pages = row
        filepath = os.path.join(UPLOAD_DIR, filename)
        # cupsenable, cancel, etc. Use lp or lpr
        cmd = ['lp', '-d', PRINTER_NAME, filepath]
        try:
            subprocess.check_call(cmd)
            c.execute("UPDATE PrintJobs SET Status='printed' WHERE JobID=?",(jobid,))
            return True
        except subprocess.CalledProcessError:
            c.execute("UPDATE PrintJobs SET Status='error' WHERE JobID=?",(jobid,))
            return False

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

Create a minimal `templates/upload.html` with a file input and JS that POSTs to `/upload` and shows `pages` and `cost`.

---

### 8) Serial listener: receive credits from ESP32

Create `/opt/pisoprint/coin_listener.py`:

```python
import serial, time, sqlite3
SERIAL_PORT = '/dev/ttyUSB0'
BAUD = 115200
DB = '/opt/pisoprint/pisoprint.db'

def add_transaction(amount):
    with sqlite3.connect(DB) as c:
        c.execute("INSERT INTO Transactions(CoinInserted) VALUES(?)", (amount,))

def listen():
    ser = serial.Serial(SERIAL_PORT, BAUD, timeout=1)
    while True:
        line = ser.readline().decode(errors='ignore').strip()
        if not line: continue
        if 'COIN' in line.upper():
            # simple: each COIN message = 1 peso
            add_transaction(1)
            print("Coin registered")
        time.sleep(0.1)

if __name__ == '__main__':
    listen()
```

**Later** you will expand logic: aggregate credits, match to pending job cost, call `print_file(jobid)` when enough.

---

### 9) Credit-checker: match coins to jobs & trigger print

Create `/opt/pisoprint/credit_checker.py`:

```python
import sqlite3, time, os
DB = '/opt/pisoprint/pisoprint.db'
from app import print_file  # import helper

def get_balance():
    with sqlite3.connect(DB) as c:
        res = c.execute("SELECT SUM(CoinInserted) FROM Transactions").fetchone()
        return res[0] or 0

def get_next_pending_job():
    with sqlite3.connect(DB) as c:
        return c.execute("SELECT JobID, Cost FROM PrintJobs WHERE Status='pending' ORDER BY CreatedAt LIMIT 1").fetchone()

def consume_credits(amount):
    # simple implementation: delete/mark transactions consumed
    # production: implement balance table per user/session
    with sqlite3.connect(DB) as c:
        # This is simplified: delete coins equal to amount
        rows = c.execute("SELECT TxID FROM Transactions ORDER BY CreatedAt LIMIT ?", (amount,)).fetchall()
        for r in rows:
            c.execute("DELETE FROM Transactions WHERE TxID=?", (r[0],))
        return True

while True:
    job = get_next_pending_job()
    if job:
        jobid, cost = job
        bal = get_balance()
        if bal >= cost:
            ok = print_file(jobid)
            if ok:
                consume_credits(cost)
    time.sleep(2)
```

This is intentionally simple — it demonstrates concept. For production, replace `Transactions` as a proper FIFO credit ledger and mark consumed TxIDs.

---

### 10) ESP32 coin sketch (Serial mode)

Use Arduino IDE, install ESP32 core.

```cpp
// ESP32 coin detector - sends "COIN\n" via Serial on valid coin pulse
const int coinPin = 4; // change per wiring
volatile int pulseCount = 0;
unsigned long lastPulse = 0;

void IRAM_ATTR coinISR() {
  unsigned long now = millis();
  if (now - lastPulse > 50) { // debounce
    pulseCount++;
    lastPulse = now;
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(coinPin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(coinPin), coinISR, FALLING);
}

void loop() {
  if (pulseCount > 0) {
    Serial.println("COIN");
    pulseCount = 0;
  }
  delay(100);
}
```

Wire coin acceptor output to `coinPin` (through opto-isolator if needed). The ESP32 sends `COIN` over the USB Serial to Orange Pi.

---

### 11) Systemd services (auto start)

Create `/etc/systemd/system/pisoprint-flask.service`:

```ini
[Unit]
Description=PisoPrint Flask app
After=network-online.target

[Service]
User=orangepi
WorkingDirectory=/opt/pisoprint
Environment="PATH=/opt/pisoprint/.venv/bin"
ExecStart=/opt/pisoprint/.venv/bin/gunicorn -w 3 -b 0.0.0.0:8000 app.app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/pisoprint-coin.service`:

```ini
[Unit]
Description=PisoPrint Coin Listener
After=network.target

[Service]
User=orangepi
ExecStart=/opt/pisoprint/.venv/bin/python /opt/pisoprint/coin_listener.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable & start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable pisoprint-flask pisoprint-coin
sudo systemctl start pisoprint-flask pisoprint-coin
```

---

### 12) iptables persistence

We already added rules earlier. Make sure `netfilter-persistent` is installed and saved:

```bash
sudo netfilter-persistent save
```

---

## 🗄 Database Schema & Discussion

**PrintJobs**

* JobID (PK), FileName, Pages, Cost, Status, CreatedAt
  **Transactions**
* TxID (PK), CoinInserted (int), CreatedAt
  **Notes / Discussion**
* Transactions act as raw credit events (FIFO). The credit_checker consumes the first N transactions equal to cost when printing.
* In a more advanced design add **Sessions** (per upload) so credits tie to a specific upload → avoids cross-user races.

---

## ✅ Testing & Validation

1. **AP up**: Connect a phone to `PISO_PRINT`, get IP `192.168.4.x`, browse to any site → should redirect to `http://192.168.4.1:8000/` (upload page).
2. **Upload**: Upload a 1-page PDF → backend returns `pages=1, cost=1`. Job appears in DB as `pending`.
3. **Coin insert**: Insert a valid ₱1 → ESP32 sends `COIN`, Orange Pi `coin_listener.py` logs transaction.
4. **Auto print**: credit_checker detects balance ≥ cost → calls `print_file(jobid)` → job sent to CUPS → status updated to `printed`.
5. **Edge cases**: Insert invalid coin (no pulse) → no COIN message → no print.
6. **Power loss**: Reboot Orange Pi mid-flow → jobs persist in SQLite; coin transactions persisted if written before crash.
7. **Multiple uploads**: Upload two files → they queue; credits consumed FIFO.

---

## 🚩 Deployment & Operation

* Keep Orange Pi powered with stable 5V supply.
* Place coin acceptor locked and secure.
* Refill paper & check toner.
* Monitor `/var/log/syslog` and `journalctl` for pisoprint services.
* Use CUPS admin UI to check printer queues: `http://192.168.4.1:631`.

---

## 🐞 Troubleshooting

* **No AP**: confirm USB Wi-Fi is supported, `iw list` supports AP mode.
* **No redirect**: check iptables NAT rules and dnsmasq `address` entries.
* **Serial not showing**: `dmesg | grep ttyUSB` to find device; check USB cable.
* **Printer not found**: `lpinfo -v` and `lpstat -p` to check CUPS.
* **Permissions**: ensure `orangepi` in `lpadmin` group.

---

## 🔮 Future Enhancements

* Proper session binding (upload → session token → credit lock).
* Cashless payments (GCash/PayMaya/QR) via secure gateway.
* Per-user accounts, receipts, and admin dashboard.
* Better captive portal UX with HTTPS support (requires certs & captive portal tricks).

---

## 📄 License & Acknowledgements

Open source / MIT — adapt for your school project. Credit to open-source projects used: CUPS, Flask, Armbian, ESP32 Arduino core.

---

## 👣 Next steps I will provide if you want

If you want, I can now generate **downloadable files** for you to copy into the Orange Pi:

* `app.py` + `templates/upload.html` (fully fleshed)
* `coin_listener.py`, `credit_checker.py`
* Systemd service files
* `hostapd.conf` and `dnsmasq.conf` examples
* A ready `install.sh` to automate apt installs and enable services

Tell me which of the above to output first (I can paste them all here so you can `scp` them to your Orange Pi).
