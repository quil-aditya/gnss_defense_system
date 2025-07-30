# test/offline_runner.py

import pandas as pd
from config import *
from filters.jamming_filter import hard_filter, is_ai_zone
from ai.spoof_classifier import SpoofClassifier
from fc.coherence_checker import is_coherent
from utils.logger import log_decision

clf = SpoofClassifier("ai/model.tflite")
df = pd.read_csv("data/Data.csv")

print("📊 Running offline simulation...")

for i, row in df.iterrows():
    fix = row.to_dict()
    features = {
        "hdop": row["hdop"],
        "vdop": row["vdop"],
        "sats": row["satellites_used"],
        "jamInd": row["jammingIndicator"],
        "noise_per_ms": row["noise_per_ms"]
    }

    if hard_filter(features):
        log_decision(fix, features, "REJECT: Hard threshold")
        continue

    if (features["hdop"] <= HDOP_AI_MIN and
        features["vdop"] <= VDOP_AI_MIN and
        features["sats"] >= SATELLITES_AI_MIN and
        features["jamInd"] < AI_TRIGGER_JAMIND_MIN and
        features["noise_per_ms"] < AI_TRIGGER_NOISE_MIN):
        log_decision(fix, features, "ACCEPT: Clean bypass")
        continue

    if is_ai_zone(features):
        prediction = clf.predict([features["hdop"], features["vdop"], features["sats"]])
        if prediction < 0.5:
            log_decision(fix, features, "REJECT: AI")
            continue
        elif not is_coherent(fix):
            log_decision(fix, features, "REJECT: AI + Incoherent")
            continue
        else:
            log_decision(fix, features, "ACCEPT: AI + Coherent")
