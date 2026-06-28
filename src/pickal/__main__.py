"""pickal — Package entrypoint.

Enables: python -m pickal
"""

import sys

from pickal.cli import app
from pickal.errors import EXIT_SIGINT


def main() -> None:
    """CLI entrypoint registered in pyproject.toml [project.scripts]."""
    try:
        app.meta()
    except KeyboardInterrupt:
        print("", file=sys.stderr)  # clean newline after ^C
        raise SystemExit(EXIT_SIGINT) from None


if __name__ == "__main__":
    main()
