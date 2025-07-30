# fc/forwarder.py

import serial
from config import FC_PORT, FC_BAUDRATE

def send_fix_to_fc(fix):
    """
    Send a GNSS fix to the Flight Controller via UART/USB.

    Parameters:
        fix (dict): GNSS fix containing at least a formatted NMEA or message string.
    """
    try:
        with serial.Serial(FC_PORT, FC_BAUDRATE, timeout=1) as ser:
            # Example: you may replace this with structured NMEA output or a JSON string
            msg = fix.get("nmea", None)
            if msg:
                if not msg.endswith("\n"):
                    msg += "\n"
                ser.write(msg.encode())
    except Exception as e:
        print(f"⚠️ Failed to forward GNSS fix to FC: {e}")
