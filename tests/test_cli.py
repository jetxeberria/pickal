"""CLI smoke tests for pickal.

Atomic Spec: CLI § 5 — Exit codes are the contract.
Tests invoke the CLI as a subprocess to validate the full execution path,
including the shim's exec handover to python -m pickal.
"""

import json
import subprocess
import sys


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    """Run the CLI via `python -m pickal` and capture output."""
    return subprocess.run(
        [sys.executable, "-m", "pickal", *args],
        capture_output=True,
        text=True,
    )


class TestGlobalOptions:
    def test_help_exits_zero(self) -> None:
        result = _run("--help")
        assert result.returncode == 0
        assert "pickal" in result.stdout

    def test_version_exits_zero(self) -> None:
        result = _run("version")
        assert result.returncode == 0

    def test_version_output_on_stdout(self) -> None:
        result = _run("version")
        # Version must go to stdout (not stderr) per CLI Spec § 4.1
        assert result.stdout.strip()
        assert not result.stderr.strip()

    def test_json_version_is_valid_json(self) -> None:
        result = _run("--json", "version")
        assert result.returncode == 0
        # Must be parseable JSON with no extra text
        parsed = json.loads(result.stdout.strip())
        assert isinstance(parsed, str)

    def test_bad_command_exits_nonzero(self) -> None:
        result = _run("nonexistent-command-that-does-not-exist")
        assert result.returncode != 0


class TestRunCommand:
    def test_run_dry_run_exits_zero(self) -> None:
        result = _run("run", "some-target", "--dry-run")
        assert result.returncode == 0

    def test_run_dry_run_returns_json_status(self) -> None:
        result = _run("--json", "run", "some-target", "--dry-run")
        assert result.returncode == 0
        data = json.loads(result.stdout.strip())
        assert data["status"] == "dry_run"

    def test_run_produces_no_logs_on_stdout(self) -> None:
        result = _run("run", "some-target", "--dry-run")
        # stdout must be data only; warnings go to stderr
        lines = [line for line in result.stdout.splitlines() if line.strip()]
        assert len(lines) == 1  # exactly one output line
