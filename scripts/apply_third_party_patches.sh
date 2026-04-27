#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ "${1:-}" != "--yes" ]]; then
  cat <<'EOF'
This script intentionally modifies files inside third_party submodules.
SceneMill no longer requires these patches for the default pipeline; it keeps
submodules pristine and handles compatibility in SceneMill wrappers instead.

If you explicitly want to apply the legacy patches, run:
  ./scripts/apply_third_party_patches.sh --yes
EOF
  exit 2
fi

git -C "${ROOT_DIR}/third_party/Depth-Anything-3" apply \
  "${ROOT_DIR}/patches/third_party/depth-anything-3-cli-ref-view-strategy.patch"

git -C "${ROOT_DIR}/third_party/3dgrut" apply \
  "${ROOT_DIR}/patches/third_party/3dgrut-usdz-64-byte-alignment.patch"

echo "Applied SceneMill third-party compatibility patches."
