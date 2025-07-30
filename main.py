# main.py

import time
from config import *
from ublox.m9n_reader import get_gnss_fix
from ublox.feature_extractor import extract_features
from filters.jamming_filter import jamming_filter
from ai.spoof_classifier import SpoofClassifier
from fc.coherence_checker import CoherenceChecker
from fc.forwarder import send_fix_to_fc
from utils.logger import log_decision

clf = SpoofClassifier("ai/model.tflite")
coherence = CoherenceChecker()

print("🚀 GNSS Spoofing Defense System Initialized")

while True:
    loop_start = time.time()

    fix = get_gnss_fix(GNSS_PORT)
    if not fix:
        log_decision(None, None, "SKIP: No GNSS fix received")
        time.sleep(LOOP_INTERVAL)
        continue

    features = extract_features(fix)
    if not features:
        log_decision(fix, None, "SKIP: Feature extraction failed")
        time.sleep(LOOP_INTERVAL)
        continue

    # Unpack values
    hdop = features["hdop"]
    vdop = features["vdop"]
    sats = features["sats"]
    jamInd = features["jamInd"]
    noise = features["noise_per_ms"]

    # ✅ Layer 1: Clean Bypass
    if (hdop <= HDOP_AI_MIN and
        vdop <= VDOP_AI_MIN and
        sats >= SATELLITES_AI_MIN and
        jamInd < AI_TRIGGER_JAMIND_MIN and
        noise < AI_TRIGGER_NOISE_MIN):
        send_fix_to_fc(fix)
        log_decision(fix, features, "ACCEPT: Clean bypass")
        time.sleep(max(0, LOOP_INTERVAL - (time.time() - loop_start)))
        continue

    # ✅ Layer 2: Hard RF Rejection
    rf_status = jamming_filter(jamInd, noise)
    if rf_status == "reject":
        log_decision(fix, features, "REJECT: RF Hard threshold")
        time.sleep(max(0, LOOP_INTERVAL - (time.time() - loop_start)))
        continue

    # ✅ Layer 3: Medium Risk (Coherence → AI)
    if rf_status == "medium_risk":
        # Check coherence first
        lat = fix.get("lat", 0.0)
        lon = fix.get("lon", 0.0)
        timestamp = fix.get("timestamp", time.time())
        fix_tuple = (lat, lon, timestamp, hdop, vdop, sats)

        if not coherence.is_coherent(fix_tuple):
            log_decision(fix, features, "REJECT: Incoherent (Medium RF)")
            time.sleep(max(0, LOOP_INTERVAL - (time.time() - loop_start)))
            continue

        prediction = clf.predict([hdop, vdop, sats])
        if prediction < 0.5:
            log_decision(fix, features, "REJECT: AI (Medium RF)")
        else:
            send_fix_to_fc(fix)
            log_decision(fix, features, "ACCEPT: AI + Coherent (Medium RF)")

    # ✅ Layer 4: Low Risk (AI → Coherence)
    elif rf_status == "low_risk":
        prediction = clf.predict([hdop, vdop, sats])
        if prediction < 0.5:
            log_decision(fix, features, "REJECT: AI (Low RF)")
        else:
            # If AI accepts, now check coherence
            lat = fix.get("lat", 0.0)
            lon = fix.get("lon", 0.0)
            timestamp = fix.get("timestamp", time.time())
            fix_tuple = (lat, lon, timestamp, hdop, vdop, sats)

            if not coherence.is_coherent(fix_tuple):
                log_decision(fix, features, "REJECT: AI Accepted but Incoherent (Low RF)")
            else:
                send_fix_to_fc(fix)
                log_decision(fix, features, "ACCEPT: AI + Coherent (Low RF)")

    # ✅ 100ms enforcement
    time.sleep(max(0, LOOP_INTERVAL - (time.time() - loop_start)))
