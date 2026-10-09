"""
REAL-TIME SAFETY CLASSIFIER
Loads trained model and classifies live sensor data

USAGE:
    python realtime_classifier.py

REQUIREMENTS:
    pip install pyserial numpy
"""

import serial
import pickle
import numpy as np
import time
from collections import deque

# ============================================================
# CONFIGURATION
# ============================================================

SERIAL_PORT = '/dev/cu.usbmodem14101'  # <-- CHANGE THIS
BAUD_RATE = 9600
MODEL_PATH = '../models/safety_classifier.pkl'

# ============================================================
# LOAD MODEL
# ============================================================

def load_model():
    print("Loading model...")

    with open(MODEL_PATH, 'rb') as f:
        model_data = pickle.load(f)

    print(f"Loaded: {model_data['model_name']}")
    return model_data

# ============================================================
# FEATURE EXTRACTION (must match training)
# ============================================================

class FeatureExtractor:
    def __init__(self, window_size=5):
        self.window = deque(maxlen=window_size)
        self.prev_value = 0

    def extract(self, sensor_value):
        self.window.append(sensor_value)

        features = {
            'sensor_value': sensor_value,
            'rolling_mean': np.mean(self.window),
            'rolling_std': np.std(self.window) if len(self.window) > 1 else 0,
            'rolling_max': max(self.window),
            'delta': sensor_value - self.prev_value,
            'abs_delta': abs(sensor_value - self.prev_value)
        }

        self.prev_value = sensor_value
        return features

# ============================================================
# MAIN LOOP
# ============================================================

def run_classifier():
    model_data = load_model()
    model = model_data['model']
    scaler = model_data['scaler']
    feature_cols = model_data['feature_cols']

    extractor = FeatureExtractor()

    print("=" * 50)
    print("REAL-TIME SAFETY CLASSIFIER")
    print("=" * 50)
    print(f"Port: {SERIAL_PORT}")
    print("Press Ctrl+C to stop")
    print("=" * 50)

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)

        # Skip header line
        ser.readline()

        while True:
            line = ser.readline().decode('utf-8').strip()

            if line and ',' in line:
                try:
                    parts = line.split(',')
                    timestamp = int(parts[0])
                    sensor_value = int(parts[1])

                    features = extractor.extract(sensor_value)

                    X = np.array([[features[col] for col in feature_cols]])
                    X_scaled = scaler.transform(X)

                    prediction = model.predict(X_scaled)[0]

                    if prediction == 0:
                        status = "\033[92mSAFE\033[0m"      # Green
                    else:
                        status = "\033[91mUNSAFE\033[0m"    # Red

                    print(f"Value: {sensor_value:5d} | Status: {status}")

                except (ValueError, IndexError):
                    pass

    except KeyboardInterrupt:
        print("\nStopped")

    except FileNotFoundError:
        print(f"\nModel not found at {MODEL_PATH}")
        print("Run train_classifier.py first")

    finally:
        if 'ser' in locals():
            ser.close()

# ============================================================
# RUN
# ============================================================

if __name__ == '__main__':
    run_classifier()
