"""
SERIAL DATA COLLECTOR
Reads sensor data from Arduino and saves to CSV

USAGE:
    python serial_data_collector.py          # Collect data
    python serial_data_collector.py --list   # List available ports

REQUIREMENTS:
    pip install pyserial
"""

import serial
import time
import os
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================

SERIAL_PORT = '/dev/cu.usbmodem14101'  # <-- CHANGE THIS
BAUD_RATE = 9600
OUTPUT_DIR = '../data'

# ============================================================
# MAIN FUNCTION
# ============================================================

def collect_data():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{OUTPUT_DIR}/sensor_data_{timestamp}.csv'

    print("=" * 50)
    print("CAPACITIVE SENSOR DATA COLLECTOR")
    print("=" * 50)
    print(f"Port: {SERIAL_PORT}")
    print(f"Baud: {BAUD_RATE}")
    print(f"Output: {filename}")
    print("-" * 50)
    print("Press Ctrl+C to stop and save")
    print("=" * 50)

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Wait for Arduino to reset

        with open(filename, 'w') as f:
            sample_count = 0

            while True:
                line = ser.readline().decode('utf-8').strip()

                if line:
                    print(line)
                    f.write(line + '\n')
                    f.flush()
                    sample_count += 1

    except KeyboardInterrupt:
        print("\n" + "=" * 50)
        print(f"STOPPED - Saved {sample_count} samples to {filename}")
        print("=" * 50)

    except serial.SerialException as e:
        print(f"\nERROR: Could not open serial port")
        print(f"Details: {e}")
        print("\nTROUBLESHOOTING:")
        print("1. Check Arduino is connected")
        print("2. Close Arduino Serial Monitor (can't share port)")
        print("3. Find correct port:")
        print("   Mac/Linux: ls /dev/cu.* or ls /dev/tty.*")
        print("   Windows: Check Device Manager")

    finally:
        if 'ser' in locals():
            ser.close()

# ============================================================
# FIND AVAILABLE PORTS
# ============================================================

def list_ports():
    import serial.tools.list_ports

    ports = serial.tools.list_ports.comports()
    print("\nAvailable ports:")
    for port in ports:
        print(f"  {port.device} - {port.description}")

    if not ports:
        print("  No ports found. Is Arduino connected?")

# ============================================================
# RUN
# ============================================================

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--list':
        list_ports()
    else:
        collect_data()
