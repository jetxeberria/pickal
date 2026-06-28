"""pickal — Exit Code Constants.

Atomic Spec: CLI § 5 — Exit Codes (The Signals).
All SystemExit calls must use these named constants for Bash compatibility.
"""

# Standard POSIX / GNU exit codes
EXIT_SUCCESS = 0       # All good. Proceed.
EXIT_FAILURE = 1       # Generic runtime error. Check logs.
EXIT_USAGE = 2         # Bad arguments / Invalid flags. Fix command syntax.
EXIT_NOPERM = 126      # Cannot execute (permission denied). Check chmod/ACLs.
EXIT_SIGINT = 130      # Terminated by Ctrl+C. Cleanup if needed.

# Application-specific codes (> 2 and < 126)
EXIT_CONFIG_ERROR = 3  # Configuration is invalid or missing required values.
EXIT_NOT_FOUND = 4     # A required resource/file was not found.
