"""pickal — Core Architecture.

Atomic Spec: Core Architecture & Patterns
  § 1  — Config, Exceptions, Logging
  § 2  — Business Logic (Framework agnostic)
  § 3  — Interfaces (CLI, REST, gRPC)
  § 4  — Error handling hierarchy
  § 5  — Logging configuration
  § 6  — Dependency injection patterns
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import rich.console
import rich.logging

from .config import config
from .errors import BaseError, EXIT_CODES


class Logger:
    """Application logger with rich formatting."""
    
    def __init__(self) -> None:
        self._logger = logging.getLogger("pickal")
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Configure logging with rich formatter."""
        # Clear existing handlers
        self._logger.handlers.clear()
        
        # Set level
        level = getattr(logging, config.log_level.upper(), logging.INFO)
        self._logger.setLevel(level)
        
        # Console handler
        console_handler = rich.logging.RichHandler(
            console=rich.console.Console(
                file=sys.stderr,
                force_terminal=True,
                width=120,
                markup=True
            ),
            show_time=True,
            show_path=False,
            show_level=True
        )
        
        formatter = rich.logging.RichFormatter(
            show_path=False,
            markup=True
        )
        
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
    
    def get_logger(self, name: str = "pickal") -> logging.Logger:
        """Get a configured logger."""
        return logging.getLogger(name)


# Global logger instance
logger = Logger()


def setup_logging() -> None:
    """Setup application logging."""
    logger._setup_logging()


def get_logger(name: str = "pickal") -> logging.Logger:
    """Get a configured logger."""
    return logger.get_logger(name)