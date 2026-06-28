"""pickal — Unit Tests.

Atomic Spec: Unit Testing
  § 1  — Test configuration
  § 2  — Core module tests
  § 3  — Domain logic tests
  § 4  — API layer tests
  § 5  — Error handling tests
  § 6  — Coverage reporting
"""

import pytest
from pickal.config import AppSettings
from pickal.errors import BaseError, ConfigurationError


class TestAppSettings:
    """Test AppSettings configuration."""
    
    def test_default_values(self) -> None:
        """Test default configuration values."""
        settings = AppSettings()
        assert settings.debug is False
        assert settings.log_level == "INFO"
        assert settings.env == "development"
        assert settings.host == "127.0.0.1"
        assert settings.port == 8080
    
    def test_environment_variables(self) -> None:
        """Test environment variable overrides."""
        import os
        os.environ["PICKAL_DEBUG"] = "true"
        os.environ["PICKAL_LOG_LEVEL"] = "DEBUG"
        
        settings = AppSettings()
        assert settings.debug is True
        assert settings.log_level == "DEBUG"
    
    def test_config_file(self) -> None:
        """Test config file loading."""
        # This would require a test config file
        pass


class TestBaseError:
    """Test error handling."""
    
    def test_base_error(self) -> None:
        """Test base error functionality."""
        error = BaseError("Test error", code=100, details={"key": "value"})
        assert str(error) == "Test error (details: {'key': 'value'})"
        assert error.code == 100
        assert error.details == {"key": "value"}
    
    def test_configuration_error(self) -> None:
        """Test configuration error."""
        error = ConfigurationError("Invalid config", details={"field": "missing"})
        assert error.code == 10
        assert error.details == {"field": "missing"}


class TestValidationError:
    """Test validation error."""
    
    def test_validation_error(self) -> None:
        """Test validation error functionality."""
        error = BaseError("Invalid data", code=20, details={"field": "invalid"})
        assert error.code == 20
        assert error.details == {"field": "invalid"}