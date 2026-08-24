# MLB Scion Deployment Pipeline — User Guide

**Version:** V25.08b2 (Standard Edition)  
**Owner:** Perceptronix Ltd © 2025

---

## Table of Contents

1. [Overview](#1-overview)
2. [System Architecture](#2-system-architecture)
3. [Prerequisites](#3-prerequisites)
4. [Installation & Setup](#4-installation--setup)
5. [Data Files](#5-data-files)
6. [Model Assets](#6-model-assets)
7. [Configuration Reference](#7-configuration-reference)
8. [Running the Pipeline](#8-running-the-pipeline)
9. [Output Files](#9-output-files)
10. [GitHub Actions (Online Execution)](#10-github-actions-online-execution)
11. [Git Workflow — Branching, Merging & Releases](#11-git-workflow--branching-merging--releases)
12. [Pulling a Full Release](#12-pulling-a-full-release)
13. [Troubleshooting](#13-troubleshooting)

---

## 1. Overview

The **MLB Scion Deployment Pipeline** is the operational prediction system for MLB games. It sits downstream of the `mlb-data-pipeline` scraper repository and consists of two sequential stages:

```
mlb-data-pipeline (separate repo)
        │
        ▼  mlbprimitives.csv
┌───────────────────────┐
│   Stage 1: MLB dBASE  │  Transforms raw primitives into the Scion feature set
└───────────────────────┘
        │
        ▼  mlbsciondata.csv
┌───────────────────────┐    ◄── mlbmups.csv (today's matchups)
│   Stage 2: MLB Scion  │  Runs 99 LightGBM ensemble models, produces predictions
└───────────────────────┘
        │
        ▼  Prediction files (timestamped CSV/TXT)
```

**MLB dBASE** (`MLB_dBASE.py`) reads `mlbprimitives.csv` — the raw scraped game database — and maps every record to the Scion V113 feature set, producing `mlbsciondata.csv`. This is the historical context the models need.

**MLB Scion** (`MLB_Scion.py`) reads `mlbsciondata.csv` plus `mlbmups.csv` (the list of upcoming games with bookie lines), loads 99 trained LightGBM classifier `.pkl` files from the `models/` directory, applies standardisation and feature engineering, runs ensemble voting, and writes time-stamped prediction files to `results/predictions/`.

---

## 2. System Architecture

### Pipeline Components

| Component | File | Role |
|---|---|---|
| dBASE Core | `src/MLB_dBASE.py` | Primitives → sciondata mapping engine |
| dBASE Globals | `src/MLB_globals.py` | Constants, date utilities |
| Shared Variables | `src/MLB_dbvar.py` | Database variable definitions (shared) |
| Scion Core | `src/MLB_Scion.py` | Main prediction orchestrator |
| Scion Globals | `src/MLB_Scion_Globals.py` | App version, folder names, system path |
| Config Parser | `src/MLB_Scion_Cfg.py` | Parses `MLB_Scion_CFG.txt` into settings object |
| Prediction Engine | `src/MLB_Scion_Preds.py` | Applies ensemble voting and generates output |
| Feature Generator | `src/MLB_Scion_dGEN.py` | Generates model input features per game |
| Data Transformer | `src/MLB_Scion_dTrans.py` | Scales and prepares data for models |
| Matchup Handler | `src/MLB_Scion_Mups.py` | Loads and validates `mlbmups.csv` |
| Master DB Handler | `src/MLB_Scion_MasterDB.py` | Loads and queries `mlbsciondata.csv` |
| Attribute Stats | `src/AttribStats.py` | Attribute-level standardisation stats |
| dBASE Wrapper | `src/run_dbase.py` | Reads YAML config, calls `MLB_dBASE.py` |
| Scion Wrapper | `src/run_scion.py` | Reads YAML config, calls `MLB_Scion.py` |

### Directory Layout

```
MLB_Scion_Deployment_Pipeline/
├── src/                    All Python source
├── configs/                YAML pipeline configs + CFG.txt example
├── data/
│   ├── primitives/         Input: mlbprimitives.csv (gitignored)
│   ├── sciondata/          Generated: mlbsciondata.csv (gitignored)
│   └── mups/               Input: mlbmups.csv
├── models/                 Gitignored: pkl, JSON lookups, CSV stats
├── results/
│   ├── predictions/        Output: timestamped prediction files
│   ├── logs/               Output: detailed processing logs
│   └── tempfiles/          Output: intermediate test pattern files
└── .github/workflows/      GitHub Actions CI/CD
```

---

## 3. Prerequisites

- **Python 3.10 or higher**
- **pip** package manager
- **make** (standard on macOS and Linux; on Windows use WSL or Git Bash)
- **Git** (for version control workflow)
- The trained model assets directory (`models/`). See [Section 6](#6-model-assets).

---

## 4. Installation & Setup

### Clone the Repository

```bash
git clone https://github.com/YOUR_ORG/MLB_Scion_Deployment_Pipeline.git
cd MLB_Scion_Deployment_Pipeline
```

### Install Python Dependencies

```bash
make setup
```

This is equivalent to:

```bash
pip install -r requirements.txt
```

Key dependencies include `pandas`, `numpy`, `lightgbm`, `xgboost`, `scikit-learn`, `statsmodels`, `joblib`, and `pyyaml`.

---

## 5. Data Files

### How MLB dBASE uses its three files

`MLB_dBASE` is an **incremental update tool**, not a from-scratch converter. It merges new games from the raw scraper dump into the existing master database and writes out an updated master. It requires three distinct files every run:

| Argument | File | Description |
|---|---|---|
| `usrMasterDB_Fname` | `mlbsciondata.csv` | **Existing** master in G_Id format (1166 columns). Must already exist. |
| `usrDump_Fname` | `mlbprimitives.csv` | Raw scraper output in `game_id`/`date` format. New games to be merged in. |
| `usrResults_Fname` | `mlbsciondata.csv` | Output path for the updated master. Typically the same as the input master (overwrites it). |

### mlbsciondata.csv (master database)

The historical master database in G_Id format (1166 columns), produced and maintained by MLB dBASE. Place your current copy at:

```
data/sciondata/mlbsciondata.csv
```

This file is **gitignored** due to its size (~555MB). You must supply it manually on each deployment machine. It is the primary input to both MLB dBASE (as the master to update) and MLB Scion (as the historical context for feature generation).

### mlbprimitives.csv

The raw game dump produced by the `mlb-data-pipeline` scraper. Place it at:

```
data/primitives/mlbprimitives.csv
```

This file is also **gitignored** (large, regenerated by the scraper). It uses the raw column format (`game_id`, `date`, etc.) defined in `MLB_dumpvar.py`. MLB dBASE reads this and merges any new game records into the master.

### mlbmups.csv

The matchups file for today's games to be predicted. Place it at:

```
data/mups/mlbmups.csv
```

**Format** — comma-separated with the following columns:

```
date, team_id, starting_pitcher_id, bookie_money_line, bookie_vig, bookie_total
```

Example:

```csv
2025-09-30,NYY,123456,-145,0.091,8.5
2025-09-30,BOS,789012,+125,0.091,8.5
```

This file **is** tracked in git (it is small and changes daily during the season).

---

## 6. Model Assets

The `models/` directory is **gitignored** because it contains large binary files. You must populate it manually before running MLB Scion. Copy the contents of your `MLBScionV25_08bSE/` working directory into `models/`:

### Required Files in models/

| File type | Example filename | Purpose |
|---|---|---|
| Master config | `MLB_Scion_CFG.txt` | Parsed by `MLB_Scion_Cfg.py`; defines all model entries |
| pkl models (x99) | `SCI1_M1_MLB_V113_B1_pm150_*.pkl` | Trained LightGBM classifiers |
| Standardisation stats | `MLB_dGENV25_04_pm150_*_STDSTATS_*.csv` | Feature scaling statistics |
| Park impact factors | `MLB_Dump_3YearParkImpactFactors_*.json` | Ballpark adjustment factors |
| Pitcher averages | `MLB_Dump_3YearSPTeamAVGS_*.json` | Starting pitcher team averages |
| Feature select mask | `MLB_V113_ScionFeatureSelect_Mask.csv` | Feature selection mask |
| dPREP mask | `MLB_V113_Scion_dPREP_Mask.csv` | Categorical variable preparation mask |
| Categ variables | `MLB_CategVariables_21Jun22.json` | Categorical variable lookup |

A fully annotated example config is provided at `configs/MLB_Scion_CFG.txt.example`. Copy and rename it:

```bash
cp configs/MLB_Scion_CFG.txt.example models/MLB_Scion_CFG.txt
```

Then edit `models/MLB_Scion_CFG.txt` to confirm all filenames match the assets you have placed in `models/`.

---

## 7. Configuration Reference

### configs/mlb_dbase_config.yaml

```yaml
input:
  primitives_file: "data/primitives/mlbprimitives.csv"
  comma_delimited: true       # true = CSV, false = TSV

output:
  sciondata_file: "data/sciondata/mlbsciondata.csv"
```

All paths are relative to the repository root.

### configs/mlb_scion_config.yaml

```yaml
system_path: "models/"          # Where pkl files and CFG.txt live
config_fname: "MLB_Scion_CFG.txt"

input:
  sciondata_file: "data/sciondata/mlbsciondata.csv"
  mups_file:      "data/mups/mlbmups.csv"

output:
  predictions_dir: "results/predictions"
  logs_dir:        "results/logs"
  tempfiles_dir:   "results/tempfiles"
```

### models/MLB_Scion_CFG.txt

This file is parsed by `MLB_Scion_Cfg.py`. It contains system-level thresholds and a numbered list of up to 99 model entries. Key system parameters:

| Parameter | Description |
|---|---|
| `SYS_RUN_MODELS` | Number of models to run (0 = all) |
| `SYS_PROB_MODELTHRESH` | Minimum probability threshold for a prediction signal |
| `SYS_PROB_AVG_AGREEMAJVOTE` | Whether to use average probability or majority vote |
| `SYS_PROB_BASE_AGREETHRESH` | Agreement threshold for the PM150 ensemble |
| `SYS_PROB_PM210_AGREETHRESH` | Agreement threshold for the PM210 ensemble |
| `SYS_STRENGTH_STATS_FNAME` | Standardisation stats CSV (shared across all models) |
| `TPROB_TASK_MODEL_CODE{N}` | Unique identifier for model N |
| `TPROB_TASK_MODEL_CFG_FNAME{N}` | pkl filename for model N |
| `TPROB_TASK_MODEL_IP_VARSTATS_FNAME{N}` | Input standardisation stats for model N |
| `TPROB_TASK_MODEL_OP_RESULT_FNAME{N}` | Output prediction text file for model N |

---

## 8. Running the Pipeline

### Full Pipeline (recommended for daily prediction runs)

```bash
make all
```

This runs dBASE first, then Scion. If `mlbsciondata.csv` already exists and is up to date, you can skip straight to Step 2.

### Step 1 Only — Process Primitives

```bash
make scion_data
```

Use this when you have a fresh `mlbprimitives.csv` from the scraper and need to rebuild `mlbsciondata.csv`.

### Step 2 Only — Run Predictions

```bash
make scion_predict
```

Use this when `mlbsciondata.csv` is already current and you only need to run predictions for a new set of matchups.

### Running Directly with Python

```bash
python src/run_dbase.py --config configs/mlb_dbase_config.yaml
python src/run_scion.py --config configs/mlb_scion_config.yaml
```

### Using a Custom Config

```bash
make scion_data DBASE_CFG=configs/my_custom_dbase.yaml
make scion_predict SCION_CFG=configs/my_custom_scion.yaml
```

### Clean Generated Files

```bash
make clean
```

This removes all files in `results/` and `data/sciondata/` while preserving `.gitkeep` placeholders.

---

## 9. Output Files

### Output Folder Structure

All output is written to `results/` as configured in `configs/mlb_scion_config.yaml`. The folder structure after a run is:

```
results/
├── predictions/
│   ├── MLB_ScionV25_08b2SE_<user>_VERBOSE_<timestamp>.csv    ← full per-game detail
│   ├── MLB_ScionV25_08b2SE_<user>_SUMMARY_<timestamp>.csv    ← canonical output (read this)
│   ├── MLB_ScionV25_08b2SE_<user>_ePLAYS_<timestamp>.txt
│   ├── MLB_ScionV25_08b2SE_<user>_iPLAYS_<timestamp>.txt
│   ├── MLB_ScionV25_08b2SE_<user>_iPOS_<timestamp>.txt
│   ├── MLB_ScionV25_08b2SE_<user>_iPOSML_<timestamp>.txt
│   │
│   ├── MLB_ScionV25_08b2SE_<user>_SUMMARY.csv     ← non-timestamped copy (latest run)
│   ├── MLB_ScionV25_08b2SE_<user>_iPLAYS.txt
│   ├── MLB_ScionV25_08b2SE_<user>_iPOS.txt
│   ├── MLB_ScionV25_08b2SE_<user>_iPOSML.txt
│   └── MLB_ScionV25_08b2SE_<user>_ePLAYS.txt
└── logs/
    └── .logs<YYYYMMDD>/
        └── (per-game team log files)
```

The **SUMMARY CSV** is the primary output you read after each run — it contains one row per game with the ensemble positions, probabilities, and the final Scion side call. The timestamped files are archived copies; the non-timestamped files are always the latest run.

The `results/tempfiles/` directory holds intermediate test pattern files created during model execution (e.g. `MLB_Scion_DT_TestPattern.csv`). These are safe to delete between runs.

All files under `results/` are gitignored.

---

## 10. GitHub Actions (Online Execution)

The pipeline is configured for GitHub Actions in `.github/workflows/mlb_scion_pipeline.yml`.

### Manual Trigger

1. Go to your repository on GitHub.
2. Click **Actions** → **MLB Scion Pipeline**.
3. Click **Run workflow**.
4. Choose whether to run dBASE, Scion, or both.
5. Click **Run workflow** to confirm.

Prediction files are automatically uploaded as **workflow artifacts** and are available for download from the Actions run page for 30 days.

### Supplying Data and Models to GitHub Actions

Because `models/`, `data/primitives/`, and large CSVs are gitignored, you need to supply them to the runner. Two approaches:

**Option A — GitHub Secrets (small files only, < 64KB)**

Encode files to base64 and store them as GitHub Secrets:

```bash
base64 -i data/mups/mlbmups.csv | pbcopy   # macOS
```

Add the result as a secret named `MUPS_B64`. Then in the workflow:

```yaml
- name: Restore mups
  run: echo "${{ secrets.MUPS_B64 }}" | base64 -d > data/mups/mlbmups.csv
```

**Option B — External Object Storage (recommended for large files)**

Store `mlbprimitives.csv` and the `models/` tarball in an S3 bucket or similar. Use the AWS CLI action or `curl` in the workflow to download them before running the pipeline.

### Scheduling

To run automatically at the start of each MLB game day, uncomment the `schedule` section in the workflow YAML:

```yaml
schedule:
  - cron: "30 11 * 4-10 *"   # 11:30 UTC daily, April–October
```

---

## 11. Git Workflow — Branching, Merging & Releases

This section describes the recommended Git workflow for managing code changes, model updates, and versioned releases.

### Branch Strategy

```
main            ← stable, production-ready code only
develop         ← integration branch for all feature work
feature/*       ← individual feature branches
hotfix/*        ← emergency fixes to main
release/vX.Y.Z  ← release preparation branches
```

### Starting New Work

Always branch from `develop`, never from `main`:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/update-scion-cfg-parser
```

### Making Commits

Write clear, imperative commit messages:

```bash
git add src/MLB_Scion_Cfg.py configs/mlb_scion_config.yaml
git commit -m "feat: migrate Scion config to YAML; preserve CFG.txt backward compat"
```

Commit message prefixes:
- `feat:` — new feature
- `fix:` — bug fix
- `refactor:` — code restructuring (no behaviour change)
- `chore:` — maintenance (deps, config, gitignore)
- `docs:` — documentation only
- `data:` — data file updates (mups, primitives)

### Merging Feature Work into Develop

```bash
git checkout develop
git pull origin develop
git merge --no-ff feature/update-scion-cfg-parser
git push origin develop
git branch -d feature/update-scion-cfg-parser
```

Using `--no-ff` (no fast-forward) preserves a merge commit so the branch history is visible in the log.

### Preparing a Release

When `develop` is stable and ready for release:

```bash
git checkout -b release/v25.08b2 develop
```

On this branch you should:
- Update version strings in `src/MLB_Scion_Globals.py` (e.g., `APP_VER`)
- Update `README.md` and `USER_GUIDE.md`
- Do final testing

Then merge into both `main` and `develop`:

```bash
# Merge into main
git checkout main
git merge --no-ff release/v25.08b2
git push origin main

# Tag the release
git tag -a v25.08b2 -m "Release v25.08b2 - Standard Edition, 99-model ensemble"
git push origin v25.08b2

# Merge back into develop
git checkout develop
git merge --no-ff release/v25.08b2
git push origin develop

# Delete the release branch
git branch -d release/v25.08b2
```

### Hotfixes

For urgent fixes to production (`main`):

```bash
git checkout -b hotfix/fix-scion-cfg-path main
# ... make fixes ...
git commit -m "fix: correct SYSTEM_PATH resolution in run_scion.py"

# Merge into main and tag
git checkout main
git merge --no-ff hotfix/fix-scion-cfg-path
git tag -a v25.08b2.1 -m "Hotfix: SYSTEM_PATH resolution"
git push origin main
git push origin v25.08b2.1

# Merge back into develop
git checkout develop
git merge --no-ff hotfix/fix-scion-cfg-path
git push origin develop

git branch -d hotfix/fix-scion-cfg-path
```

### Tagging Conventions

Use annotated tags (not lightweight tags) for all releases. Annotated tags carry metadata (tagger, date, message) and are the correct form for release references.

```bash
git tag -a v25.08b2    -m "Release v25.08b2 SE — 99-model ensemble, YAML config"
git tag -a v25.09a1    -m "Pre-release v25.09a1 — new pitcher feature set"
git tag -a v26.01      -m "Release v26.01 — 2026 season model refresh"
```

List all tags:

```bash
git tag -l
git tag -l "v25.*"   # Filter by pattern
```

Show tag details:

```bash
git show v25.08b2
```

---

## 12. Pulling a Full Release

To pull a specific tagged release to a fresh machine (e.g., deploying to a new server):

### Step 1 — Clone the repository

```bash
git clone https://github.com/YOUR_ORG/MLB_Scion_Deployment_Pipeline.git
cd MLB_Scion_Deployment_Pipeline
```

### Step 2 — Check out the specific release tag

```bash
git fetch --tags
git checkout tags/v25.08b2 -b release-v25.08b2
```

This creates a local branch `release-v25.08b2` pinned to that exact tagged commit. You are now running an exact, reproducible snapshot of the code for that release.

### Step 3 — Verify the release

```bash
git log --oneline -5
git describe --tags
```

### Step 4 — Install dependencies for that release

```bash
pip install -r requirements.txt
```

### Step 5 — Restore model assets

Copy or download your `models/` directory for the matching model version. The config file `models/MLB_Scion_CFG.txt` must reference the correct `.pkl` filenames for this release.

### Step 6 — Place data files

```
data/primitives/mlbprimitives.csv
data/mups/mlbmups.csv
```

### Step 7 — Run the pipeline

```bash
make all
```

### Updating to a Newer Release

```bash
git fetch --tags
git checkout main
git pull origin main
```

Or to jump to a specific new tag:

```bash
git fetch --tags
git checkout tags/v26.01 -b release-v26.01
pip install -r requirements.txt   # re-install in case deps changed
```

---

## 13. Troubleshooting

### Config file not found

```
[run_scion] ERROR: Config file not found: configs/mlb_scion_config.yaml
```

Ensure you are running from the repository root, not from inside `src/`. All `make` commands automatically run from the repo root.

### Models directory is empty

```
FileNotFoundError: [Errno 2] No such file or directory: 'models/MLB_Scion_CFG.txt'
```

You need to populate the `models/` directory with your pkl files and `MLB_Scion_CFG.txt`. See [Section 6](#6-model-assets).

### mlbprimitives.csv not found

```
FileNotFoundError: data/primitives/mlbprimitives.csv
```

The primitives file must be placed manually (it comes from the `mlb-data-pipeline` scraper). Copy it to `data/primitives/mlbprimitives.csv`.

### mlbsciondata.csv not found when running Scion

Run `make scion_data` first to generate it from primitives, or copy an existing `mlbsciondata.csv` to `data/sciondata/`.

### Module import errors

```
ModuleNotFoundError: No module named 'lightgbm'
```

Run `make setup` or `pip install -r requirements.txt`.

### Python version errors

The pipeline requires Python 3.10+. Check your version:

```bash
python3 --version
```

If needed, specify an explicit interpreter:

```bash
make all PYTHON=python3.11
```

### Reverting to a previous working state

If a recent change broke the pipeline, revert to the last known good tag:

```bash
git stash                       # save any uncommitted local changes
git checkout tags/v25.08b2      # go back to the last good release
```

Or, if you want to permanently undo the last commit on your branch:

```bash
git revert HEAD                 # creates a new revert commit (safe)
```

Never use `git reset --hard` on shared branches (`main`, `develop`).
