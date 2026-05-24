#!/usr/bin/env python3
"""
evaluate_backtest.py
--------------------
Reads a Scion SUMMARY predictions CSV produced by a backtest run and
computes performance metrics against actual game results.

The predictions CSV contains Scion's calls (HomFave, VisFave, HomDog,
VisDog, No Play). You supply an actuals CSV with the real game outcomes,
and this script joins them on Game_Id and computes:

  - Total plays, win/loss/push breakdown
  - Hit rate (%) overall and by play type
  - P&L in cents per game at actual bookie prices
  - ROI (%) overall and by ensemble (PM150, PM210)
  - Plays by confidence star rating
  - Monthly breakdown

Usage (from repo root):
    python scripts/evaluate_backtest.py \\
        --preds  results/backtests/EXP-001_20251001_120000/MLB_Scion_SUMMARY_*.csv \\
        --actuals data/backtest/outsample/actuals_2024.csv \\
        --out    results/backtests/EXP-001_eval.csv

Actuals CSV format (minimum required columns):
    game_id, home_win    (1 = home won, 0 = visitor won)
"""

import argparse
import glob
import os
import sys
import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# Column name constants — match MLB_Scion_Preds.py output
# ---------------------------------------------------------------------------
COL_GAME_ID       = "Pred_Id"
COL_DATE          = "Date"
COL_H_TEAM        = "H_Team"
COL_V_TEAM        = "V_Team"
COL_H_BOOKIE      = "H_Bookie_Price"
COL_V_BOOKIE      = "V_Bookie_Price"
COL_ENS1_POS      = "V113PM210_2023_PlayPosition"
COL_ENS2_POS      = "V113PM150_2023_PlayPosition"
COL_ENS1_HPRICE   = "V113PM210_2023_H_Price"
COL_ENS2_HPRICE   = "V113PM150_2023_H_Price"
COL_ENS1_AGREE    = "V113PM210_2023_VoteAgreement"
COL_ENS2_AGREE    = "V113PM150_2023_VoteAgreement"
COL_SCION_POS     = "Scion_Side_Play_Position"
COL_SCION_STARS   = "Scion_Side_Stars"
COL_SCION_CONF    = "Scion_Side_Play_Confidence"
COL_COMMENTS      = "Comments"

NO_PLAY           = "No Play"
HOME_FAVE         = "HomFave"
HOME_DOG          = "HomDog"
VIS_FAVE          = "VisFave"
VIS_DOG           = "VisDog"
HOME_PLAYS        = {HOME_FAVE, HOME_DOG}
VIS_PLAYS         = {VIS_FAVE, VIS_DOG}


def load_preds(preds_path):
    """Load predictions CSV, expanding glob patterns if needed."""
    if "*" in preds_path:
        matches = sorted(glob.glob(preds_path))
        if not matches:
            print(f"[evaluate] ERROR: No files matched: {preds_path}")
            sys.exit(1)
        preds_path = matches[-1]  # most recent if multiple
        print(f"[evaluate] Using predictions file: {preds_path}")
    return pd.read_csv(preds_path)


def load_actuals(actuals_path):
    """Load actuals CSV. Must contain game_id and home_win columns."""
    df = pd.read_csv(actuals_path)
    required = {"game_id", "home_win"}
    missing = required - set(df.columns.str.lower())
    if missing:
        print(f"[evaluate] ERROR: Actuals file missing columns: {missing}")
        sys.exit(1)
    df.columns = df.columns.str.lower()
    return df


def american_to_profit(price, stake=1.0):
    """Convert American odds to profit on a winning bet of given stake."""
    price = float(price)
    if price < 0:
        return round(stake * (100.0 / abs(price)), 4)
    else:
        return round(stake * (price / 100.0), 4)


