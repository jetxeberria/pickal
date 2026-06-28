"""pickal — CLI Entrypoint.

Atomic Spec: CLI
  § 1  — Verb-based invocation pattern, core principles
  § 2  — Global options: --verbose, --quiet, --json, --config
  § 3  — Command hierarchy (verb / subcommand)
  § 4  — I/O: stdout=data, stderr=logs
  § 5  — Exit codes via errors.py
  § 6  — TTY detection for interactive prompts
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import cyclopts

from . import __version__
from .config import AppSettings, load_config
from .logging import setup_logging

# ── Application ──────────────────────────────────────────────

app = cyclopts.App(
    name="pickal",
    help="Identify events in a picture and save them to calendar",
    version=__version__,
)

# ── Global state (set by top-level callback) ─────────────────

_cfg: AppSettings | None = None
_json_mode: bool = False


# ── Root meta-parameter callback ─────────────────────────────


@app.meta.default
def _global_options(
    *tokens: Annotated[str, cyclopts.Parameter(show=False, allow_leading_hyphen=True)],
    verbose: Annotated[int, cyclopts.Parameter(name=["-v", "--verbose"], negative=[])] = 0,
    quiet: Annotated[bool, cyclopts.Parameter(name=["-q", "--quiet"])] = False,
    json_output: Annotated[bool, cyclopts.Parameter(name=["--json"])] = False,
    config: Annotated[Path | None, cyclopts.Parameter(name=["--config"])] = None,
) -> None:
    """Process global options before any subcommand runs."""
    global _cfg, _json_mode
    setup_logging(verbosity=verbose, quiet=quiet)
    
    # Load configuration
    _cfg = load_config(config)
    
    # Set JSON mode
    _json_mode = json_output
    
    # Configure logging level
    if verbose > 0:
        logging.getLogger("pickal").setLevel(logging.DEBUG)
    elif quiet:
        logging.getLogger("pickal").setLevel(logging.WARNING)

    app(tokens)


# ── Helper ────────────────────────────────────────────────────


def _out(data: object) -> None:
    """Write output to stdout.

    In --json mode: serialize as JSON (machine-readable).
    In TTY mode: human-friendly repr.
    All logs/progress remain on stderr via logging.
    """
    if _json_mode:
        print(json.dumps(data, default=str))
    else:
        print(data)


# ── Commands ─────────────────────────────────────────────────


@app.command
def version() -> None:
    """Print the application version and exit 0."""
    _out(__version__)


@app.command
def run(
    target: Annotated[str, cyclopts.Parameter(help="Target file or resource.")],
    *,
    dry_run: Annotated[bool, cyclopts.Parameter(name=["--dry-run"])] = False,
    force: Annotated[bool, cyclopts.Parameter(name=["--force"])] = False,
) -> None:
    """TODO: Replace with your primary command.

    Args:
        target: The target file or resource to operate on.
        dry_run: Simulate action, do not mutate any state.
        force: Skip confirmation prompts.
    """
    import logging

    log = logging.getLogger(__name__)

    log.info("Starting run: target=%s dry_run=%s force=%s", target, dry_run, force)

    if dry_run:
        log.warning("[DRY RUN] Would process: %s", target)
        _out({"status": "dry_run", "target": target})
        return

    # TODO: implement your core logic here
    _out({"status": "ok", "target": target})


# Import additional modules
from .errors import EXIT_SIGINT
from .core import setup_logging
from .config import load_config

# Add missing commands
def version() -> None:
    """Show version information."""
    print(f"pickal v")


@app.command()
def config() -> None:
    """Show current configuration."""
    if _cfg is None:
        print("Configuration not loaded")
        return
    
    if _json_mode:
        print(json.dumps(_cfg.to_dict(), indent=2))
    else:
        print("Current configuration:")
        for key, value in _cfg.to_dict().items():
            print(f"  {key}: {value}")


@app.command()
def health() -> None:
    """Check application health."""
    print("pickal is running")


@app.command()
def help() -> None:
    """Show help information."""
    app.print_help()


def main() -> None:
    """CLI entrypoint."""
    try:
        app.run()
    except KeyboardInterrupt:
        print("", file=sys.stderr)
        raise SystemExit(EXIT_SIGINT) from None


if __name__ == "__main__":
    main()
