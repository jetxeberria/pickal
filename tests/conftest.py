"""pickal — Test Configuration.

Atomic Spec: Testing Infrastructure
  § 1  — Unit tests
  § 2  — Integration tests
  § 3  — Test configuration
  § 4  — Mock/fixture utilities
  § 5  — Test data management
  § 6  — Coverage reporting
"""

import pytest
from pytest import fixture


@fixture
def config() -> dict:
    """Test configuration fixture."""
    return {
        "debug": True,
        "log_level": "DEBUG",
        "env": "test",
        "host": "127.0.0.1",
        "port": 8000,
    }


@fixture
def app_settings(config: dict) -> dict:
    """App settings fixture."""
    from pickal.config import AppSettings
    return AppSettings(**config)


@fixture
def mock_repository() -> dict:
    """Mock repository fixture."""
    return {
        "find": lambda id: {"id": id, "name": "test"},
        "save": lambda entity: entity,
        "delete": lambda id: True,
        "list": lambda **filters: [{"id": 1, "name": "test"}]
    }


@fixture
def mock_service(mock_repository: dict) -> dict:
    """Mock service fixture."""
    from pickal.domain import Service
    return Service(mock_repository)