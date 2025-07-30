# main.py

import time
from config import *
from ublox.m9n_reader import get_gnss_fix
from ublox.feature_extractor import extract_features
from filters.jamming_filter import jamming_filter
from ai.spoof_classifier import SpoofClassifier
from fc.coherence_checker import is_coherent
from fc.forwarder import send_fix_to_fc
from utils.logger import log_decision

# Initialize AI model
clf = SpoofClassifier("ai/model.tflite")
prev_fix = None

print("🚀 GNSS Spoofing Defense System Initialized")

while True:
    loop_start = time.time()

    fix = get_gnss_fix(GNSS_PORT)
    if fix is None:
        log_decision(None, None, "SKIP: No GNSS fix received")
        time.sleep(LOOP_INTERVAL)
        continue

    features = extract_features(fix)
    if not features:
        log_decision(fix, None, "SKIP: Feature extraction failed")
        time.sleep(LOOP_INTERVAL)
        continue

    hdop, vdop, sats = features["hdop"], features["vdop"], features["sats"]
    jamInd, noise = features["jamInd"], features["noise_per_ms"]

    # ✅ Layer 1: Clean Bypass for overhead, noise-free signals
    if (hdop <= HDOP_AI_MIN and
        vdop <= VDOP_AI_MIN and
        sats >= SATELLITES_AI_MIN and
        jamInd < AI_TRIGGER_JAMIND_MIN and
        noise < AI_TRIGGER_NOISE_MIN):
        send_fix_to_fc(fix)
        log_decision(fix, features, "ACCEPT: Clean bypass")
        prev_fix = features
        loop_duration = time.time() - loop_start
        time.sleep(max(0, LOOP_INTERVAL - loop_duration))
        continue

    # ✅ Layer 2: RF filter (hardcoded jam/spoof rejection)
    rf_status = jamming_filter(jamInd, noise)

    if rf_status == "reject":
        log_decision(fix, features, "REJECT: RF Hard threshold")
        loop_duration = time.time() - loop_start
        time.sleep(max(0, LOOP_INTERVAL - loop_duration))
        continue

    # ✅ Layer 3: Medium Risk (coherence + AI)
    if rf_status == "medium_risk":
        if not is_coherent(prev_fix, features):
            log_decision(fix, features, "REJECT: Incoherent (Medium RF)")
            loop_duration = time.time() - loop_start
            time.sleep(max(0, LOOP_INTERVAL - loop_duration))
            continue

        prediction = clf.predict([hdop, vdop, sats])
        if prediction < 0.5:
            log_decision(fix, features, "REJECT: AI (Medium RF)")
        else:
            send_fix_to_fc(fix)
            log_decision(fix, features, "ACCEPT: AI + Coherent (Medium RF)")
            prev_fix = features

    # ✅ Layer 4: Low Risk (AI only)
    elif rf_status == "low_risk":
        prediction = clf.predict([hdop, vdop, sats])
        if prediction < 0.5:
            log_decision(fix, features, "REJECT: AI (Low RF)")
        else:
            send_fix_to_fc(fix)
            log_decision(fix, features, "ACCEPT: AI (Low RF)")
            prev_fix = features

    # ✅ Enforce 100ms interval
    loop_duration = time.time() - loop_start
    time.sleep(max(0, LOOP_INTERVAL - loop_duration))
