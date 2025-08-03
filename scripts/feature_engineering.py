import pandas as pd
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--subject", type=str, default="001")
args = parser.parse_args()

# File paths
PROCESSED_DIR = "../data/processed/"
FEATURES_DIR = "../data/features/"
os.makedirs(FEATURES_DIR, exist_ok=True)

SUBJECT_ID = args.subject

# Load data
cgm_path = os.path.join(PROCESSED_DIR, f"{SUBJECT_ID}_cgm_processed.csv")
insulin_path = os.path.join(PROCESSED_DIR, f"{SUBJECT_ID}_insulin_processed.csv")

cgm = pd.read_csv(cgm_path, parse_dates=["timestamp"])
insulin = pd.read_csv(insulin_path, parse_dates=["timestamp"])

# Add date column
cgm["date"] = cgm["timestamp"].dt.date
insulin["date"] = insulin["timestamp"].dt.date

# ---- CGM FEATURES ---- #
cgm_features = cgm.groupby("date").agg(
    avg_glucose=("glucose_mgdl", "mean"),
    min_glucose=("glucose_mgdl", "min"),
    max_glucose=("glucose_mgdl", "max"),
    hypo_events=("glucose_mgdl", lambda x: (x < 70).sum()),
    hyper_events=("glucose_mgdl", lambda x: (x > 180).sum()),
    time_in_range=("glucose_mgdl", lambda x: (x.between(70, 180)).mean() * 100)
).reset_index()

# ---- INSULIN FEATURES ---- #
insulin_features = insulin.groupby("date").agg(
    total_insulin=("insulin_units", "sum"),
    total_carbs=("carbs_g", "sum"),
    bolus_count=("bolus_type", "count")
).reset_index()

# ---- COMBINE FEATURES ---- #
features = pd.merge(cgm_features, insulin_features, on="date", how="outer").fillna(0)

# Save to CSV
features_path = os.path.join(FEATURES_DIR, f"{SUBJECT_ID}_daily_features.csv")
features.to_csv(features_path, index=False)

print(f"Saved engineered features to {features_path}")
