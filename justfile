# pickal
# Justfile — Command Runner Contract (Atomic Spec: DX & Repo Structure)
# Usage: just <target>

set shell := ["bash", "-euo", "pipefail", "-c"]
set dotenv-load := true

APP      := "pickal"
MODULE   := "pickal"
SRC_DIR  := "src"
DIST_DIR := "dist"

# ── Default ─────────────────────────────────────────────────

# List all available targets
default:
    @just --list

# ── Code Quality ─────────────────────────────────────────────

# Format source code
fmt:
    uv run ruff format src tests

# Lint (ruff + mypy)
lint *ARGS:
    uv run ruff check {{ARGS}} src tests
    uv run mypy src

# Fix auto-fixable lint issues
fix:
    uv run ruff check --fix src tests
    uv run ruff format src tests

# ── Testing ──────────────────────────────────────────────────

# Run test suite
test:
    uv run pytest

# Run tests with coverage report
coverage:
    uv run pytest --cov=src/pickal --cov-report=term-missing --cov-report=html

# ── Build ────────────────────────────────────────────────────

# Build the wheel artifact
build:
    # Create dist directory
    mkdir -p {{DIST_DIR}}/dist
    
    # Build wheel
    uv build --wheel --out-dir {{DIST_DIR}}/lib
    
    # Copy lockfile
    cp uv.lock {{DIST_DIR}}/dist/
    
    # Copy shim
    cp bin/bootstrap_shim.sh {{DIST_DIR}}/dist/
    
    # Create tarball
    tar -czf {{DIST_DIR}}/{{APP}}-{{VERSION}}.tar.gz \
        -C {{DIST_DIR}}/dist \
        .

# Generate locked dependency file for target platform
lock:
    uv export --no-dev --format requirements-txt -o conf/requirements.lock

# ── Distribution ─────────────────────────────────────────────

# Assemble portable tarball (Atomic Spec: Distribution § 3)
dist: build lock
    #!/usr/bin/env bash
    set -euo pipefail
    VERSION=$(uv run python -c "from pickal import __version__; print(__version__)")
    STAGING="{{DIST_DIR}}/pickal-${VERSION}"
    rm -rf "${STAGING}"
    mkdir -p "${STAGING}/bin" "${STAGING}/lib" "${STAGING}/conf"

    # Shim entrypoint
    cp bin/pickal.sh "${STAGING}/bin/pickal"
    chmod +x "${STAGING}/bin/pickal"

    # Application logic (wheel)
    cp {{DIST_DIR}}/lib/pickal-*.whl "${STAGING}/lib/"

    # Dependency lock
    cp conf/requirements.lock "${STAGING}/conf/"

    # Default config
    cp conf/defaults.yaml "${STAGING}/conf/"

    # Create archive
    ARCHIVE="{{DIST_DIR}}/pickal-${VERSION}-linux-x64.tar.gz"
    tar -czf "${ARCHIVE}" -C "{{DIST_DIR}}" "pickal-${VERSION}"
    echo "✅ Distribution artifact: ${ARCHIVE}"

# ── Cleanup ───────────────────────────────────────────────────

# Remove all build/cache artifacts
clean:
    rm -rf {{DIST_DIR}} .venv __pycache__ .mypy_cache .ruff_cache .pytest_cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true

# ── Development ───────────────────────────────────────────────

# Run the CLI in dev mode
run *ARGS:
    uv run pickal {{ARGS}}

# Run the application
run:
    uv run python -m pickal "$@"

# Full CI sequence (lint → test)
ci: lint test
    @echo "✅ CI checks passed"

# ── Release ───────────────────────────────────────────────────

# Release the application
release:
    # Ensure we're on main branch
    git checkout main
    
    # Ensure working directory is clean
    if ! git diff --quiet; then
        echo "Working directory is not clean. Please commit changes first."
        exit 1
    fi
    
    # Build distribution
    just build
    
    # Create tag
    VERSION=$(python -c "import pickal; print(pickal.__version__)" 2>/dev/null || echo "0.1.0")
    git tag -a "v$VERSION" -m "Release v$VERSION"
    
    # Push tag
    git push origin "v$VERSION"
    
    # Push main
    git push origin main

# ── Tagging ───────────────────────────────────────────────────

# Tag the current version
# Usage: just tag [major|minor|patch]
tag:
    # Get current version
    CURRENT_VERSION=$(python -c "import pickal; print(pickal.__version__)" 2>/dev/null || echo "0.1.0")
    
    # Determine version bump
    case "${1:-patch}" in
        major)
            NEW_VERSION=$(echo "$CURRENT_VERSION" | awk -F. '{print $1+1".0.0"}')
            ;;
        minor)
            NEW_VERSION=$(echo "$CURRENT_VERSION" | awk -F. '{print $1"."$2+1".0"}')
            ;;
        patch)
            NEW_VERSION=$(echo "$CURRENT_VERSION" | awk -F. '{print $1"."$2"."$3+1}')
            ;;
        *)
            echo "Usage: just tag [major|minor|patch]"
            exit 1
            ;;
    esac
    
    # Update version in pyproject.toml
    sed -i "s/^version = .*/version = '$NEW_VERSION'/" pyproject.toml
    
    # Commit and tag
    git add pyproject.toml
    git commit -m "Bump version to $NEW_VERSION"
    git tag -a "v$NEW_VERSION" -m "Version $NEW_VERSION"
    
    echo "Version bumped to $NEW_VERSION and tagged as v$NEW_VERSION"

# ── Template ─────────────────────────────────────────────────

# Update template from upstream
update-template:
    copier update
    
    # Reinstall development dependencies
    uv pip install -e .[dev]
    
    # Run validation
    just check

# Validate all quality gates
validate:
    # Run all quality checks
    just test
    just lint
    just fmt --check
    just check

# ── Documentation ─────────────────────────────────────────────

# Generate documentation
# Usage: just docs [serve]
docs:
    # Generate API documentation
    uv run pdoc --html --output-dir docs/api src/pickal
    
    # Generate README
    uv run pdoc --html --output-dir docs src/pickal/__main__.py
    
    # Serve documentation if requested
    if [ "$1" = "serve" ]; then
        cd docs && python -m http.server 8000
    fi

# Environment management
env-add:
    uv add "$@"
    
env-remove:
    uv remove "$@"
    
env-lock:
    uv lock
    
env-sync:
    uv sync

# Install development dependencies
setup:
    # Install uv if not present
    if ! command -v uv &> /dev/null; then
        echo "Installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh -s -- --yes --dest ~/.local/bin
        export PATH="$HOME/.local/bin:$PATH"
    fi
    
    # Install dependencies
    uv pip install -e .[dev]
    
    # Install pre-commit hooks if available
    if [ -f .pre-commit-config.yaml ]; then
        pre-commit install
    fi
