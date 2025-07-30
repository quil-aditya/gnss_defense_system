# main.py

import time
from config import *
from ublox.m9n_reader import get_gnss_fix
from ublox.feature_extractor import extract_features
from filters.jamming_filter import hard_filter, is_ai_zone
from ai.spoof_classifier import SpoofClassifier
from fc.coherence_checker import is_coherent
from fc.forwarder import send_fix_to_fc
from utils.logger import log_decision

# Initialize model
clf = SpoofClassifier("ai/model.tflite")

print("🚀 GNSS Spoofing Defense System Started")

while True:
    fix = get_gnss_fix(GNSS_PORT)
    if fix is None:
        time.sleep(LOOP_INTERVAL)
        continue

    features = extract_features(fix)  # returns dict with hdop, vdop, sats, jamInd, noise_per_ms

    # Hardcoded Rejection Layer
    if hard_filter(features):
        log_decision(fix, features, "REJECT: Hard threshold")
        continue

    # Clean Bypass Layer
    if (features["hdop"] <= HDOP_AI_MIN and
        features["vdop"] <= VDOP_AI_MIN and
        features["sats"] >= SATELLITES_AI_MIN and
        features["jamInd"] < AI_TRIGGER_JAMIND_MIN and
        features["noise_per_ms"] < AI_TRIGGER_NOISE_MIN):
        send_fix_to_fc(fix)
        log_decision(fix, features, "ACCEPT: Clean bypass")
        continue

    # AI Decision Zone
    if is_ai_zone(features):
        prediction = clf.predict([features["hdop"], features["vdop"], features["sats"]])
        if prediction < 0.5:
            log_decision(fix, features, "REJECT: AI")
            continue
        elif not is_coherent(fix):
            log_decision(fix, features, "REJECT: AI + Incoherent")
            continue
        else:
            send_fix_to_fc(fix)
            log_decision(fix, features, "ACCEPT: AI + Coherent")
