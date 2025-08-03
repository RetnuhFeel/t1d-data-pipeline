import pandas as pd
import numpy as np
import os
import argparse
from datetime import datetime, timedelta

parser = argparse.ArgumentParser()
parser.add_argument("--subject", type=str, default="001")
args = parser.parse_args()

# Output directories
RAW_DIR = "../data/raw/"
PROCESSED_DIR = "../data/processed/"
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Parameters
SUBJECT_ID = args.subject
START_TIME = datetime(2025, 1, 1, 6)  # Start at 6 AM
NUM_DAYS = 3
CGM_INTERVAL_MIN = 5
ENTRIES_PER_DAY = int((24 * 60) / CGM_INTERVAL_MIN)


def generate_cgm_data():
    timestamps = [START_TIME + timedelta(minutes=CGM_INTERVAL_MIN * i)
                  for i in range(ENTRIES_PER_DAY * NUM_DAYS)]
    glucose = np.random.normal(loc=120, scale=30, size=len(timestamps)).clip(40, 400)

    df = pd.DataFrame({
        "timestamp": timestamps,
        "glucose_mgdl": glucose.round(1)
    })

    raw_path = os.path.join(RAW_DIR, f"{SUBJECT_ID}_cgm_raw.csv")
    df.to_csv(raw_path, index=False)
    return df


def generate_insulin_data():
    timestamps = []
    carbs = []
    insulin = []
    types = []

    for i in range(NUM_DAYS):
        base = START_TIME + timedelta(days=i)
        for hour in [8, 12, 18]:  # 3 boluses per day
            t = base + timedelta(hours=hour)
            timestamps.append(t)
            carbs.append(np.random.randint(30, 90))
            insulin.append(round(np.random.uniform(2, 10), 2))
            types.append(np.random.choice(['Meal Bolus', 'Correction Bolus']))

    df = pd.DataFrame({
        "timestamp": timestamps,
        "carbs_g": carbs,
        "insulin_units": insulin,
        "bolus_type": types
    })

    raw_path = os.path.join(RAW_DIR, f"{SUBJECT_ID}_insulin_raw.csv")
    df.to_csv(raw_path, index=False)
    return df


def preprocess_and_save(df, name):
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df.dropna(subset=['timestamp'], inplace=True)
    df = df.sort_values(by='timestamp')
    out_path = os.path.join(PROCESSED_DIR, f"{SUBJECT_ID}_{name}_processed.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved processed: {out_path}")


if __name__ == "__main__":
    cgm_df = generate_cgm_data()
    insulin_df = generate_insulin_data()

    preprocess_and_save(cgm_df, "cgm")
    preprocess_and_save(insulin_df, "insulin")
