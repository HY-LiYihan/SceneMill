#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

FAILURES=0

ok() { printf "[ OK ] %s\n" "$*"; }
warn() { printf "[WARN] %s\n" "$*"; }
fail() { printf "[FAIL] %s\n" "$*"; FAILURES=$((FAILURES + 1)); }

have_cmd() {
  command -v "$1" >/dev/null 2>&1
}

check_cmd() {
  if have_cmd "$1"; then ok "$1: $(command -v "$1")"; else fail "$1 not found"; fi
}

check_conda_env() {
  local env_name="$1"
  if ! have_cmd conda; then
    fail "conda not found, cannot check env ${env_name}"
    return
  fi
  if conda env list | awk '{print $1}' | grep -qx "${env_name}"; then
    ok "conda env exists: ${env_name}"
  else
    warn "conda env missing: ${env_name}"
  fi
}

check_submodule_clean() {
  local repo="$1"
  local status
  status="$(git -C "${repo}" status --short --untracked-files=no 2>/dev/null || true)"
  if [[ -z "${status}" ]]; then
    ok "submodule clean: ${repo}"
  else
    warn "submodule has tracked local changes: ${repo}"
    printf "%s\n" "${status}"
  fi
}

echo "== SceneMill Doctor =="

check_cmd python3
check_cmd git
check_cmd conda
check_cmd nvidia-smi

if have_cmd nvidia-smi; then
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader || true
fi

check_conda_env da3_recon
check_conda_env 3dgrut_recon
check_conda_env env_isaacsim

[[ -d third_party/Depth-Anything-3/.git ]] && ok "submodule ready: Depth-Anything-3" || fail "submodule missing: Depth-Anything-3"
[[ -d third_party/3dgrut/.git ]] && ok "submodule ready: 3dgrut" || fail "submodule missing: 3dgrut"

[[ -x /usr/bin/gcc-11 ]] && ok "gcc-11 found" || warn "gcc-11 not found at /usr/bin/gcc-11"
[[ -x /usr/bin/g++-11 ]] && ok "g++-11 found" || warn "g++-11 not found at /usr/bin/g++-11"
[[ -d /usr/local/cuda-12.4 ]] && ok "CUDA found: /usr/local/cuda-12.4" || warn "CUDA 12.4 not found at /usr/local/cuda-12.4"

if [[ -d third_party/Depth-Anything-3/.git ]]; then
  check_submodule_clean third_party/Depth-Anything-3
fi
if [[ -d third_party/3dgrut/.git ]]; then
  check_submodule_clean third_party/3dgrut
fi

echo "== SceneMill CLI Doctor =="
./scenemill doctor || warn "scenemill doctor returned non-zero"

echo "== Isaac USD Python =="
ISAACSIM_ROOT="${ISAACSIM_ROOT:-${HOME}/isaacsim}"
USD_LIB=""
if [[ -d "${ISAACSIM_ROOT}/extscache" ]]; then
  USD_LIB="$(find "${ISAACSIM_ROOT}/extscache" -maxdepth 1 -type d -name 'omni.usd.libs-*' | head -n 1)"
fi
if [[ -n "${USD_LIB}" ]]; then
  if PYTHONPATH="${USD_LIB}:${PYTHONPATH:-}" LD_LIBRARY_PATH="${USD_LIB}/bin:${ISAACSIM_ROOT}/kit/python/lib:${CONDA_PREFIX:-}/lib:${LD_LIBRARY_PATH:-}" python3 -c "from pxr import Usd" >/dev/null 2>&1; then
    ok "pxr import works via ${USD_LIB}"
  else
    warn "pxr import failed even though omni.usd.libs was found"
  fi
else
  warn "omni.usd.libs not found under ${ISAACSIM_ROOT}/extscache"
fi

if [[ "${FAILURES}" -gt 0 ]]; then
  echo "SceneMill doctor found ${FAILURES} hard failure(s)."
  exit 1
fi
echo "SceneMill doctor finished."
