import pandas as pd
import numpy as np
import os
import argparse
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

parser = argparse.ArgumentParser()
parser.add_argument("--subject", type=str, default="001")
parser.add_argument("--test-size", type=float, default=0.2,
                    help="Fraction of the (chronologically last) rows held out for testing (default: 0.2)")
args = parser.parse_args()

# Paths are resolved relative to the repo root, independent of the working directory
ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
FEATURES_DIR = ROOT / "data" / "features"
MODEL_DIR = ROOT / "models"
os.makedirs(MODEL_DIR, exist_ok=True)

SUBJECT_ID = args.subject
CGM_INTERVAL_MIN = 5
HORIZON_STEPS = 6  # 6 x 5-min intervals = 30 min
WINDOW = pd.Timedelta(minutes=30)

# Load data
cgm_path = os.path.join(PROCESSED_DIR, f"{SUBJECT_ID}_cgm_processed.csv")
insulin_path = os.path.join(PROCESSED_DIR, f"{SUBJECT_ID}_insulin_processed.csv")

cgm = pd.read_csv(cgm_path, parse_dates=["timestamp"])
insulin = pd.read_csv(insulin_path, parse_dates=["timestamp"])

# Sort and align by timestamp
cgm = cgm.sort_values("timestamp").reset_index(drop=True)

# Add future glucose target (30 min ahead)
cgm["glucose_target"] = cgm["glucose_mgdl"].shift(-HORIZON_STEPS)
cgm = cgm.dropna().reset_index(drop=True)


def merge_insulin_glucose(cgm_df, insulin_df):
    """Add insulin/carbs totals for doses in the window [ts - 30 min, ts] (vectorised)."""
    ins = insulin_df.sort_values("timestamp").reset_index(drop=True)
    ins_times = ins["timestamp"].to_numpy()
    cgm_times = cgm_df["timestamp"].to_numpy()

    # For each CGM timestamp find the slice of insulin events inside the window,
    # then take the difference of cumulative sums over that slice.
    left = np.searchsorted(ins_times, cgm_times - WINDOW.to_timedelta64(), side="left")
    right = np.searchsorted(ins_times, cgm_times, side="right")

    out = cgm_df.copy()
    for col, name in [("insulin_units", "insulin_last30"), ("carbs_g", "carbs_last30")]:
        csum = np.concatenate([[0.0], np.cumsum(ins[col].to_numpy(dtype=float))])
        out[name] = csum[right] - csum[left]
    return out


df = merge_insulin_glucose(cgm, insulin)

# Feature selection
features = ["glucose_mgdl", "insulin_last30", "carbs_last30"]
target = "glucose_target"

# Chronological split: train on the earlier rows, test on the later ones.
# (A random split would leak neighbouring, highly autocorrelated readings into the test set.)
split_idx = int(len(df) * (1 - args.test_size))
train, test = df.iloc[:split_idx], df.iloc[split_idx:]
X_train, y_train = train[features], train[target]
X_test, y_test = test[features], test[target]

# Fit model
model = LinearRegression()
model.fit(X_train, y_train)

# Predict and evaluate
y_pred = model.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

# Naive persistence baseline: "glucose in 30 min = glucose now"
baseline_rmse = np.sqrt(mean_squared_error(y_test, X_test["glucose_mgdl"]))

print(f"Train rows: {len(train)} | Test rows: {len(test)} (chronological split)")
print(f"Linear regression RMSE (30 min ahead): {rmse:.2f}")
print(f"Persistence baseline RMSE (30 min ahead): {baseline_rmse:.2f}")
print("Note: the data is synthetic, so these numbers are illustrative only.")

# Save predictions for later plotting
predictions = X_test.copy()
predictions["actual"] = y_test
predictions["predicted"] = y_pred
predictions["persistence_baseline"] = X_test["glucose_mgdl"]
predictions.to_csv(os.path.join(MODEL_DIR, f"{SUBJECT_ID}_glucose_predictions.csv"), index=False)
