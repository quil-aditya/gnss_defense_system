# 🛰️ GNSS Spoofing & Jamming Defense System

A lightweight, real-time GPS spoofing and jamming defense pipeline for drones and embedded systems.  
This multi-layered system **filters malicious satellite signals** using a combination of:
- hardcoded RF thresholds,
- AI classification (via TFLite),
- motion-based coherence checking, and
- physical antenna shielding.

Designed for deployment on **Raspberry Pi 5** with a **u-blox M9N** GNSS receiver.

## 🎯 Core Logic & Flow

The system runs every **100ms** and follows a four-stage decision pipeline:

### ✅ Layer 1: Clean Bypass  
- Signals with:
  - `hdop ≤ 1.5`
  - `vdop ≤ 2.0`
  - `sats_used ≥ 9`
  - `jamInd < 8`
  - `noise_per_ms < 2.8`
- Are **directly forwarded to FC** (i.e., clearly valid overhead fixes)

### ❌ Layer 2: Hard RF Rejection  
- Signals with:
  - `jamInd ≥ 10` or
  - `noise_per_ms ≥ 3.0`
- Are **instantly rejected** (strongly spoofed/jammed)

### 🟡 Layer 3: Medium RF Risk → Coherence + AI  
- If:
  - `jamInd ∈ [8,10)` or
  - `noise ∈ [2.8,3.0)`
- Check **motion coherence**
  - If incoherent → reject
  - If coherent → run **AI model**
    - If spoofed → reject
    - If clean → forward

### 🔵 Layer 4: Low RF Risk → AI + Coherence  
- If RF seems fine but bypass conditions aren’t met:
  - Run **AI model**
    - If spoofed → reject
    - If clean → check **coherence**
      - If incoherent → reject
      - Else → forward to FC

---

## 🧠 AI Model Info

- Framework: **TensorFlow Lite**
- Inputs: `[hdop, vdop, sats_used]`
- Output: `0 = Clean`, `1 = Spoofed`
- Trained on: real + synthetic spoofing datasets
- Preprocessing: **StandardScaler** (`scaler.pkl`) saved from training pipeline

---

## 🔁 Coherence Checker

Checks for realistic satellite motion:
- Spatial consistency (lat/lon distance per second)
- Temporal progression
- DOP stability
- Satellite count stability

This helps block:
- **Replay attacks**
- **Sudden jumps in GNSS fix**
- **High-speed ghost locations**

---

## 🛜 Data Flow Summary

[GNSS Antenna + M9N]
↓
[m9n_reader.py] ➝ [feature_extractor.py]
↓
Hardcoded RF Filter ➝ AI Zone (if needed) ➝ Coherence Check
↓
✔️ Forward Fix to FC ❌ Drop Fix


---

## 📡 Hardware Stack

- 🧠 **Raspberry Pi 5 (8GB)**
- 📶 **u-blox M9N GNSS Module**
- 🛰️ **Helical GNSS antenna** (placed open to sky)
- 🛡️ **Custom aluminum shielding box**
  - Blocks lateral spoofed signals
  - Allows clean overhead signals

---

## 🧪 Offline Testing

Use the test runner to evaluate the pipeline on CSV logs:

```bash
python test/offline_runner.py
Logs will be printed + saved to gnss_log.txt.

📝 Output Logging
Every fix decision is logged via utils/logger.py, e.g.:

ACCEPT: Clean bypass
REJECT: RF Hard threshold
REJECT: AI + Incoherent (Low RF)
ACCEPT: AI + Coherent (Medium RF)
🛠 Setup Instructions

1. 📦 Dependencies
Install required packages:
pip install numpy joblib pyserial tensorflow

2. 🔌 Connect Hardware
Connect M9N GNSS via USB-C to Raspberry Pi
Confirm port as /dev/ttyACM0 (adjust in config.py)

3. 🧠 Place Model Files
Place model.tflite and scaler.pkl inside the ai/ folder

🔐 Full Defense Stack
Layer	Function	Hardware	Software
Physical	Lateral spoof rejection	✅	–
RF Filter	Threshold-based hard filter	–	✅
AI Detector	Statistical spoof detection	–	✅
Coherence	Temporal-spatial validation	–	✅

🚀 Status
✅ Fully modular
✅ Lightweight (runs under 100ms/loop)
✅ Real-time compatible on Pi 5
🟡 Awaiting real-world test logging
🟢 Offline CSV testing module ready

🤖 Credits
Developed by Aditya Parihar
Under: Indian Army



---
