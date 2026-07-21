#!/usr/bin/env python3
"""
run_dbase.py
------------
Thin wrapper that reads configs/mlb_dbase_config.yaml and invokes
MLB_dBASE.py with the correct command-line arguments.

MLB_dBASE takes three distinct files:
  1. usrMasterDB_Fname  — the existing mlbsciondata.csv (1166-column G_Id format master)
  2. usrDump_Fname      — mlbprimitives.csv (raw scraper output, game_id/date format)
  3. usrResults_Fname   — output path for the updated mlbsciondata.csv

Usage (from repo root):
    python src/run_dbase.py
    python src/run_dbase.py --config configs/mlb_dbase_config.yaml
"""

import argparse
import os
import subprocess
import sys
import yaml


def main():
    parser = argparse.ArgumentParser(
        description="Run MLB dBASE using settings from a YAML config file."
    )
    parser.add_argument(
        "--config",
        default="configs/mlb_dbase_config.yaml",
        help="Path to the dBASE YAML configuration file (default: configs/mlb_dbase_config.yaml)",
    )
    args = parser.parse_args()

    # Resolve paths relative to the repo root (parent of src/)
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(repo_root, args.config)

    if not os.path.exists(config_path):
        print(f"[run_dbase] ERROR: Config file not found: {config_path}")
        sys.exit(1)

    with open(config_path, "r") as fh:
        cfg = yaml.safe_load(fh)

    # --- Three distinct files ---
    # 1. The existing master database (mlbsciondata.csv, G_Id format)
    master_file     = os.path.join(repo_root, cfg["input"]["master_file"])
    # 2. The raw primitives dump from the scraper (mlbprimitives.csv, game_id format)
    primitives_file = os.path.join(repo_root, cfg["input"]["primitives_file"])
    # 3. Output path for the updated master
    sciondata_file  = os.path.join(repo_root, cfg["output"]["sciondata_file"])
    comma_flag      = str(cfg["input"].get("comma_delimited", True))

    # Validate inputs exist
    if not os.path.exists(master_file):
        print(f"[run_dbase] ERROR: Master file not found: {master_file}")
        print(f"[run_dbase] The master file must be an existing mlbsciondata.csv (G_Id format).")
        print(f"[run_dbase] Place your current mlbsciondata.csv at: {master_file}")
        sys.exit(1)

    if not os.path.exists(primitives_file):
        print(f"[run_dbase] ERROR: Primitives dump file not found: {primitives_file}")
        print(f"[run_dbase] Place the latest mlbprimitives.csv from the scraper at: {primitives_file}")
        sys.exit(1)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(sciondata_file), exist_ok=True)

    script = os.path.join(repo_root, "src", "MLB_dBASE.py")

    cmd = [
        sys.executable, script,
        master_file,       # usrMasterDB_Fname  — existing mlbsciondata.csv master
        primitives_file,   # usrDump_Fname      — raw scraper primitives dump
        sciondata_file,    # usrResults_Fname   — output updated master
    ]

    print(f"[run_dbase] Master DB : {master_file}")
    print(f"[run_dbase] Dump file : {primitives_file}")
    print(f"[run_dbase] Output    : {sciondata_file}")
    print(f"[run_dbase] Executing : {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=os.path.join(repo_root, "src"))
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
