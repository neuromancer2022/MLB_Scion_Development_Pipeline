#!/usr/bin/env python3
"""
promote_to_deployment.py
------------------------
Copies proven model assets and config from this development pipeline
to the MLB_Scion_Deployment_Pipeline repository, ready for a release
tag. Run this once an experiment has been validated and you are ready
to graduate it to production.

What it copies:
  models/MLB_Scion_CFG.txt     → <deployment_repo>/models/MLB_Scion_CFG.txt
  models/experiments/<name>/   → <deployment_repo>/models/  (pkl files etc)

Usage (from repo root):
    python scripts/promote_to_deployment.py \\
        --deployment-repo ../MLB_Scion_Deployment_Pipeline \\
        --cfg models/MLB_Scion_CFG.txt

    # To also promote experimental pkl files:
    python scripts/promote_to_deployment.py \\
        --deployment-repo ../MLB_Scion_Deployment_Pipeline \\
        --cfg models/MLB_Scion_CFG.txt \\
        --model-dir models/experiments/my_new_models/
"""

import argparse
import os
import shutil
import sys
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(
        description="Promote validated model/config to the deployment pipeline."
    )
    parser.add_argument(
        "--deployment-repo", required=True,
        help="Path to the MLB_Scion_Deployment_Pipeline repository root."
    )
    parser.add_argument(
        "--cfg", default="models/MLB_Scion_CFG.txt",
        help="Path to the CFG.txt to promote (default: models/MLB_Scion_CFG.txt)."
    )
    parser.add_argument(
        "--model-dir", default=None,
        help="Optional: path to a folder of pkl/JSON/CSV model assets to copy into deployment models/."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be copied without actually copying anything."
    )
    args = parser.parse_args()

    repo_root    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    deploy_root  = os.path.abspath(os.path.join(repo_root, args.deployment_repo))
    cfg_src      = os.path.join(repo_root, args.cfg)
    cfg_dst      = os.path.join(deploy_root, "models", "MLB_Scion_CFG.txt")

    if not os.path.exists(deploy_root):
        print(f"[promote] ERROR: Deployment repo not found: {deploy_root}")
        sys.exit(1)

    if not os.path.exists(cfg_src):
        print(f"[promote] ERROR: CFG file not found: {cfg_src}")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"\n[promote] {'='*55}")
    print(f"[promote] Promoting to deployment pipeline")
    print(f"[promote] Source  : {repo_root}")
    print(f"[promote] Target  : {deploy_root}")
    print(f"[promote] Dry run : {args.dry_run}")
    print(f"[promote] {'='*55}\n")

    # --- Backup existing deployment CFG ---------------------------------
    if os.path.exists(cfg_dst) and not args.dry_run:
        backup = cfg_dst + f".backup_{timestamp}"
        shutil.copy(cfg_dst, backup)
        print(f"[promote] Backed up existing CFG to: {backup}")

    # --- Copy CFG -------------------------------------------------------
    print(f"[promote] CFG: {cfg_src}")
    print(f"         → {cfg_dst}")
    if not args.dry_run:
        shutil.copy(cfg_src, cfg_dst)
        print(f"[promote] CFG copied.")

    # --- Copy model assets if provided ----------------------------------
    if args.model_dir:
        model_src = os.path.join(repo_root, args.model_dir)
        model_dst = os.path.join(deploy_root, "models")

        if not os.path.exists(model_src):
            print(f"[promote] ERROR: Model directory not found: {model_src}")
            sys.exit(1)

        files = [f for f in os.listdir(model_src) if not f.startswith(".")]
        print(f"\n[promote] Model assets ({len(files)} files): {model_src}")
        print(f"         → {model_dst}")

        for fname in sorted(files):
            src = os.path.join(model_src, fname)
            dst = os.path.join(model_dst, fname)
            print(f"  {fname}")
            if not args.dry_run:
                shutil.copy(src, dst)

        if not args.dry_run:
            print(f"[promote] {len(files)} model file(s) copied.")

    if args.dry_run:
        print("\n[promote] DRY RUN complete — nothing was copied.")
    else:
        print(f"\n[promote] Promotion complete.")
        print(f"[promote] Next steps:")
        print(f"  1. cd {deploy_root}")
        print(f"  2. Review the changes: git diff models/")
        print(f"  3. Commit: git add models/ && git commit -m 'chore: promote model vX.Y from dev pipeline'")
        print(f"  4. Tag:    git tag -a vX.Y -m 'Release vX.Y — <description>'")
        print(f"  5. Push:   git push origin main --tags")


if __name__ == "__main__":
    main()
