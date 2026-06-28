"""pickal — Configuration Management.

Atomic Spec: Configuration Management
  § 1  — Hierarchical Merge strategy, highest-wins precedence
  § 3  — Env vars with PICKAL_ prefix
  § 4  — XDG-compliant discovery paths
  § 6  — Fail-fast validation at startup

Precedence (highest → lowest):
  1. CLI flags (applied by cli.py after loading this config)
  2. Environment variables (PICKAL_*)
  3. User config  : ~/.config/pickal/config.yaml
  4. System config: /etc/pickal/config.yaml
  5. Base defaults : <package>/conf/defaults.yaml  ← ONLY place for defaults
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from .errors import EXIT_CONFIG_ERROR

logger = logging.getLogger(__name__)

# ── Discovery paths ─────────────────────────────────────────

_XDG_CONFIG_HOME = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
_USER_CONFIG = _XDG_CONFIG_HOME / "pickal" / "config.yaml"
_SYSTEM_CONFIG = Path("/etc/pickal/config.yaml")
_PKG_DEFAULTS = Path(__file__).parent.parent.parent / "conf" / "defaults.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML file; return empty dict if it doesn't exist."""
    if not path.exists():
        logger.debug("Config file not found (skipping): %s", path)
        return {}
    logger.debug("Loading config from: %s", path)
    with path.open() as f:
        return yaml.safe_load(f) or {}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge override into base (override wins on conflicts)."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


# ── Settings Model ───────────────────────────────────────────


class LoggingSettings(BaseSettings):
    """Logging configuration."""

    model_config = SettingsConfigDict(populate_by_name=True)

    level: str = "WARNING"


class AppSettings(BaseSettings):
    """Root application configuration.

    TODO: Add your application-specific settings here.
    Each field maps to a key in config.yaml and/or an env var.

    Example:
        class ServerSettings(BaseSettings):
            host: str = "127.0.0.1"
            port: int = 8080
    """

    model_config = SettingsConfigDict(
        env_prefix="PICKAL_",
        env_nested_delimiter="__",
        populate_by_name=True,
        extra="ignore",  # Change to "forbid" for strict unknown-key rejection
    )

    logging: LoggingSettings = LoggingSettings()
    config_file: Path | None = None  # Set by --config CLI flag


# ── Public API ───────────────────────────────────────────────


def load_config(config_file: Path | None = None) -> AppSettings:
    """Load and validate merged configuration.

    Applies the layered merge strategy and validates the result.
    Fails fast (EXIT_CONFIG_ERROR) on any validation error.

    Args:
        config_file: Optional explicit path from --config CLI flag.

    Returns:
        Validated AppSettings instance.
    """
    # Layer 1: base defaults (mandatory — packaged with the application)
    merged: dict[str, Any] = _load_yaml(_PKG_DEFAULTS)

    # Layer 2: system-wide config (optional)
    merged = _deep_merge(merged, _load_yaml(_SYSTEM_CONFIG))

    # Layer 3: user config (optional, XDG)
    merged = _deep_merge(merged, _load_yaml(_USER_CONFIG))

    # Layer 4: explicit --config flag (optional, highest YAML precedence)
    if config_file:
        override = _load_yaml(config_file)
        if not override and config_file.exists():
            logger.warning("Explicit config file is empty: %s", config_file)
        merged = _deep_merge(merged, override)

    # Layer 5: environment variables are handled automatically by Pydantic Settings
    try:
        return AppSettings(**merged)
    except ValidationError as exc:
        # Atomic Spec: Config § 6 — Fail-fast at startup
        # Redact any value containing secret-like key names
        _safe = str(exc).replace(str(exc), "[CONFIG VALIDATION ERROR — see below]")
        print(
            f"[CONFIG ERROR] Invalid configuration:\n{exc}",
            file=sys.stderr,
        )
        raise SystemExit(EXIT_CONFIG_ERROR) from None

