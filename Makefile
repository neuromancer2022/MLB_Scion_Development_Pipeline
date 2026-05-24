# =============================================================
# MLB Scion Deployment Pipeline — Makefile
# =============================================================
# Targets:
#   make all            – full pipeline: scion_data → scion_predict
#   make scion_data     – Step 1: primitives → sciondata (MLB dBASE)
#   make scion_predict  – Step 2: sciondata + mups → predictions (MLB Scion)
#   make setup          – install Python dependencies
#   make clean          – remove generated output files
#   make help           – show this message
# =============================================================

PYTHON      ?= python3
DBASE_CFG   ?= configs/mlb_dbase_config.yaml
SCION_CFG   ?= configs/mlb_scion_config.yaml

.PHONY: all scion_data scion_predict setup clean help

## ---- Default target: run the full pipeline -----------------
all: scion_data scion_predict

## ---- Step 1: Process primitives → sciondata ----------------
scion_data:
	@echo "=== [1/2] Running MLB dBASE (primitives → sciondata) ==="
	$(PYTHON) src/run_dbase.py --config $(DBASE_CFG)

## ---- Step 2: Run Scion predictions -------------------------
scion_predict:
	@echo "=== [2/2] Running MLB Scion (sciondata + mups → predictions) ==="
	$(PYTHON) src/run_scion.py --config $(SCION_CFG)

## ---- Install dependencies ----------------------------------
setup:
	@echo "=== Installing Python dependencies ==="
	$(PYTHON) -m pip install -r requirements.txt

## ---- Remove generated outputs ------------------------------
clean:
	@echo "=== Cleaning generated output files ==="
	find results/predictions -type f ! -name ".gitkeep" -delete
	find results/logs        -type f ! -name ".gitkeep" -delete
	find results/tempfiles   -type f ! -name ".gitkeep" -delete
	find data/sciondata      -type f ! -name ".gitkeep" -delete
	@echo "Done."

## ---- Help --------------------------------------------------
help:
	@echo ""
	@echo "MLB Scion Deployment Pipeline"
	@echo "------------------------------"
	@echo "  make all            Full pipeline (dBASE → Scion)"
	@echo "  make scion_data     Step 1 only: process primitives"
	@echo "  make scion_predict  Step 2 only: run predictions"
	@echo "  make setup          Install Python requirements"
	@echo "  make clean          Remove generated output files"
	@echo ""
	@echo "Override defaults:"
	@echo "  make scion_data DBASE_CFG=path/to/config.yaml"
	@echo "  make scion_predict SCION_CFG=path/to/config.yaml"
	@echo ""
