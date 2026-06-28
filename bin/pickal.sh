#!/usr/bin/env bash
# =============================================================================
# pickal — Runtime Bootstrap Shim
# Atomic Spec: Distribution & Runtime Provisioning § 5
#
# This script is the sole executable entrypoint in the distribution tarball.
# It is location-agnostic and performs lazy first-run bootstrapping.
#
# Bootstrapping sequence (§ 5.2):
#   1. Resolve own physical location (follows symlinks)
#   2. Check for uv; download static binary if absent
#   3. Create .venv if not yet initialized
#   4. Sync dependencies from conf/requirements.lock
#   5. Install local .whl into .venv
#   6. exec into Python (replacing THIS process, inheriting PID)
# =============================================================================

set -euo pipefail

# ── 1. Resolve installation directory ─────────────────────────────────────────
# Works correctly even when invoked through a symlink in ~/.local/bin
INSTALL_DIR="$(dirname "$(realpath "$0")")"
# The shim lives in $INSTALL_DIR/bin/, so the root is one level up
INSTALL_DIR="$(dirname "${INSTALL_DIR}")"

UV_BIN="${INSTALL_DIR}/bin/uv"
VENV_DIR="${INSTALL_DIR}/.venv"
LOCK_FILE="${INSTALL_DIR}/conf/requirements.lock"
WHL_DIR="${INSTALL_DIR}/lib"

# ── 2. Tool check: uv ─────────────────────────────────────────────────────────
if [[ ! -x "${UV_BIN}" ]]; then
    echo "[pickal] uv not found. Downloading static binary..." >&2
    ARCH="$(uname -m)"
    UV_URL="https://github.com/astral-sh/uv/releases/latest/download/uv-${ARCH}-unknown-linux-musl.tar.gz"
    TMP_UV="$(mktemp -d)"
    curl --silent --show-error --fail --location "${UV_URL}" \
        | tar xz -C "${TMP_UV}"
    mv "${TMP_UV}/uv-${ARCH}-unknown-linux-musl/uv" "${UV_BIN}"
    chmod +x "${UV_BIN}"
    rm -rf "${TMP_UV}"
    echo "[pickal] uv installed at ${UV_BIN}" >&2
fi

# ── 3. Environment check: .venv ───────────────────────────────────────────────
if [[ ! -d "${VENV_DIR}" ]]; then
    echo "[pickal] First run: creating virtual environment..." >&2
    "${UV_BIN}" venv "${VENV_DIR}" --quiet
fi

# ── 4. Dependency sync ────────────────────────────────────────────────────────
# Only sync if lock file exists; skip gracefully otherwise (dev installs)
if [[ -f "${LOCK_FILE}" ]]; then
    "${UV_BIN}" pip sync --quiet \
        --python "${VENV_DIR}/bin/python" \
        "${LOCK_FILE}"
fi

# ── 5. Install local wheel ────────────────────────────────────────────────────
# Installs the app from the bundled .whl — NOT from git or PyPI
WHL_FILE="$(find "${WHL_DIR}" -name "*.whl" 2>/dev/null | head -1)"
if [[ -n "${WHL_FILE}" ]]; then
    "${UV_BIN}" pip install --quiet \
        --python "${VENV_DIR}/bin/python" \
        --no-deps \
        "${WHL_FILE}"
fi

# ── 6. PATH integration hint (first-run UX) ──────────────────────────────────
SHIM_PATH="${INSTALL_DIR}/bin/pickal"
if command -v pickal &>/dev/null; then
    : # already in PATH, no prompt needed
elif [[ -t 0 ]]; then
    # Interactive terminal: offer to create symlink
    read -r -p "[pickal] Not in PATH. Add symlink to ~/.local/bin? [y/N] " _answer
    if [[ "${_answer:-N}" =~ ^[Yy]$ ]]; then
        mkdir -p "${HOME}/.local/bin"
        ln -sf "${SHIM_PATH}" "${HOME}/.local/bin/pickal"
        echo "[pickal] Symlink created. Ensure ~/.local/bin is in your \$PATH." >&2
    fi
fi

# ── 7. Execution handover ─────────────────────────────────────────────────────
# Use exec to replace this process (inherits PID, transparent stream handling)
exec "${VENV_DIR}/bin/python" -m pickal "$@"
