# utils/logger.py

import csv
import os
from datetime import datetime

LOG_FILE = "logs/gnss_log.csv"

# Ensure log directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log_decision(fix, features, decision_reason):
    """
    Log GNSS decision with timestamp, fix data, and reason.

    Parameters:
        fix (dict or None): GNSS fix dictionary with lat/lon/time etc.
        features (dict or None): Extracted features from fix
        decision_reason (str): Accept/Reject reason
    """
    row = {
        "timestamp": datetime.utcnow().isoformat(),
        "decision": decision_reason,
        "lat": fix.get("lat") if fix else None,
        "lon": fix.get("lon") if fix else None,
        "hdop": features.get("hdop") if features else None,
        "vdop": features.get("vdop") if features else None,
        "sats": features.get("sats") if features else None,
        "jamInd": features.get("jamInd") if features else None,
        "noise_per_ms": features.get("noise_per_ms") if features else None
    }

    write_header = not os.path.exists(LOG_FILE)

    with open(LOG_FILE, mode="a", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=row.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(row)
