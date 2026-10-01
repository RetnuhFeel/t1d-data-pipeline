import subprocess
import sys
import os
import argparse

# Define paths to scripts in run order
SCRIPTS = [
    "generate_and_preprocess_synthetic.py",
    "feature_engineering.py",
    "modeling.py"
]


def run_script(script_name, subject_id, seed=None):
    """Run one pipeline step. Returns True on success, False on failure."""
    full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name)
    print(f"\n▶ Running: {script_name} (subject {subject_id})")
    cmd = [sys.executable, full_path, "--subject", subject_id]
    if seed is not None and script_name.startswith("generate"):
        cmd += ["--seed", str(seed)]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Success")
        print(result.stdout)
        return True

    print("❌ Failed")
    print(result.stdout)
    print(result.stderr, file=sys.stderr)
    return False


def main():
    # parse command line arguments
    parser = argparse.ArgumentParser(description="Run the full T1D synthetic pipeline.")
    parser.add_argument("--subject", type=str, default="001", help="Subject ID to use for synthetic data (default: 001)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for synthetic data generation (default: 42)")
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
        elif not run_script(script, args.subject, args.seed):
            print(f"\n💥 Pipeline aborted: {script} failed.", file=sys.stderr)
            sys.exit(1)

    if not args.dry_run:
        print("\n🎉 Pipeline completed successfully.")


if __name__ == "__main__":
    main()
