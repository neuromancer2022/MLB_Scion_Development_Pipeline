# MLB Scion Audit Pipeline

Empirically tests whether the 31 LGBM models trained on pre-v5.6 (noisy) dGEN data are still usable given the v5.6-v5.8 data-quality fixes. Implements Phases 1, 2, and 4 of the MLB Scion: Audit Checklist for Noisy-Trained LGBM Models, plus a bonus monthly-stability check.

## Quick start

```bash
make setup                          # install dependencies (one-off)
# Place files into place (see "Inputs required" below), then:
make check                          # verify inputs are present
make all                            # run phase1, phase2, phase4, monthly
```

Per-phase invocation if you prefer:

```bash
make phase1     # contamination audit (no compute, 30 seconds)
make phase2     # prediction-stability test (compute-heavy: ~5-10 min for 31 models)
make phase4     # ensemble-level evaluation
make monthly    # bonus monthly-stability diagnostic
```

## Directory structure

```
mlb_scion_audit/
├── README.md
├── Makefile
├── configs/
│   └── audit_config.yaml       # paths, feature lists, thresholds
├── input/
│   ├── outsample_noisy_5May2025_25May2026.csv    # pre-v5.6 dGEN output
│   └── outsample_clean_5May2025_25May2026.csv    # post-v5.8 dGEN output
├── models/
│   └── model_NN.pkl            # the 31 pickled LGBM models (any filename ending .pkl/.joblib)
├── results/
│   ├── phase1_audit.csv                # contamination categorisation
│   ├── phase2_stability.csv            # per-model decision status
│   ├── combined_audit.csv              # Phase 1 + Phase 2 joined
│   ├── phase4_ensemble.csv             # ensemble sweep across thresholds
│   ├── monthly_stability.csv           # long format
│   └── monthly_stability_wide.csv      # one row per model
└── src/
    ├── lib.py                  # shared utilities (config, model loading, I/O)
    ├── phase1_audit.py
    ├── phase2_stability.py
    ├── phase4_ensemble.py
    └── monthly_stability.py
```

## Inputs required

Before running, place these three things:

1. **Noisy outsample CSV** in `input/`. Generated with pre-v5.6 dGEN over the calendar period 5 May 2025 to 25 May 2026 (or whatever your original outsample period was). Filename should match the pattern in `configs/audit_config.yaml -> paths.noisy_outsample`.

2. **Clean outsample CSV** in `input/`. Generated with post-v5.8 dGEN over the **same calendar period and identical game IDs**. The two files must contain the same set of games — only the feature values differ. The pipeline will raise an error if the game ID sets don't match.

3. **31 LGBM model files** in `models/`, saved as `.pkl` (pickle) or `.joblib`. Each file should contain a single LGBMClassifier instance. The file stem (e.g. `model_017` from `model_017.pkl`) is used as the model identifier throughout the pipeline.

## Outputs

Each phase produces a CSV in `results/`:

### phase1_audit.csv

Per-model contamination categorisation based on feature-importance exposure to affected features. Columns:

| Column | Meaning |
|---|---|
| `model_id` | Filename stem |
| `category` | Clean / Light / Substantial / Heavy |
| `strong_share` | Fraction of total gain importance attributable to strongly-affected features (Pythag, FIP_YTD_HV, WHIP-VHRatios, MenOnBase_Strength) |
| `weak_share` | Same for mildly-affected features (FIP non-HV variants, EarnedRuns) |
| `fip_ythv_imp` | Standalone importance of G_VHRatio_FIP_YTD_HV (specifically tracked because of NaN-routing behaviour change) |
| `top3_affected` | Top three affected features by importance for this model |

### phase2_stability.csv

Per-model empirical diagnostics and KEEP/INVESTIGATE/DEMOTE/RETIRE/KEEP_SUSPECT decision. Columns:

| Column | Meaning |
|---|---|
| `model_id` | Filename stem |
| `status` | Phase 3 decision (see thresholds below) |
| `pred_agreement` | % games with unchanged class prediction |
| `proba_corr` | Pearson corr between probabilities on noisy vs clean |
| `prec_old`, `prec_new`, `prec_delta` | Precision-on-Yes-predictions before/after data fix |
| `n_yes_predicted_old`, `n_yes_predicted_new` | How many games each version of the model wanted to bet Yes |

### combined_audit.csv

Phase 1 + Phase 2 joined by `model_id`. Use this as the single source of truth for per-model decisions.

### phase4_ensemble.csv

Ensemble precision / coverage at each agreement threshold (0.55, 0.60, 0.65, 0.70, 0.75, 0.80) applied to survivors (anyone with status != RETIRE). Use the precision-coverage curve to choose the optimal operating point for clean data.

### monthly_stability.csv (and _wide.csv)

For each survivor, precision computed per calendar month. Look for models with low std across months — that's stable signal vs. regime-dependent noise.

## Interpretation guide

### Phase 1 categories

- **Clean**: model essentially ignored affected features. Expect Phase 2 to confirm KEEP.
- **Light**: modest use of affected features. Likely KEEP or INVESTIGATE in Phase 2.
- **Substantial**: meaningful reliance on affected features. Phase 2 result is the critical signal.
- **Heavy**: substantial reliance on FIP_YTD_HV or aggregate affected features. Likely DEMOTE or RETIRE.

### Phase 2 statuses

- **KEEP**: robust to the data fix. Use as production candidate.
- **KEEP_SUSPECT**: precision improved >3pp on clean data. Counter-intuitive — spot-check 10-20 games for label leakage before celebrating, then keep.
- **INVESTIGATE**: meaningful shift in predictions. Run the per-game analysis from the checklist to decide.
- **DEMOTE**: significant shift but model still functional. Keep as observation candidate; replacement-first priority.
- **RETIRE**: model relied substantially on noise. Discard.

The DEMOTE band is included because the ensemble is **observed-not-traded** in your current workflow — you can afford to keep marginal models for further validation rather than discard them outright. If you ever switch to live trading, tighten the thresholds to discard the DEMOTE tier as well.

### Phase 4 sweep

Look for the agreement threshold that maximises **expected value per bet** rather than raw precision. EV = (precision − breakeven) × n_bets, where breakeven at −110 is 52.38%. Often the optimum is at a moderate threshold (~0.65-0.70) rather than the extremes.

## Configuration

Everything tunable lives in `configs/audit_config.yaml`:

- File paths
- CSV column names (`game_id`, `date`, `target`)
- The 38-feature Scion V26.06 list
- Affected feature classifications (strong / weak)
- Phase 1 categorisation thresholds
- Phase 2 decision thresholds (including the new DEMOTE band)
- Phase 4 ensemble settings

Edit and re-run; nothing else should need changing.

## Notes on assumptions

- Feature ordering: the pipeline uses the explicit feature list from the YAML config (not the model's internal `feature_name()`) for prediction. If your 31 models were trained on a feature subset, make sure the config's `features` list matches what each model actually expects.
- Target column: hard-assumed binary (`0` or `1`). The config's `columns.target` setting points to whichever column holds your home-win label (default `H_Won_F`).
- Missing models / corrupted pickles are logged as warnings rather than fatal errors — the pipeline continues with the models it could load.
- BOM-safe CSV reading: outsample CSVs are read with `utf-8-sig` to handle any upstream BOM corruption (see v5.7 fix history).
