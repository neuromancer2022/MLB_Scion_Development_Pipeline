#!/usr/bin/env python3
"""
compare_experiments.py
----------------------
Compares evaluation summary CSVs from two or more experiments side by side,
showing the delta in key metrics so you can quickly see whether a config
change improved or degraded performance.

Usage (from repo root):
    python scripts/compare_experiments.py \\
        results/backtests/EXP-001_eval.csv \\
        results/backtests/EXP-002_eval.csv \\
        results/backtests/EXP-003_eval.csv

Each CSV must have been produced by evaluate_backtest.py.
"""

import argparse
import os
import sys
import pandas as pd


METRICS = ["total_plays", "wins", "hit_rate_pct", "total_pnl_units", "roi_pct"]


def main():
    parser = argparse.ArgumentParser(
        description="Compare evaluation CSVs from multiple Scion experiments."
    )
    parser.add_argument(
        "eval_csvs", nargs="+",
        help="Two or more evaluation CSV files produced by evaluate_backtest.py"
    )
    args = parser.parse_args()

    if len(args.eval_csvs) < 2:
        print("[compare] ERROR: Provide at least two evaluation CSVs to compare.")
        sys.exit(1)

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frames = []

    for path in args.eval_csvs:
        full_path = os.path.join(repo_root, path) if not os.path.isabs(path) else path
        if not os.path.exists(full_path):
            print(f"[compare] ERROR: File not found: {full_path}")
            sys.exit(1)
        df = pd.read_csv(full_path)
        # Tag each row with the experiment name (derived from filename)
        exp_name = os.path.splitext(os.path.basename(full_path))[0]
        df["experiment"] = exp_name
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)

    # Print comparison table per ensemble label
    for label in combined["label"].unique():
        subset = combined[combined["label"] == label][["experiment"] + METRICS].copy()
        subset = subset.set_index("experiment")

        print(f"\n{'='*65}")
        print(f"  {label}")
        print(f"{'='*65}")
        print(subset.to_string())

        # Show delta vs first experiment
        if len(subset) > 1:
            baseline = subset.iloc[0]
            print(f"\n  Δ vs baseline ({subset.index[0]}):")
            for exp in subset.index[1:]:
                delta = subset.loc[exp, METRICS] - baseline[METRICS]
                delta_str = "  ".join([
                    f"{m}={'+' if delta[m] >= 0 else ''}{round(delta[m], 3)}"
                    for m in METRICS
                ])
                print(f"    {exp}: {delta_str}")

    print()


if __name__ == "__main__":
    main()