def evaluate(preds_df, actuals_df, ensemble_col, price_col, label):
    """Evaluate a single ensemble column against actuals."""
    plays = preds_df[preds_df[ensemble_col] != NO_PLAY].copy()
    if plays.empty:
        print(f"\n[{label}] No plays found — skipping.")
        return None

    # Join to actuals on game_id
    plays = plays.merge(
        actuals_df[["game_id", "home_win"]],
        left_on=COL_GAME_ID, right_on="game_id", how="inner"
    )
    unmatched = len(plays[plays["home_win"].isna()])
    if unmatched:
        print(f"[{label}] WARNING: {unmatched} plays could not be matched to actuals.")

    plays = plays.dropna(subset=["home_win"])
    plays["home_win"] = plays["home_win"].astype(int)

    # Determine whether Scion's call was correct
    def is_win(row):
        pos = row[ensemble_col]
        hw  = row["home_win"]
        if pos in HOME_PLAYS:
            return 1 if hw == 1 else 0
        elif pos in VIS_PLAYS:
            return 1 if hw == 0 else 0
        return None  # push or unknown

    plays["win"] = plays.apply(is_win, axis=1)
    plays = plays.dropna(subset=["win"])
    plays["win"] = plays["win"].astype(int)

    # P&L per play at actual bookie price
    def pnl(row):
        pos = row[ensemble_col]
        if pos in HOME_PLAYS:
            price = row[COL_H_BOOKIE]
        else:
            price = row[COL_V_BOOKIE]
        if row["win"] == 1:
            return american_to_profit(price)
        else:
            return -1.0

    plays["pnl"] = plays.apply(pnl, axis=1)

    total       = len(plays)
    wins        = plays["win"].sum()
    losses      = total - wins
    hit_rate    = round(wins / total * 100, 2) if total else 0
    total_pnl   = round(plays["pnl"].sum(), 2)
    roi         = round(total_pnl / total * 100, 2) if total else 0

    print(f"\n{'='*55}")
    print(f"  {label}")
    print(f"{'='*55}")
    print(f"  Total plays    : {total}")
    print(f"  Wins           : {wins}")
    print(f"  Losses         : {losses}")
    print(f"  Hit rate       : {hit_rate}%")
    print(f"  Total P&L      : {total_pnl} units")
    print(f"  ROI            : {roi}%")

    # Breakdown by play type
    print(f"\n  Breakdown by play type:")
    for pt in [HOME_FAVE, HOME_DOG, VIS_FAVE, VIS_DOG]:
        subset = plays[plays[ensemble_col] == pt]
        if not subset.empty:
            pt_wins = subset["win"].sum()
            pt_total = len(subset)
            pt_pnl = round(subset["pnl"].sum(), 2)
            print(f"    {pt:12s}: {pt_total:3d} plays, "
                  f"{pt_wins}/{pt_total} wins "
                  f"({round(pt_wins/pt_total*100,1)}%), "
                  f"P&L={pt_pnl}")

    return {
        "label": label,
        "total_plays": total,
        "wins": wins,
        "losses": losses,
        "hit_rate_pct": hit_rate,
        "total_pnl_units": total_pnl,
        "roi_pct": roi,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate a Scion backtest predictions CSV against actual results."
    )
    parser.add_argument("--preds",   required=True, help="Path to Scion SUMMARY CSV (glob OK)")
    parser.add_argument("--actuals", required=True, help="Path to actuals CSV (game_id, home_win)")
    parser.add_argument("--out",     default=None,  help="Optional path to save summary CSV")
    args = parser.parse_args()

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    preds_path   = os.path.join(repo_root, args.preds)   if not os.path.isabs(args.preds)   else args.preds
    actuals_path = os.path.join(repo_root, args.actuals) if not os.path.isabs(args.actuals) else args.actuals

    preds_df   = load_preds(preds_path)
    actuals_df = load_actuals(actuals_path)

    print(f"[evaluate] Predictions loaded : {len(preds_df)} games")
    print(f"[evaluate] Actuals loaded     : {len(actuals_df)} games")

    results = []

    # Evaluate each ensemble
    r1 = evaluate(preds_df, actuals_df, COL_ENS1_POS, COL_ENS1_HPRICE, "PM210 Ensemble (Ens1)")
    r2 = evaluate(preds_df, actuals_df, COL_ENS2_POS, COL_ENS2_HPRICE, "PM150 Ensemble (Ens2)")
    r3 = evaluate(preds_df, actuals_df, COL_SCION_POS, COL_H_BOOKIE,   "Scion Combined Side")

    for r in [r1, r2, r3]:
        if r:
            results.append(r)

    # Optional: save summary
    if args.out and results:
        out_path = os.path.join(repo_root, args.out) if not os.path.isabs(args.out) else args.out
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        pd.DataFrame(results).to_csv(out_path, index=False)
        print(f"\n[evaluate] Summary saved to: {out_path}")


if __name__ == "__main__":
    main()
