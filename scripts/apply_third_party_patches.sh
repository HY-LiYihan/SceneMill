#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

git -C "${ROOT_DIR}/third_party/Depth-Anything-3" apply \
  "${ROOT_DIR}/patches/third_party/depth-anything-3-cli-ref-view-strategy.patch"

git -C "${ROOT_DIR}/third_party/3dgrut" apply \
  "${ROOT_DIR}/patches/third_party/3dgrut-usdz-64-byte-alignment.patch"

echo "Applied SceneMill third-party compatibility patches."

