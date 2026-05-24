# MLB Scion Deployment Pipeline

**Version:** V25.08b2 (Standard Edition)  
**Owner:** Perceptronix Ltd © 2025

A professional deployment repository for the **MLB Scion** MLB game prediction system, comprising two pipeline stages:

1. **MLB dBASE** — maps raw scraped primitives (`mlbprimitives.csv`) to the Scion feature set (`mlbsciondata.csv`)
2. **MLB Scion** — runs the ensemble LightGBM classifier models against live matchup data (`mlbmups.csv`) to produce time-stamped prediction files

---

## Repository Structure

```
MLB_Scion_Deployment_Pipeline/
├── src/                        # All Python source code
│   ├── MLB_dBASE.py            # dBASE core (primitives → sciondata)
│   ├── MLB_globals.py          # dBASE globals
│   ├── MLB_dbvar.py            # Shared variable definitions
│   ├── MLB_Scion.py            # Scion core (predictions)
│   ├── MLB_Scion_Globals.py    # Scion global constants
│   ├── MLB_Scion_Cfg.py        # Scion config parser
│   ├── MLB_Scion_Preds.py      # Prediction engine
│   ├── MLB_Scion_dGEN.py       # Feature generation
│   ├── MLB_Scion_dTrans.py     # Data transformation
│   ├── MLB_Scion_Mups.py       # Matchup (MUPs) handler
│   ├── MLB_Scion_MasterDB.py   # Master database handler
│   ├── AttribStats.py          # Attribute statistics
│   ├── run_dbase.py            # YAML-driven wrapper for MLB_dBASE
│   └── run_scion.py            # YAML-driven wrapper for MLB_Scion
├── configs/
│   ├── mlb_dbase_config.yaml   # dBASE pipeline configuration
│   └── mlb_scion_config.yaml   # Scion pipeline configuration
├── data/
│   ├── primitives/             # Place mlbprimitives.csv here
│   ├── sciondata/              # mlbsciondata.csv is generated here
│   └── mups/                   # Place mlbmups.csv here
├── models/                     # ⚠ GITIGNORED — place pkl, JSON, CSV assets here
├── results/
│   ├── predictions/            # Timestamped prediction output files
│   ├── logs/                   # Detailed processing logs
│   └── tempfiles/              # Intermediate files during model testing
├── .github/workflows/
│   └── mlb_scion_pipeline.yml  # GitHub Actions CI/CD workflow
├── Makefile                    # Make targets for pipeline execution
├── requirements.txt            # Python dependencies
└── USER_GUIDE.md               # Full usage and Git workflow guide
```

---

## Quick Start

### 1. Install dependencies

```bash
make setup
# or: pip install -r requirements.txt
```

### 2. Place your data files

```
data/sciondata/mlbsciondata.csv     ← your current master DB (G_Id format, 1166 cols)
data/primitives/mlbprimitives.csv   ← latest dump from mlb-data-pipeline scraper
data/mups/mlbmups.csv               ← today's matchups to predict
```

> **How dBASE works:** `MLB_dBASE` merges new games from `mlbprimitives.csv` (raw scraper format) into the existing `mlbsciondata.csv` master (G_Id format), and writes the updated master back out. Both input files must exist before running `make scion_data`.

### 3. Place your model assets

The `models/` directory already contains `MLB_Scion_CFG.txt` (tracked in git). You need to add the binary model assets which are gitignored due to their size:

```
models/
├── MLB_Scion_CFG.txt               ← already present (tracked in git)
├── SCI1_M1_MLB_V113_*.pkl          ← pkl model files (x99) — ADD THESE
├── MLB_dGENV25_04_*.csv            ← standardisation stats files — ADD THESE
├── MLB_Dump_3Year*.json            ← park impact factors + pitcher averages — ADD THESE
└── MLB_V113_*.csv                  ← feature select and prep masks — ADD THESE
```

### 4. Run the full pipeline

```bash
make all
```

Or run each stage independently:

```bash
make scion_data      # Step 1: primitives → sciondata
make scion_predict   # Step 2: predictions
```

After `make scion_predict`, output appears in `results/` (gitignored):

```
results/predictions/         ← SUMMARY CSV, iPLAYS, iPOS, ePLAYS (timestamped + latest)
results/logs/                ← per-game team log files
results/tempfiles/           ← intermediate test pattern files
```

The `results/predictions/MLB_Scion*_SUMMARY_*.csv` file is the canonical output to read after each run.

---

## Make Targets

| Target | Description |
|---|---|
| `make all` | Full pipeline: dBASE then Scion |
| `make scion_data` | Step 1 only — process primitives |
| `make scion_predict` | Step 2 only — run predictions |
| `make setup` | Install Python requirements |
| `make clean` | Remove all generated output files |
| `make help` | Show help message |

---

## Configuration

All paths and settings are controlled through YAML files in `configs/`.  
Edit `configs/mlb_dbase_config.yaml` and `configs/mlb_scion_config.yaml` — you should not need to modify any Python source files for deployment.

See [USER_GUIDE.md](USER_GUIDE.md) for full configuration reference and Git workflow guidance.

---

## GitHub Actions

The pipeline can run on GitHub Actions via a manual trigger (`workflow_dispatch`) or on a schedule. See `.github/workflows/mlb_scion_pipeline.yml`.

> **Note:** Model asset files (`.pkl`, `.json`, `.csv` stats) are too large for the repo. For GitHub Actions runs, supply them via GitHub Secrets or an external object store. See the workflow YAML for instructions.

---

## Related Repositories

| Repo | Purpose |
|---|---|
| `mlb-data-pipeline` | Data scraping → produces `mlbprimitives.csv` |
| `MLB_Scion_Deployment_Pipeline` | **This repo** — dBASE + Scion prediction |
