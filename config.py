# config.py

# ⏱️ GNSS fix polling rate (in seconds)
LOOP_INTERVAL = 0.1  # 100 ms

# 🔒 Thresholds for jamming/spoofing defense
HARD_REJECT_JAMIND = 10
HARD_REJECT_NOISE = 3.0

AI_TRIGGER_JAMIND_MIN = 8
AI_TRIGGER_NOISE_MIN = 2.8

HDOP_AI_MIN = 1.5
VDOP_AI_MIN = 2.0
SATELLITES_AI_MIN = 9

# 🛰️ Port configuration (update on actual Pi)
GNSS_PORT = "/dev/ttyACM0"
FC_PORT = "/dev/ttyUSB0"
