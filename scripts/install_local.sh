#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "[SceneMill] Initializing submodules"
git submodule update --init --recursive

echo "[SceneMill] Installing package with dev/docs/ros extras"
python3 -m pip install -e ".[dev,docs,ros]"

echo "[SceneMill] Leaving third_party submodules pristine"

echo "[SceneMill] Installation complete"
echo "Run: ./scenemill doctor"
