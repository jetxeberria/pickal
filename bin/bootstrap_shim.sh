#!/usr/bin/env bash
# pickal — Distribution Shim
# Atomic Spec: Distribution & Runtime Provisioning

set -euo pipefail

# Compute installation directory (location agnostic)
INSTALL_DIR="$(cd "$(dirname "$(realpath "$0")")" && pwd)"

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "Installing uv..." >&2
    curl -LsSf https://astral.sh/uv/install.sh | sh -s -- --yes --dest "$INSTALL_DIR"
    export PATH="$INSTALL_DIR:$PATH"
fi

# Check if virtual environment exists
VENV_DIR="$INSTALL_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Setting up virtual environment..." >&2
    uv venv "$VENV_DIR"
fi

# Activate virtual environment and sync dependencies
export UV_HOME="$VENV_DIR"
uv pip sync "$INSTALL_DIR/uv.lock"

# Install the bundled application wheel
WHEEL_PATH=$(find "$INSTALL_DIR/dist/lib" -name "*.whl" -print -quit)
if [ -n "$WHEEL_PATH" ]; then
    uv pip install "$WHEEL_PATH"
fi

# Execute the application with original arguments
exec "$VENV_DIR/bin/python" -m pickal "$@"