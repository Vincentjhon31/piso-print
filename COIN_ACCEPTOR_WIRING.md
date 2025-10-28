# Coin Acceptor Wiring Guide

## ⚠️ IMPORTANT: Use the COUNTER Wire!

### Coin Acceptor Wire Colors:
- **Red** = +12V (Power)
- **Black** = GND (Ground)
- **White** = COIN (Indicator LED signal - NOT for counting!)
- **Gray** = COUNTER (Pulse signal for counting) ← **USE THIS ONE!**

---

## Correct Wiring to ESP32:

```
Coin Acceptor          →    ESP32
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Red (12V)              →    12V Power Supply +
Black (GND)            →    12V Power Supply - AND ESP32 GND
Gray (COUNTER)         →    Pin 32 (GPIO 32)
White (COIN)           →    Not Connected (optional: connect LED for debugging)
```

### Power Supply Connections:
```
12V Power Supply       →    Devices
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
+ (Positive)           →    Coin Acceptor Red
- (Negative/GND)       →    Coin Acceptor Black + ESP32 GND (common ground!)
```

**CRITICAL: ESP32 GND and Coin Acceptor GND must be connected together!**

---

## Why COUNTER (Gray) Instead of COIN (White)?

| Wire | Purpose | Why Not Use for Counting? |
|------|---------|---------------------------|
| **White (COIN)** | Indicator signal, stays HIGH when coin detected | Too slow, not precise, meant for LED |
| **Gray (COUNTER)** | Precise pulse counting, 1 pulse per denomination unit | Designed for microcontrollers, fast and accurate |

**The White wire is like a "coin detected" LED signal - it's too slow and imprecise for counting pulses!**

---

## Ghost Pulse Problem (Detecting coins when none inserted)

### Causes:
1. ❌ **Wrong wire used** (White instead of Gray)
2. ⚡ **Electrical noise** from power supply
3. 🔌 **No common ground** between ESP32 and coin acceptor
4. 📡 **Interference** from WiFi, other devices
5. 🔧 **Loose connections**

### Solutions Applied in Code:
- ✅ **2-second startup delay** - Ignores pulses during power-on noise
- ✅ **50ms debounce** - Filters electrical noise
- ✅ **500ms timeout** - Better coin detection window

### Hardware Solutions:

#### 1. Add External Pull-Down Resistor (Recommended)
```
ESP32 Pin 32  ──────┬────── Coin Acceptor COUNTER (Gray)
                    │
                   ┴ 10kΩ Resistor
                    │
                   GND
```

This helps filter noise by ensuring Pin 32 stays at 0V when no pulse.

#### 2. Add Capacitor Filter (Advanced)
```
Coin Acceptor COUNTER ──┬──── ESP32 Pin 32
                        │
                       ═══ 0.1µF Capacitor
                        │
                       GND
```

Smooths out electrical noise spikes.

#### 3. Shielded Cable (Best for long wires)
- Use twisted pair or shielded cable between coin acceptor and ESP32
- Keep wires as short as possible
- Avoid running near power cables

---

## Testing Steps:

### Step 1: Upload Fixed Code
1. Upload the updated ESP32 code
2. Open Serial Monitor (115200 baud)
3. Wait for: `✅ System Ready!`
4. Wait 2 more seconds for noise filter

### Step 2: Test WITHOUT Coins
1. Don't insert any coins
2. Wait 30 seconds
3. **Should NOT see any pulse messages**
4. If you still see ghost pulses → Check wiring!

### Step 3: Test WITH Coins
1. Insert ₱1 coin
   - Should see: `💰 COIN ACCEPTED: ₱1` with `📊 Pulses: 1`
2. Insert ₱5 coin
   - Should see: `💰 COIN ACCEPTED: ₱5` with `📊 Pulses: 5`
3. Insert ₱10 coin
   - Should see: `💰 COIN ACCEPTED: ₱10` with `📊 Pulses: 10`

### Step 4: If Still Getting Wrong Pulse Counts

#### If pulses are consistently wrong (e.g., ₱5 = 4 pulses instead of 5):
Adjust tolerance in code:
```cpp
// In checkCoinType() function:
else if (detectedPulses >= 4 && detectedPulses <= 6) {  // ₱5 coin
    coinValue = 5;
```

#### If pulses are random (3, 7, 14, 16, etc.):
1. **Check COUNTER wire is connected** (not COIN wire!)
2. **Add pull-down resistor** (10kΩ from Pin 32 to GND)
3. **Check common ground** between ESP32 and coin acceptor
4. **Use shorter wires** (< 30cm if possible)
5. **Move coin acceptor away** from power supply and other electronics

---

## Coin Acceptor Modes (If Available)

Some coin acceptors have DIP switches or jumpers. If yours has settings:

### Mode Settings:
- **NO (Normally Open)** ← Use this! (Default for most)
- **NC (Normally Closed)** - Less common

### Speed Settings:
- **FAST** - For arcade machines (may cause false counts)
- **MEDIUM** ← Recommended for ESP32
- **SLOW** - Very conservative (may miss fast coins)

**Check your coin acceptor manual or look for tiny switches on the side/bottom of the unit.**

---

## Common Issues & Fixes:

### Issue: Pulses detected at startup
**Fix:** Code now ignores first 2 seconds ✅

### Issue: Random pulse counts (not 1, 5, or 10)
**Fix:** 
1. Switch to COUNTER (Gray) wire ✅
2. Add 10kΩ pull-down resistor
3. Check common ground connection

### Issue: ₱5 coin detected as ₱10 (double counting)
**Fix:** Increase debounce time in code (try 100ms)

### Issue: Coins not detected at all
**Fix:**
1. Check COUNTER wire is connected to Pin 32
2. Check coin acceptor is powered (12V)
3. Check common ground
4. Try manually bridging Gray wire to GND briefly (should see pulses)

---

## Verification Test:

Run this test to verify wiring:

1. **Power Test:**
   - Coin acceptor LED should light up when powered
   - ESP32 should boot normally

2. **Ground Test:**
   - Use multimeter: ESP32 GND to Coin Acceptor Black = 0Ω (continuity)

3. **Signal Test:**
   - Serial Monitor open
   - Insert ₱1 coin slowly
   - Should see pulses: 1
   - Insert ₱5 coin
   - Should see pulses: 5

4. **Noise Test:**
   - Don't touch anything
   - Wait 1 minute
   - Should NOT see any pulse messages

---

## Still Having Problems?

Share in Serial Monitor:
1. What pulses you're seeing (with no coins)
2. What pulses for ₱1, ₱5, ₱10 coins
3. Your wiring photo (if possible)

Example good output:
```
✅ System Ready!
⏳ Waiting 2 seconds for coin acceptor to stabilize...

(2 seconds later, insert ₱5)

💰 COIN ACCEPTED: ₱5
📊 Pulses: 5
💵 Pending Credits: ₱5
```
