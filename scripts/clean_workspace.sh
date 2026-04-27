#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "[SceneMill] Removing Python caches and local temp files"
find . -type d -name "__pycache__" -prune -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
rm -rf .pytest_cache .mypy_cache .ruff_cache tmp/*

if [[ "${SCENEMILL_CLEAN_RUNS:-0}" == "1" ]]; then
  echo "[SceneMill] Removing run outputs under runs/"
  find runs -mindepth 1 ! -name ".gitkeep" -exec rm -rf {} +
else
  echo "[SceneMill] Keeping runs/. Set SCENEMILL_CLEAN_RUNS=1 to remove run outputs."
fi
