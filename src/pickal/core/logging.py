"""pickal — Logging Setup.

Atomic Spec: CLI § 4.2 — ALL logs go to stderr. stdout is reserved for data.
Uses Rich for human-readable TTY output, structured plain text for pipes.
"""

import logging
import sys

# Use Rich if available (it's a declared dependency)
try:
    from rich.logging import RichHandler

    _RICH_AVAILABLE = True
except ImportError:
    _RICH_AVAILABLE = False


def setup_logging(verbosity: int = 0, quiet: bool = False) -> None:
    """Configure the root logger based on CLI verbosity flags.

    Priority (per CLI Spec § 6.2):
      --quiet  → Only ERROR and CRITICAL
      default  → WARNING
      -v       → INFO
      -vv      → DEBUG

    All output goes to stderr. stdout remains clean for piped data.

    Args:
        verbosity: Number of times --verbose was passed (0, 1, or 2+).
        quiet: If True, suppress everything below ERROR.
    """
    if quiet:
        level = logging.ERROR
    elif verbosity == 0:
        level = logging.WARNING
    elif verbosity == 1:
        level = logging.INFO
    else:
        level = logging.DEBUG

    if _RICH_AVAILABLE:
        handler: logging.Handler = RichHandler(
            rich_tracebacks=True,
            show_path=(level == logging.DEBUG),
            markup=True,
            stream=sys.stderr,
        )
        formatter = logging.Formatter("%(message)s", datefmt="[%X]")
    else:
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        )

    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)

