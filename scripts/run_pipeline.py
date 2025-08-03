import subprocess
import os
import argparse

# Define paths to scripts in run order
SCRIPTS = [
    "generate_and_preprocess_synthetic.py",
    "feature_engineering.py",
    "modeling.py"
]

def run_script(script_name, subject_id):
    full_path = os.path.join(os.path.dirname(__file__), script_name)
    print(f"\n▶ Running: {script_name} (subject {subject_id})")
    # pass subject_id as argument if script accepts it
    result = subprocess.run(["python3", full_path, "--subject", subject_id], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Success")
        print(result.stdout)
    else:
        print("❌ Failed")
        print(result.stderr)

def main():
    # parse command line arguments
    parser = argparse.ArgumentParser(description="Run the full T1D synthetic pipeline.")
    parser.add_argument("--subject", type=str, default="001", help="Subject ID to use for synthetic data (default: 001)")
    parser.add_argument("--dry-run", action="store_true", help="List scripts without executing")
    parser.add_argument("--skip-model", action="store_true", help="Skip the modeling stage")
    args = parser.parse_args()

    print("🔁 Starting full synthetic T1D pipeline...\n")
    for script in SCRIPTS:
        if args.skip_model and "modeling" in script:
            print("⏩ Skipping modeling step as requested.")
            continue
 
        if args.dry_run:
            print(f"📝 Would run: {script} --subject {args.subject}")
        else:
            run_script(script, args.subject)

    if not args.dry_run:
        print("\n🎉 Pipeline completed successfully.")

if __name__ == "__main__":
    main()
