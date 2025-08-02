import synapseclient
import pandas as pd
import os

# Constants
SYNAPSE_ID = "syn38187184"
DOWNLOAD_DIR = "../data/raw/"
PROCESSED_DIR = "../data/processed/"

# Connect to Synapse
syn = synapseclient.Synapse()
syn.login()  # Will prompt in console or you can use syn.login('username', 'password')

# Ensure directories exist
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# List and download files (simplified: example for 1 subject’s CGM & Pump logs)
def download_and_process(subject_id="1"):
    files = {
        "CGM": f"DiaTrend-{subject_id}-cgm.csv",
        "Pump": f"DiaTrend-{subject_id}-pump.csv"
    }

    for file_type, filename in files.items():
        print(f"Downloading {filename}...")

        entity = syn.get(f"{SYNAPSE_ID}/{filename}", downloadLocation=DOWNLOAD_DIR)
        df = pd.read_csv(entity.path)

        # Preprocessing: Normalize timestamps, remove nulls
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df.dropna(subset=['timestamp'], inplace=True)

        # Example: Keep relevant columns for CGM or Pump
        if file_type == "CGM":
            df = df[['timestamp', 'glucose']].dropna()
            df = df.rename(columns={'glucose': 'glucose_mgdl'})
        else:
            df = df[['timestamp', 'carbInput', 'bolusVolumeDelivered', 'eventType']].dropna()
            df = df.rename(columns={
                'carbInput': 'carbs_g',
                'bolusVolumeDelivered': 'insulin_units',
                'eventType': 'bolus_type'
            })

        # Save cleaned file
        out_file = f"{PROCESSED_DIR}subject_{subject_id.lower()}_{file_type.lower()}_processed.csv"
        df.to_csv(out_file, index=False)
        print(f"Saved {file_type} data to: {out_file}")

if __name__ == "__main__":
    download_and_process(subject_id="1")
