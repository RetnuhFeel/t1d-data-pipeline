import subprocess
import os

# Define paths to scripts
SCRIPTS = [
    "generate_and_preprocess_synthetic.py",
    "feature_engineering.py",
    "modeling.py"
]

def run_script(script_name):
    full_path = os.path.join(os.path.dirname(__file__), script_name)
    print(f"\n▶ Running: {script_name}")
    result = subprocess.run(["python", full_path], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Success")
        print(result.stdout)
    else:
        print("❌ Failed")
        print(result.stderr)

def main():
    print("🔁 Starting full synthetic T1D pipeline...\n")
    for script in SCRIPTS:
        run_script(script)
    print("\n🎉 Pipeline completed successfully.")

if __name__ == "__main__":
    main()
