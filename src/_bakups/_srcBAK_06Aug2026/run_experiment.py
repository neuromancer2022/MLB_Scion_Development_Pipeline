#!/usr/bin/env python3
"""
run_experiment.py
-----------------
Runs MLB Scion using an experiment config YAML. Supports cfg_overrides
which patch specific parameters in MLB_Scion_CFG.txt at runtime without
modifying the source file — so each experiment is fully reproducible
from its YAML alone.

Output files are automatically tagged with the experiment ID and timestamp
so results from different experiments never overwrite each other.

Usage (from repo root):
    python src/run_experiment.py --config configs/experiments/exp_001_pm150_agreethresh_0.75.yaml
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
import yaml


def apply_cfg_overrides(cfg_txt_path, overrides):
    """
    Read MLB_Scion_CFG.txt, apply parameter overrides from the experiment
    YAML, and write a patched copy to a temp file. Returns the temp file path.
    """
    with open(cfg_txt_path, "r") as fh:
        lines = fh.readlines()

    patched_lines = []
    applied = set()
    for line in lines:
        matched = False
        for param, value in overrides.items():
            # Match lines like: PARAM_NAME = value  (with optional whitespace)
            pattern = rf"^(\s*{re.escape(param)}\s*=\s*)(.+)$"
            m = re.match(pattern, line.rstrip())
            if m:
                patched_lines.append(f"{m.group(1)}{value}\r\n")
                applied.add(param)
                matched = True
                break
        if not matched:
            patched_lines.append(line)

    # Warn about any overrides that didn't match a parameter
    for param in overrides:
        if param not in applied:
            print(f"[run_experiment] WARNING: Override '{param}' not found in CFG.txt — check spelling.")

    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False,
        prefix="MLB_Scion_CFG_patched_"
    )
    tmp.writelines(patched_lines)
    tmp.close()
    return tmp.name


def main():
    parser = argparse.ArgumentParser(
        description="Run an MLB Scion experiment using a YAML experiment config."
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to the experiment YAML config file.",
    )
    args = parser.parse_args()

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(repo_root, args.config)

    if not os.path.exists(config_path):
        print(f"[run_experiment] ERROR: Config not found: {config_path}")
        sys.exit(1)

    with open(config_path, "r") as fh:
        cfg = yaml.safe_load(fh)

    # --- Resolve paths --------------------------------------------------
    system_path    = os.path.join(repo_root, cfg["system_path"])
    config_fname   = cfg.get("config_fname", "MLB_Scion_CFG.txt")
    sciondata_file = os.path.join(repo_root, cfg["input"]["sciondata_file"])
    mups_file      = os.path.join(repo_root, cfg["input"]["mups_file"])
    preds_dir      = os.path.join(repo_root, cfg["output"]["predictions_dir"])
    logs_dir       = os.path.join(repo_root, cfg["output"]["logs_dir"])
    temp_dir       = os.path.join(repo_root, cfg["output"]["tempfiles_dir"])

    # --- Experiment metadata --------------------------------------------
    exp_meta    = cfg.get("experiment", {})
    exp_id      = exp_meta.get("id", "EXP-UNKNOWN")
    exp_desc    = exp_meta.get("description", "")
    overrides   = exp_meta.get("cfg_overrides", {})
    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Tag the predictions subdirectory with experiment ID + timestamp
    exp_preds_dir = os.path.join(preds_dir, f"{exp_id}_{timestamp}")
    for d in [exp_preds_dir, logs_dir, temp_dir]:
        os.makedirs(d, exist_ok=True)

    # --- Apply CFG overrides if any -------------------------------------
    cfg_txt_path = os.path.join(system_path, config_fname)
    patched_cfg_path = None

    if overrides:
        print(f"[run_experiment] Applying {len(overrides)} CFG override(s):")
        for k, v in overrides.items():
            print(f"    {k} = {v}")
        patched_cfg_path = apply_cfg_overrides(cfg_txt_path, overrides)
        # Copy patched cfg into system_path temporarily under a unique name
        active_cfg_name = f"MLB_Scion_CFG_{exp_id}_{timestamp}.txt"
        active_cfg_path = os.path.join(system_path, active_cfg_name)
        shutil.copy(patched_cfg_path, active_cfg_path)
        os.unlink(patched_cfg_path)
    else:
        active_cfg_name = config_fname
        active_cfg_path = None

    # --- Build environment for subprocess -------------------------------
    env = os.environ.copy()
    # Add src/ to PYTHONPATH so imports resolve when cwd is repo root
    src_dir = os.path.join(repo_root, "src")
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = src_dir + (os.pathsep + existing_pythonpath if existing_pythonpath else "")
    # Suppress SettingWithCopyWarning and deprecation warnings from the Scion
    # engine internals. These are known and non-critical.
    env["PYTHONWARNINGS"] = "ignore"
    env["MLB_SCION_SYSTEM_PATH"] = system_path.rstrip(os.sep) + os.sep  # ensure exactly one trailing slash
    env["MLB_SCION_PREDS_DIR"]   = exp_preds_dir
    env["MLB_SCION_LOGS_DIR"]    = logs_dir
    env["MLB_SCION_TEMP_DIR"]    = temp_dir

    script = os.path.join(repo_root, "src", "MLB_Scion.py")

    # Temporarily patch Globals to use the experiment config name
    # by passing it via environment variable
    env["MLB_SCION_CONFIG_FNAME"] = active_cfg_name

    print(f"\n[run_experiment] {'='*55}")
    print(f"[run_experiment] Experiment : {exp_id}")
    print(f"[run_experiment] Description: {exp_desc}")
    print(f"[run_experiment] Config     : {active_cfg_name}")
    print(f"[run_experiment] MUPs file  : {mups_file}")
    print(f"[run_experiment] Output dir : {exp_preds_dir}")
    print(f"[run_experiment] {'='*55}\n")

    cmd = [sys.executable, script, sciondata_file, mups_file]
    result = subprocess.run(cmd, cwd=repo_root, env=env)

    # --- Save a copy of the experiment config alongside results ---------
    exp_config_copy = os.path.join(exp_preds_dir, f"{exp_id}_config.yaml")
    shutil.copy(config_path, exp_config_copy)
    print(f"\n[run_experiment] Config saved to results: {exp_config_copy}")

    # --- Clean up patched CFG file -------------------------------------
    if active_cfg_path and os.path.exists(active_cfg_path):
        os.unlink(active_cfg_path)

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
