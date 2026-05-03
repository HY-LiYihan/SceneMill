#!/usr/bin/env bash
# End-to-end test for SceneMill.
#
# Automated tier (no GPU required):
#   1. Create a fresh conda environment
#   2. Install SceneMill
#   3. Run scenemill doctor
#   4. Run unit tests (pytest)
#   5. Run dry-run pipeline and verify manifest
#
# Usage:
#   ./scripts/test_e2e.sh [options]
#
# Options:
#   --env-name NAME        Conda env to create (default: scenemill_test)
#   --skip-env-create      Skip env creation (use existing env)
#   --keep-workspace       Keep runs/e2e_dry after the test
#   --input PATH           Image directory for dry-run (default: data/test_scene)

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

ENV_NAME="scenemill_test"
SKIP_ENV_CREATE=false
KEEP_WORKSPACE=false
INPUT_PATH="data/test_scene"
WORKSPACE="runs/e2e_dry"
PASS=0
FAIL=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --env-name)     ENV_NAME="$2"; shift 2 ;;
        --skip-env-create) SKIP_ENV_CREATE=true; shift ;;
        --keep-workspace)  KEEP_WORKSPACE=true; shift ;;
        --input)        INPUT_PATH="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 2 ;;
    esac
done

ok()   { printf "[ OK ] %s\n" "$*"; PASS=$((PASS + 1)); }
fail() { printf "[FAIL] %s\n" "$*"; FAIL=$((FAIL + 1)); }

eval "$(conda shell.bash hook)"

# ── Step 1: Create environment ────────────────────────────────────────────────
if [[ "${SKIP_ENV_CREATE}" == "false" ]]; then
    echo ""
    echo "=== Step 1: Create conda environment '${ENV_NAME}' ==="
    if conda env list | awk '{print $1}' | grep -qx "${ENV_NAME}"; then
        echo "  Environment already exists, removing it first..."
        conda env remove -n "${ENV_NAME}" -y
    fi
    conda create -n "${ENV_NAME}" python=3.11 -y
    conda activate "${ENV_NAME}"
    pip install -e ".[dev]" -q
    ok "Environment created and SceneMill installed"
else
    echo ""
    echo "=== Step 1: Skipping env creation, activating '${ENV_NAME}' ==="
    conda activate "${ENV_NAME}"
    ok "Environment activated"
fi

# ── Step 2: doctor ────────────────────────────────────────────────────────────
echo ""
echo "=== Step 2: scenemill doctor ==="
if PYTHONPATH=src python -m scenemill.cli doctor 2>&1 | tee /tmp/scenemill_doctor.txt; then
    ok "doctor exited 0"
else
    fail "doctor returned non-zero"
fi

# ── Step 3: Unit tests ────────────────────────────────────────────────────────
echo ""
echo "=== Step 3: Unit tests ==="
if PYTHONPATH=src python -m pytest tests/ -v --tb=short 2>&1; then
    ok "All unit tests passed"
else
    fail "Unit tests failed"
fi

# ── Step 4: Dry-run pipeline ──────────────────────────────────────────────────
echo ""
echo "=== Step 4: Dry-run pipeline ==="
if [[ ! -d "${INPUT_PATH}" ]]; then
    fail "Input path not found: ${INPUT_PATH}"
else
    if PYTHONPATH=src python -m scenemill.cli run \
        --preset da3 \
        --input "${INPUT_PATH}" \
        --workspace "${WORKSPACE}" \
        --dry-run 2>&1; then
        ok "Dry-run pipeline completed"
    else
        fail "Dry-run pipeline failed"
    fi
fi

# ── Step 5: Verify manifest ───────────────────────────────────────────────────
echo ""
echo "=== Step 5: Verify manifest ==="
MANIFEST="${WORKSPACE}/scene_manifest.yaml"
if [[ -f "${MANIFEST}" ]]; then
    ok "Manifest exists: ${MANIFEST}"
    # Check all stage returncodes are 0
    if python3 -c "
import yaml, sys
with open('${MANIFEST}') as f:
    m = yaml.safe_load(f)
stages = m.get('stages', {})
bad = [(k, v.get('returncode')) for k, v in stages.items() if isinstance(v, dict) and v.get('returncode', 0) != 0]
if bad:
    print('Non-zero returncodes:', bad)
    sys.exit(1)
print('All stage returncodes: 0')
" 2>&1; then
        ok "All stage returncodes are 0"
    else
        fail "Some stages returned non-zero"
    fi
else
    fail "Manifest not found: ${MANIFEST}"
fi

# ── Cleanup ───────────────────────────────────────────────────────────────────
if [[ "${KEEP_WORKSPACE}" == "false" && -d "${WORKSPACE}" ]]; then
    rm -rf "${WORKSPACE}"
    echo ""
    echo "Cleaned up workspace: ${WORKSPACE}"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════"
echo "  SceneMill E2E Test Results"
echo "  Passed: ${PASS}   Failed: ${FAIL}"
echo "════════════════════════════════════════"

if [[ "${FAIL}" -gt 0 ]]; then
    echo ""
    echo "To run the full GPU pipeline manually:"
    echo "  conda activate scenemill"
    echo "  ./scenemill run --preset da3 --input ${INPUT_PATH} --workspace runs/e2e_full"
    exit 1
fi

echo ""
echo "Automated tests passed. For the full GPU pipeline run:"
echo "  conda activate scenemill"
echo "  ./scenemill run --preset da3 --input ${INPUT_PATH} --workspace runs/e2e_full"
