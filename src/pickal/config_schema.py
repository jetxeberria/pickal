"""pickal — Configuration Schema.

Atomic Spec: Configuration Schema
  § 1  — Configuration models
  § 2  — Validation rules
  § 3  — Default values
  § 4  — Environment variable mapping
  § 5  — Configuration loading
  § 6  — Configuration validation
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class DatabaseConfig:
    """Database configuration."""
    
    url: Optional[str] = None
    max_connections: int = 10
    timeout: int = 30
    pool_size: int = 5


class LoggingConfig:
    """Logging configuration."""
    
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[Path] = None
    console: bool = True


class NetworkConfig:
    """Network configuration."""
    
    host: str = "127.0.0.1"
    port: int = 8080
    timeout: int = 30
    max_retries: int = 3


class SecurityConfig:
    """Security configuration."""
    
    secret_key: Optional[str] = None
    token_expiry: int = 3600
    enable_cors: bool = False
    cors_origins: list[str] = ["*"]


class AppSettings(BaseSettings):
    """Main application settings."""
    
    # Core settings
    debug: bool = False
    env: str = "development"
    name: str = "pickal"
    
    # Paths
    config_dir: Path = Path("/etc/pickal")
    data_dir: Path = Path("/var/lib/pickal")
    cache_dir: Path = Path("/var/cache/pickal")
    log_dir: Path = Path("/var/log/pickal")
    
    # Database
    database: DatabaseConfig = DatabaseConfig()
    
    # Logging
    logging: LoggingConfig = LoggingConfig()
    
    # Network
    network: NetworkConfig = NetworkConfig()
    
    # Security
    security: SecurityConfig = SecurityConfig()
    
    # Features
    enable_metrics: bool = True
    enable_tracing: bool = False
    enable_profiling: bool = False
    
    class Config:
        env_prefix = "PICKAL_"
        env_file = ".env"
        case_sensitive = True
        extra = "forbid"


# Global configuration instance
config: AppSettings = AppSettings()