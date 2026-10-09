"""
ML CLASSIFIER TRAINING
Trains a model to classify safe vs unsafe sensor readings

USAGE:
    python train_classifier.py

REQUIREMENTS:
    pip install pandas scikit-learn matplotlib

INPUT:
    CSV file with columns: timestamp, sensor_value, label

OUTPUT:
    - Trained model (pickle file)
    - Performance metrics
"""

import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR = '../data'
MODEL_DIR = '../models'

# ============================================================
# STEP 1: LOAD DATA
# ============================================================

def load_data(filepath):
    print("=" * 50)
    print("STEP 1: LOADING DATA")
    print("=" * 50)

    df = pd.read_csv(filepath)

    print(f"Loaded {len(df)} samples")
    print(f"Columns: {list(df.columns)}")
    print(f"\nLabel distribution:")
    print(df['label'].value_counts())
    print(f"\nSensor value stats:")
    print(df['sensor_value'].describe())

    return df

# ============================================================
# STEP 2: FEATURE ENGINEERING
# ============================================================

def create_features(df):
    print("\n" + "=" * 50)
    print("STEP 2: FEATURE ENGINEERING")
    print("=" * 50)

    features = df.copy()

    window = 5
    features['rolling_mean'] = df['sensor_value'].rolling(window=window, min_periods=1).mean()
    features['rolling_std'] = df['sensor_value'].rolling(window=window, min_periods=1).std().fillna(0)
    features['rolling_max'] = df['sensor_value'].rolling(window=window, min_periods=1).max()

    features['delta'] = df['sensor_value'].diff().fillna(0)
    features['abs_delta'] = features['delta'].abs()

    feature_cols = ['sensor_value', 'rolling_mean', 'rolling_std', 'rolling_max', 'delta', 'abs_delta']

    print(f"Created {len(feature_cols)} features: {feature_cols}")

    return features, feature_cols

# ============================================================
# STEP 3: TRAIN/TEST SPLIT
# ============================================================

def split_data(features, feature_cols):
    print("\n" + "=" * 50)
    print("STEP 3: TRAIN/TEST SPLIT")
    print("=" * 50)

    X = features[feature_cols]
    y = features['label']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return X_train_scaled, X_test_scaled, y_train, y_test, scaler

# ============================================================
# STEP 4: TRAIN MODELS
# ============================================================

def train_models(X_train, y_train):
    print("\n" + "=" * 50)
    print("STEP 4: TRAINING MODELS")
    print("=" * 50)

    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'SVM': SVC(kernel='rbf', random_state=42),
        'KNN': KNeighborsClassifier(n_neighbors=5)
    }

    trained_models = {}
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        trained_models[name] = model

    return trained_models

# ============================================================
# STEP 5: EVALUATE MODELS
# ============================================================

def evaluate_models(models, X_test, y_test):
    print("\n" + "=" * 50)
    print("STEP 5: EVALUATION")
    print("=" * 50)

    results = {}
    best_model = None
    best_accuracy = 0

    for name, model in models.items():
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        results[name] = accuracy

        print(f"\n{name}:")
        print(f"  Accuracy: {accuracy:.2%}")
        print(f"  Confusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(f"    {cm[0]}")
        print(f"    {cm[1]}")

        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_model = (name, model)

    print(f"\n{'=' * 50}")
    print(f"BEST MODEL: {best_model[0]} ({best_accuracy:.2%} accuracy)")
    print(f"{'=' * 50}")

    return best_model, results

# ============================================================
# STEP 6: SAVE MODEL
# ============================================================

def save_model(model, scaler, feature_cols, filepath):
    print("\n" + "=" * 50)
    print("STEP 6: SAVING MODEL")
    print("=" * 50)

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    model_data = {
        'model': model[1],
        'model_name': model[0],
        'scaler': scaler,
        'feature_cols': feature_cols
    }

    with open(filepath, 'wb') as f:
        pickle.dump(model_data, f)

    print(f"Model saved to: {filepath}")

# ============================================================
# MAIN
# ============================================================

def main():
    print("\n")
    print("*" * 50)
    print("  CAPACITIVE SENSOR ML CLASSIFIER")
    print("*" * 50)

    data_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]

    if not data_files:
        print(f"\nNo CSV files found in {DATA_DIR}")
        print("Run serial_data_collector.py first to collect data")
        return

    print(f"\nAvailable data files:")
    for i, f in enumerate(data_files):
        print(f"  {i+1}. {f}")

    latest_file = sorted(data_files)[-1]
    filepath = os.path.join(DATA_DIR, latest_file)
    print(f"\nUsing: {latest_file}")

    df = load_data(filepath)
    features, feature_cols = create_features(df)
    X_train, X_test, y_train, y_test, scaler = split_data(features, feature_cols)
    models = train_models(X_train, y_train)
    best_model, results = evaluate_models(models, X_test, y_test)
    save_model(best_model, scaler, feature_cols, f'{MODEL_DIR}/safety_classifier.pkl')

    print("\n" + "*" * 50)
    print("  TRAINING COMPLETE")
    print("*" * 50)

if __name__ == '__main__':
    main()
