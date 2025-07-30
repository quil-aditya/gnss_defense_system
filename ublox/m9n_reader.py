# ublox/m9n_reader.py

import serial
from pyubx2 import UBXReader

def get_ublox_data(port="/dev/ttyACM0", baudrate=9600, timeout=1.0):
    """
    Reads both NMEA and UBX messages from u-blox M9N GNSS receiver.
    Returns: dict with NMEA ($GNGGA, $GNGSA), UBX-NAV-SIG, UBX-MON-RF
    """
    try:
        with serial.Serial(port, baudrate=baudrate, timeout=timeout) as stream:
            ubr = UBXReader(stream, protfilter=7)  # NMEA + UBX
            messages = {}

            for _ in range(20):  # Read multiple lines to get all needed messages
                raw_data, parsed_data = ubr.read()
                if parsed_data:
                    msg_id = parsed_data.identity

                    if msg_id == "GNGGA":
                        messages["GGA"] = parsed_data
                    elif msg_id == "GNGSA":
                        messages["GSA"] = parsed_data
                    elif msg_id == "NAV-SIG":
                        messages["SIG"] = parsed_data
                    elif msg_id == "MON-RF":
                        messages["RF"] = parsed_data

                if all(k in messages for k in ["GGA", "GSA", "SIG", "RF"]):
                    return messages

    except Exception as e:
        print(f"[Reader Error] {e}")

    return None
