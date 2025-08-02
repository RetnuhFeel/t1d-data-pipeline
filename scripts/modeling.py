import pandas as pd
import numpy as np
import os
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Paths
PROCESSED_DIR = "../data/processed/"
FEATURES_DIR = "../data/features/"
MODEL_DIR = "../models/"
os.makedirs(MODEL_DIR, exist_ok=True)

SUBJECT_ID = "001"

# Load data
cgm_path = os.path.join(PROCESSED_DIR, f"{SUBJECT_ID}_cgm_processed.csv")
insulin_path = os.path.join(PROCESSED_DIR, f"{SUBJECT_ID}_insulin_processed.csv")

cgm = pd.read_csv(cgm_path, parse_dates=["timestamp"])
insulin = pd.read_csv(insulin_path, parse_dates=["timestamp"])

# Sort and align by timestamp
cgm = cgm.sort_values("timestamp")
cgm = cgm.reset_index(drop=True)

# Add future glucose target (30 min ahead)
cgm["glucose_target"] = cgm["glucose_mgdl"].shift(-6)  # 6 x 5-min intervals = 30 min
cgm.dropna(inplace=True)

# Merge insulin/carb data (last dose within past 30 min)
def merge_insulin_glucose(cgm_df, insulin_df):
    insulin_features = []

    for ts in cgm_df["timestamp"]:
        recent = insulin_df[(insulin_df["timestamp"] <= ts) & 
                            (insulin_df["timestamp"] >= ts - pd.Timedelta(minutes=30))]
        total_insulin = recent["insulin_units"].sum()
        total_carbs = recent["carbs_g"].sum()
        insulin_features.append((total_insulin, total_carbs))

    insulin_features = pd.DataFrame(insulin_features, columns=["insulin_last30", "carbs_last30"])
    return pd.concat([cgm_df.reset_index(drop=True), insulin_features], axis=1)

df = merge_insulin_glucose(cgm, insulin)

# Feature selection
features = ["glucose_mgdl", "insulin_last30", "carbs_last30"]
target = "glucose_target"

X = df[features]
y = df[target]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Fit model
model = LinearRegression()
model.fit(X_train, y_train)

# Predict and evaluate
y_pred = model.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

# Save results
print(f"Glucose Prediction RMSE (30 min ahead): {rmse:.2f}")

# Optional: Save predictions for later plotting
predictions = X_test.copy()
predictions["actual"] = y_test
predictions["predicted"] = y_pred
predictions.to_csv(os.path.join(MODEL_DIR, f"{SUBJECT_ID}_glucose_predictions.csv"), index=False)
