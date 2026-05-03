#!/usr/bin/env bash
# Create a unified conda environment for SceneMill (DA3 + 3DGUT + SceneMill).
#
# Usage:
#   ./scripts/create_env.sh [ENV_NAME]
#
# ENV_NAME defaults to "scenemill". Pass a different name to create a test
# environment without touching the production one, e.g.:
#   ./scripts/create_env.sh scenemill_test
#
# After this script completes:
#   conda activate <ENV_NAME>
#   ./scripts/install_local.sh   # installs SceneMill in editable mode
#   ./scenemill doctor            # verify everything is in order
#
# Isaac Sim (env_isaacsim) is NOT included here — it has Omniverse/USD
# dependencies that must be installed separately via the NVIDIA Isaac Sim
# installer. See docs/zh/installation.md for details.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

ENV_NAME="${1:-scenemill}"

echo "[SceneMill] Creating conda environment: ${ENV_NAME}"
echo "[SceneMill] Python 3.11 + PyTorch (CUDA 12.4)"
echo ""

# Initialise conda shell functions so we can use 'conda activate' in a script.
# shellcheck disable=SC1091
eval "$(conda shell.bash hook)"

if conda env list | awk '{print $1}' | grep -qx "${ENV_NAME}"; then
    echo "[SceneMill] Environment '${ENV_NAME}' already exists."
    echo "  To recreate it from scratch, first run:"
    echo "    conda env remove -n ${ENV_NAME}"
    echo "  Then re-run this script."
    exit 0
fi

conda create -n "${ENV_NAME}" python=3.11 -y
conda activate "${ENV_NAME}"

echo ""
echo "[SceneMill] Installing PyTorch with CUDA 12.4 wheels"
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124

echo ""
echo "[SceneMill] Installing DA3 dependencies"
pip install -r third_party/Depth-Anything-3/requirements.txt

echo ""
echo "[SceneMill] Installing 3DGUT dependencies"
cd third_party/3dgrut
pip install -e .
cd "${ROOT_DIR}"

echo ""
echo "[SceneMill] Installing SceneMill (editable) with dev/docs/ros extras"
pip install -e ".[dev,docs,ros]"

echo ""
echo "[SceneMill] Environment '${ENV_NAME}' is ready."
echo ""
echo "  Next steps:"
echo "    conda activate ${ENV_NAME}"
echo "    ./scenemill doctor"
