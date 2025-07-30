
# fc/coherence_checker.py

import time
from math import radians, cos, sin, asin, sqrt

class CoherenceChecker:
    def __init__(self):
        self.last_fix = None  # (lat, lon, time, hdop, vdop, sats_used)

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        R = 6371000  # Earth radius in meters
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
        c = 2 * asin(sqrt(a))
        return R * c

    def is_coherent(self, current_fix):
        """
        Verifies spatial-temporal plausibility of a GNSS fix.
        current_fix = (lat, lon, timestamp, hdop, vdop, sats_used)
        """
        lat, lon, fix_time, hdop, vdop, sats = current_fix

        if self.last_fix is None:
            self.last_fix = current_fix
            return True

        lat0, lon0, t0, hdop0, vdop0, sats0 = self.last_fix
        dt = fix_time - t0

        if dt <= 0:
            return True  # Treat as coherent if time hasn't advanced

        # Speed calculation (m/s)
        distance = self.haversine_distance(lat0, lon0, lat, lon)
        speed = distance / dt

        # Coherence thresholds (adjustable)
        if speed > 50:  # 180 km/h jump? suspicious.
            return False
        if abs(hdop - hdop0) > 1.5:
            return False
        if abs(vdop - vdop0) > 2.0:
            return False
        if abs(sats - sats0) > 4:
            return False

        # Passed all checks
        self.last_fix = current_fix
        return True
