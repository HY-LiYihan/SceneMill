#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

INPUT_PATH="${1:-}"
WORKSPACE="${2:-runs/example_da3_3dgut}"

if [[ -z "${INPUT_PATH}" ]]; then
  echo "Usage: $0 /path/to/images [workspace]"
  exit 2
fi

./scenemill run \
  -c configs/presets/images_da3_3dgut_isaac.yaml \
  --input "${INPUT_PATH}" \
  --workspace "${WORKSPACE}"
