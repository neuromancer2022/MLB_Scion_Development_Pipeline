# MLB Scion Development Pipeline — User Guide

**Version:** V25.08b2 (Standard Edition)  
**Owner:** Perceptronix Ltd © 2025

---

## Table of Contents

1. [Overview and Philosophy](#1-overview-and-philosophy)
2. [Relationship to the Deployment Pipeline](#2-relationship-to-the-deployment-pipeline)
3. [Prerequisites and Setup](#3-prerequisites-and-setup)
4. [Data Files](#4-data-files)
5. [Model Assets](#5-model-assets)
6. [Development Workflow](#6-development-workflow)
7. [Running Experiments](#7-running-experiments)
8. [Backtesting](#8-backtesting)
9. [Evaluating and Comparing Results](#9-evaluating-and-comparing-results)
10. [Promoting to Deployment](#10-promoting-to-deployment)
11. [Notebooks](#11-notebooks)
12. [Git Workflow for Development](#12-git-workflow-for-development)
13. [What Gets Changed Where](#13-what-gets-changed-where)

---

## 1. Overview and Philosophy

The development pipeline exists to keep experimentation completely separate from production operations. The core principle is:

> **Nothing reaches the deployment pipeline without being proven here first.**

In practice this means:

- You change config parameters, tree settings, ensemble composition, and betting strategy thresholds in this repo
- You run backtests here against historical data with known outcomes
- You evaluate ROI, hit rate, and P&L here before committing to anything
- Only when a change demonstrably improves out-of-sample performance do you promote it to the deployment pipeline

This protects your live prediction workflow from being disrupted by experimental changes, and gives you a clean audit trail of what was tested, what the results were, and what decision was made.

---

## 2. Relationship to the Deployment Pipeline

```
mlb-data-pipeline (scraper)
        │
        ▼ mlbprimitives.csv
MLB_Scion_Development_Pipeline
        │
        ├── Experiment 1: agree threshold 0.71 → 0.75   results/backtests/EXP-001/
        ├── Experiment 2: model threshold 0.538 → 0.55  results/backtests/EXP-002/
        ├── Experiment 3: new pkl set from 2024 retrain  results/backtests/EXP-003/
        │
        │  EXP-003 shows +2.1% ROI improvement out-of-sample ✓
        │  make promote
        ▼
MLB_Scion_Deployment_Pipeline
        │
        ▼ git tag v26.01
        Daily predictions
```

Both pipelines share the same source code (`src/`). Changes to the Python source are made here first, tested via backtests, then the updated files are copied to the deployment pipeline's `src/` manually (or via a future sync script) before tagging a release.

---

## 3. Prerequisites and Setup

### Requirements

- Python 3.10+
- pip
- make
- Git
- Jupyter (for notebooks) — installed via `requirements.txt`

### Install

```bash
git clone https://github.com/YOUR_ORG/MLB_Scion_Development_Pipeline.git
cd MLB_Scion_Development_Pipeline
make setup
```

---

## 4. Data Files

### data/sciondata/mlbsciondata.csv

The full historical master database in G_Id format. This is gitignored (~555MB). Place your current copy here:

```
data/sciondata/mlbsciondata.csv
```

### data/mups/mlbmups.csv

The current matchups file for live development runs. Tracked in git.

### data/backtest/

This is the key addition over the deployment pipeline. It holds historical matchup files with **known outcomes** for evaluating model performance.

```
data/backtest/
├── insample/
│   └── mlbmups_insample.csv      ← games from 2004–2023 (model training period)
│   └── actuals_insample.csv      ← actual results for insample games
└── outsample/
    └── mlbmups_outsample.csv     ← games from 2024+ (after training cutoff)
    └── actuals_outsample.csv     ← actual results for outsample games
```

**Backtest mups CSV format** — same as the live mups format (date, team_id, sp_id, bookie_money_line, bookie_vig, bookie_total) but covering historical games.

**Actuals CSV format** — minimum required columns:

```csv
game_id, home_win
20240401_NYY_BOS, 1
20240401_LAD_SFG, 0
```

Where `home_win = 1` means the home team won, `0` means the visitor won.

The distinction between insample and outsample is important:

- **Insample results** tell you how well the model fits its training data. Useful for sanity checks but not a reliable indicator of live performance.
- **Outsample results** are the honest test — games the model has never seen. Always lead with outsample when making promotion decisions.

---

## 5. Model Assets

### Versioned Subfolder Structure

Model assets are stored in **versioned subfolders** under `models/`, using the same naming convention as the deployment pipeline. This ensures you always know which assets correspond to which release, and can reproduce any past run exactly.

```
models/
├── MLB_Scion_CFG.txt          ← git-tracked — always reflects active/baseline config
├── V25_08bSE/                 ← production baseline (copy from deployment pipeline)
│   └── Tepper_Prob/
│       ├── SCI1_M1_MLB_V113_*.pkl   (x99 pkl files)
│       ├── MLB_dGENV25_04_*_STDSTATS_*.csv
│       ├── MLB_Dump_3Year*.json
│       └── MLB_V113_*.csv
└── experiments/
    ├── EXP-001/               ← experimental pkl set for experiment 1
    │   └── Tepper_Prob/
    └── EXP-003_2024retrain/   ← retrained model set
        └── Tepper_Prob/
```

The `V25_08bSE/` folder is a copy of the current production assets from the deployment pipeline. The development pipeline runs against these by default, so dev and deployment are always aligned unless you explicitly point an experiment at a different set.

The `configs/mlb_scion_dev_config.yaml` `system_path` setting controls which version is active:

```yaml
system_path: "models/V25_08bSE"   # baseline
```

For experiments pointing at a new model set:

```yaml
system_path: "models/experiments/EXP-003_2024retrain"
```

### configs/versions/ — Archived CFG files

As in the deployment pipeline, archive `MLB_Scion_CFG.txt` into `configs/versions/` before updating it. These are git-tracked and act as the manifest for each version:

```
configs/versions/
├── V25_08bSE_MLB_Scion_CFG.txt
└── V26_01_MLB_Scion_CFG.txt
```

See `MLB_Scion_DevDeploy_Workflow.docx` for the complete versioning and promotion workflow.

---

## 6. Development Workflow

The typical development cycle looks like this:

### Changing strategy parameters (no new model training needed)

1. Identify the parameter you want to test (e.g., `SYS_PROB_BASE_AGREETHRESH`)
2. Create an experiment config in `configs/experiments/`
3. Run the experiment against out-of-sample backtest data
4. Evaluate results
5. If better: update `models/MLB_Scion_CFG.txt` and promote
6. If not: discard — the baseline CFG.txt is unchanged

### Changing model files (new pkl set from retraining)

1. Place new pkl files in `models/experiments/EXP-003_2024retrain/Tepper_Prob/`
2. Create a matching `MLB_Scion_CFG.txt` variant pointing to the new pks
3. Create an experiment config pointing `system_path` at `models/experiments/EXP-003_2024retrain`
4. Run backtest and evaluate
5. If better: promote new pkls and CFG to deployment

### Changing source code (feature engineering, strategy logic)

1. Create a feature branch: `git checkout -b feature/new-sp-feature`
2. Make changes in `src/`
3. Run dev tests with `make run`
4. Run backtests with `make backtest` + `make evaluate`
5. Merge to `develop` and then follow the Git release process

---

## 7. Running Experiments

### The Experiment Config

Each experiment is defined by a YAML file in `configs/experiments/`. The critical section is `cfg_overrides`, which lists only the parameters that differ from the baseline `models/MLB_Scion_CFG.txt`:

```yaml
experiment:
  id:          "EXP-001"
  description: "PM150 agree threshold 0.71 → 0.75"
  cfg_overrides:
    SYS_PROB_BASE_AGREETHRESH: 0.75     # was 0.71
```

Only list the parameters you are changing. Everything else is read from the CFG.txt as normal. This ensures experiments are isolated to a single variable.

### Running an Experiment

```bash
make experiment EXP=configs/experiments/exp_001_pm150_agreethresh_0.75.yaml
```

Or directly:

```bash
python src/run_experiment.py --config configs/experiments/exp_001_pm150_agreethresh_0.75.yaml
```

### What the Experiment Runner Does

1. Reads the experiment YAML
2. Applies `cfg_overrides` to a temporary patched copy of `MLB_Scion_CFG.txt`
3. Runs Scion with the patched config
4. Saves all output to `results/experiments/<EXP_ID>_<timestamp>/`
5. Saves a copy of the experiment YAML alongside the results for reproducibility
6. Deletes the temporary patched CFG (the source CFG.txt is never modified)

### Experiment Naming Convention

```
exp_<NNN>_<parameter_changed>_<new_value>.yaml
```

Examples:
```
exp_001_pm150_agreethresh_0.75.yaml
exp_002_pm210_modelthresh_0.55.yaml
exp_003_dog_winprice_thresh_minus110.yaml
exp_004_new_pkl_set_2024retrain.yaml
```

The experiment `id` in the YAML should match the filename prefix (`EXP-001`, `EXP-002`, etc.) for easy cross-referencing.

---

## 8. Backtesting

Backtesting runs Scion against a historical matchups file where outcomes are already known, so you can score the predictions objectively.

### Run a Backtest

```bash
make backtest
```

This uses `configs/mlb_scion_backtest_config.yaml`, which points at `data/backtest/outsample/mlbmups_backtest.csv` by default. Edit the config to switch between insample and outsample, or to point at a specific season's data.

To run a specific experiment as a backtest (most common use case):

```bash
make experiment EXP=configs/experiments/exp_001_pm150_agreethresh_0.75.yaml
```

The experiment config's `mups_file` should point at the backtest data:

```yaml
input:
  mups_file: "data/backtest/outsample/mlbmups_backtest.csv"
```

### Building Your Backtest Mups Files

Your backtest mups files should use exactly the same format as live `mlbmups.csv` files, just covering historical games. Build these from your `mlbsciondata.csv` master by extracting the relevant columns for games you want to evaluate. The key fields Scion needs are: date, home team id, visitor team id, home SP id, visitor SP id, bookie money line, bookie vig, and bookie total.

---

## 9. Evaluating and Comparing Results

### Evaluate a Backtest

After running a backtest, score the predictions against actuals:

```bash
make evaluate \
  PREDS="results/experiments/EXP-001_20251001_120000/MLB_Scion_SUMMARY_*.csv" \
  ACTUALS=data/backtest/outsample/actuals_outsample.csv \
  EVAL_OUT=results/backtests/EXP-001_eval.csv
```

The evaluator reports for each ensemble (PM210, PM150) and the combined Scion side call:

- Total plays, wins, losses
- Hit rate (%)
- Total P&L in units (at actual bookie prices)
- ROI (%)
- Breakdown by play type (HomFave, HomDog, VisFave, VisDog)

### Compare Multiple Experiments

Once you have eval CSVs for two or more experiments:

```bash
make compare \
  COMPARE_CSVS="results/backtests/EXP-001_eval.csv results/backtests/EXP-002_eval.csv"
```

This prints a side-by-side table with deltas vs the baseline experiment, making it easy to see at a glance whether a change helped or hurt.

### Interpreting Results

When deciding whether to promote an experiment:

- **Outsample ROI improvement** is the primary signal. Even a small consistent improvement (+0.5% ROI) over a large sample is meaningful.
- **Hit rate** alone is not enough — a higher hit rate at worse prices can still reduce ROI.
- **Fewer plays at higher ROI** is often preferable to more plays at lower ROI.
- **Insample improvement without outsample improvement** is overfitting — do not promote.
- Always test against at least one full season of outsample data before promoting.

---

## 10. Promoting to Deployment

When an experiment has proven itself out-of-sample and you're ready to take it live:

### Step 1 — Update models/MLB_Scion_CFG.txt

Apply the winning parameters from your experiment to the tracked CFG.txt:

```bash
# Edit models/MLB_Scion_CFG.txt directly, changing the proven parameters
# e.g. SYS_PROB_BASE_AGREETHRESH = 0.75
```

Commit this change on a feature branch:

```bash
git checkout -b feature/promote-exp001-agreethresh
git add models/MLB_Scion_CFG.txt
git commit -m "feat: raise PM150 agree threshold to 0.75 (EXP-001, +1.2% ROI outsample)"
```

### Step 2 — Dry run the promotion

```bash
make promote-dry DEPLOY_REPO=../MLB_Scion_Deployment_Pipeline
```

Review the output — it shows exactly what files will be copied without touching anything.

### Step 3 — Promote

```bash
make promote DEPLOY_REPO=../MLB_Scion_Deployment_Pipeline
```

This copies `models/MLB_Scion_CFG.txt` (and any experimental pkl files if specified) to the deployment pipeline's `models/` directory.

### Step 4 — Tag and release in the deployment pipeline

```bash
cd ../MLB_Scion_Deployment_Pipeline
git add models/
git commit -m "chore: promote EXP-001 — PM150 agree threshold 0.75"
git tag -a v26.01 -m "Release v26.01 — improved PM150 agreement threshold"
git push origin main --tags
```

### Step 5 — Merge back into develop here

```bash
cd ../MLB_Scion_Development_Pipeline
git checkout develop
git merge --no-ff feature/promote-exp001-agreethresh
git push origin develop
```

---

## 11. Notebooks

The `notebooks/` folder is for Jupyter-based exploratory analysis. Some suggested notebooks to create:

- `01_data_exploration.ipynb` — explore mlbsciondata.csv, feature distributions, team statistics
- `02_prediction_analysis.ipynb` — analyse prediction output, vote agreement distributions, play frequency by team/month
- `03_backtest_deep_dive.ipynb` — detailed breakdown of a backtest result beyond what evaluate_backtest.py provides
- `04_strategy_sensitivity.ipynb` — sweep a parameter across a range and plot ROI vs parameter value

Start Jupyter from the repo root:

```bash
jupyter notebook
```

All notebooks should be checked in to git (without output cells cleared for cleanliness — use `jupyter nbconvert --clear-output` before committing).

---

## 12. Git Workflow for Development

The development pipeline uses the same branching strategy as the deployment pipeline (see that repo's USER_GUIDE for full details), with one addition — experiment tracking.

### Branch for an Experiment

Each significant experiment that involves source code changes should have its own branch:

```bash
git checkout -b experiment/exp-001-agreethresh develop
# ... make changes, run experiment ...
git commit -m "experiment: EXP-001 PM150 agree threshold 0.75 — +1.2% ROI outsample"
```

If the experiment is successful, merge it to `develop` and eventually to a release. If not, the branch is simply abandoned (don't delete it — keep it for the record).

### Committing Experiment Configs

Every experiment YAML in `configs/experiments/` should be committed to git immediately when created, before you run it. This ensures you always have a record of what was tested even if the results were discarded.

```bash
git add configs/experiments/exp_001_pm150_agreethresh_0.75.yaml
git commit -m "experiment: add EXP-001 config — PM150 agree threshold test"
```

### What NOT to Commit

- `results/` — all gitignored; results are local artefacts
- `data/sciondata/mlbsciondata.csv` — gitignored; too large
- `models/V25_08bSE/*.pkl`, `models/experiments/**/*.pkl` etc. — gitignored; binary/large
- Notebook output cells — clear before committing

### What to ALWAYS Commit

- All experiment YAML configs in `configs/experiments/`
- Updated `models/MLB_Scion_CFG.txt` when a parameter change is proven
- Archived CFG files in `configs/versions/` before each version update
- Any source code changes in `src/`
- Updated `data/mups/mlbmups.csv` when the matchups change

---

## 13. What Gets Changed Where

A quick reference for where each type of change belongs:

| What you're changing | Where | Notes |
|---|---|---|
| Model probability thresholds | `configs/experiments/` YAML → `models/MLB_Scion_CFG.txt` | Test via experiment first |
| Agreement thresholds | `configs/experiments/` YAML → `models/MLB_Scion_CFG.txt` | Test via experiment first |
| Betting strategy logic | `src/MLB_Scion.py` | Branch, backtest, then merge |
| Feature engineering | `src/MLB_Scion_dGEN.py` | Branch, backtest, then merge |
| New pkl model files | `models/experiments/EXP-NNN/` → `models/V26_01/` after validation | gitignored, copy manually |
| Number of ensemble models | `models/MLB_Scion_CFG.txt` | Edit directly or via experiment override |
| Confidence base values (HF/HD/VF/VD) | `configs/experiments/` YAML → `models/MLB_Scion_CFG.txt` | Test via experiment first |
| Daily mups for live dev test | `data/mups/mlbmups.csv` | Committed to git |
| Historical backtest mups | `data/backtest/` | Gitignored (large), place manually |
