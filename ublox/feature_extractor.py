# ublox/feature_extractor.py

def extract_features(msg_dict):
    """
    Extracts hdop, vdop, satellites_used, jammingIndicator, noise_per_ms
    Input: dict from get_ublox_data()
    Output: dict of extracted features
    """

    try:
        gga = msg_dict.get("GGA", None)
        gsa = msg_dict.get("GSA", None)
        sig = msg_dict.get("SIG", None)
        rf = msg_dict.get("RF", None)

        # HDOP, VDOP
        hdop = float(gga.HDOP) if gga else -1
        vdop = float(gsa.PDOP) - float(gga.HDOP) if gsa and gga else -1

        # Satellites used (from GGA)
        sats_used = int(gga.numSV) if gga else -1

        # SNR / C/N0 from UBX-NAV-SIG
        cn0_values = [sig.get("cno") for sig in sig.signals if hasattr(sig, "cno")]
        avg_cn0 = sum(cn0_values) / len(cn0_values) if cn0_values else -1

        # UBX-MON-RF: jammingIndicator & noise_per_ms
        jamInd = rf[0].jamInd if isinstance(rf, list) else rf.jamInd
        noise = rf[0].noisePerMS if isinstance(rf, list) else rf.noisePerMS

        return {
            "hdop": hdop,
            "vdop": vdop,
            "sats": sats_used,
            "jammingIndicator": jamInd,
            "noise_per_ms": noise,
            "avg_cn0": avg_cn0
        }

    except Exception as e:
        print(f"[Feature Extractor Error] {e}")
        return None
