"""pickal — Error Handling.

Atomic Spec: Error Handling & Exit Codes
  § 1  — Base error hierarchy
  § 2  — Exit code definitions
  § 3  — Error formatting
  § 4  — Exception wrapping
  § 5  — Error reporting
  § 6  — Graceful shutdown
"""

from __future__ import annotations

import sys
from typing import Optional


class BaseError(Exception):
    """Base application error."""
    
    def __init__(
        self,
        message: str,
        code: int = 1,
        details: Optional[dict] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message)
        self.code = code
        self.details = details
        self.cause = cause
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.args[0]} (details: {self.details})"
        return self.args[0]


class ConfigurationError(BaseError):
    """Configuration validation error."""
    
    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message, code=10, details=details)


class ValidationError(BaseError):
    """Data validation error."""
    
    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message, code=20, details=details)


class NetworkError(BaseError):
    """Network communication error."""
    
    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message, code=30, details=details)


class DatabaseError(BaseError):
    """Database operation error."""
    
    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message, code=40, details=details)


class PermissionError(BaseError):
    """Permission denied error."""
    
    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message, code=50, details=details)


class NotFoundError(BaseError):
    """Resource not found error."""
    
    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message, code=60, details=details)


class TimeoutError(BaseError):
    """Operation timeout error."""
    
    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message, code=70, details=details)


class RateLimitError(BaseError):
    """Rate limit exceeded error."""
    
    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message, code=80, details=details)


class ServiceUnavailableError(BaseError):
    """Service unavailable error."""
    
    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message, code=90, details=details)


# Exit codes
EXIT_CODES = {
    "SUCCESS": 0,
    "CONFIGURATION_ERROR": 10,
    "VALIDATION_ERROR": 20,
    "NETWORK_ERROR": 30,
    "DATABASE_ERROR": 40,
    "PERMISSION_ERROR": 50,
    "NOT_FOUND_ERROR": 60,
    "TIMEOUT_ERROR": 70,
    "RATE_LIMIT_ERROR": 80,
    "SERVICE_UNAVAILABLE_ERROR": 90,
    "UNKNOWN_ERROR": 1
}


# Common exit codes
EXIT_SUCCESS = EXIT_CODES["SUCCESS"]
EXIT_SIGINT = 130
EXIT_SIGTERM = 143