"""pickal — Configuration Management.

Atomic Spec: Configuration Management
  § 1  — Schema-first hierarchical overrides
  § 2  — Environment variables: _VAR_NAME
  § 3  — Local dev config: .env file
  § 4  — Base defaults: hardcoded in models
  § 5  — Fail-fast policy: startup time
  § 6  — Pydantic Settings for type safety
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """Application configuration schema."""
    
    # Core settings
    debug: bool = False
    log_level: str = "INFO"
    
    # Environment-specific
    env: str = "development"
    
    # Paths
    config_dir: Path = Path("/etc/pickal")
    data_dir: Path = Path("/var/lib/pickal")
    cache_dir: Path = Path("/var/cache/pickal")
    
    # Network
    host: str = "127.0.0.1"
    port: int = 8080
    timeout: int = 30
    
    # Security
    secret_key: Optional[str] = None
    
    # Database
    database_url: Optional[str] = None
    
    class Config:
        env_prefix = "PICKAL_"
        env_file = ".env"
        case_sensitive = True
        extra = "forbid"


# Global configuration instance
config: AppSettings = AppSettings()