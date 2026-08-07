#!/usr/bin/env python3
"""
run_scion.py
------------
Thin wrapper that reads configs/mlb_scion_config.yaml and invokes
MLB_Scion.py with the correct command-line arguments.

MLB_Scion.py captures os.getcwd() at startup and uses it as the root
for all output folders (.MLB_scion_preds, .MLB_scion_logs). This wrapper
therefore runs the subprocess with cwd set to the repo root, so that
output lands in results/ rather than src/.

src/ is added to PYTHONPATH so all module imports resolve correctly
regardless of the working directory.

Usage (from repo root):
    python src/run_scion.py
    python src/run_scion.py --config configs/mlb_scion_config.yaml
"""

import argparse
import os
import subprocess
import sys
import yaml


def main():
    parser = argparse.ArgumentParser(
        description="Run MLB Scion using settings from a YAML config file."
    )
    parser.add_argument(
        "--config",
        default="configs/mlb_scion_config.yaml",
        help="Path to the Scion YAML config file (default: configs/mlb_scion_config.yaml)",
    )
    args = parser.parse_args()

    # Resolve paths relative to the repo root (parent of src/)
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(repo_root, args.config)

    if not os.path.exists(config_path):
        print(f"[run_scion] ERROR: Config file not found: {config_path}")
        sys.exit(1)

    with open(config_path, "r") as fh:
        cfg = yaml.safe_load(fh)

    system_path    = os.path.join(repo_root, cfg["system_path"])
    sciondata_file = os.path.join(repo_root, cfg["input"]["sciondata_file"])
    mups_file      = os.path.join(repo_root, cfg["input"]["mups_file"])
    preds_dir      = os.path.join(repo_root, cfg["output"]["predictions_dir"])
    logs_dir       = os.path.join(repo_root, cfg["output"]["logs_dir"])
    temp_dir       = os.path.join(repo_root, cfg["output"]["tempfiles_dir"])

    # Ensure output directories exist
    for d in [preds_dir, logs_dir, temp_dir]:
        os.makedirs(d, exist_ok=True)

    # Build environment:
    # - PYTHONPATH includes src/ so all module imports resolve from repo root cwd
    # - MLB_SCION_* vars pass output paths to the process
    env = os.environ.copy()
    src_dir = os.path.join(repo_root, "src")
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = src_dir + (os.pathsep + existing_pythonpath if existing_pythonpath else "")
    # Suppress SettingWithCopyWarning and deprecation warnings from the Scion
    # engine internals. These are known and non-critical.
    env["PYTHONWARNINGS"] = "ignore"
    env["MLB_SCION_SYSTEM_PATH"] = system_path.rstrip(os.sep) + os.sep  # ensure exactly one trailing slash
    env["MLB_SCION_PREDS_DIR"]   = preds_dir
    env["MLB_SCION_LOGS_DIR"]    = logs_dir
    env["MLB_SCION_TEMP_DIR"]    = temp_dir

    script = os.path.join(src_dir, "MLB_Scion.py")

    cmd = [
        sys.executable, script,
        sciondata_file,   # usrMasterDB_Fname
        mups_file,        # usrMatchup_Fname
    ]

    print(f"[run_scion] System path : {system_path}")
    print(f"[run_scion] Scion data  : {sciondata_file}")
    print(f"[run_scion] MUPs file   : {mups_file}")
    print(f"[run_scion] Predictions : {preds_dir}")
    print(f"[run_scion] Logs        : {logs_dir}")
    print(f"[run_scion] Working dir : {repo_root}")
    print(f"[run_scion] Executing   : {' '.join(cmd)}\n")

    # Run from repo root so MLB_Scion.py's os.getcwd() == repo root
    # Output folders (.MLB_scion_preds, .MLB_scion_logs) are then
    # created under repo root, which maps to results/ via .gitignore
    result = subprocess.run(cmd, cwd=repo_root, env=env)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
