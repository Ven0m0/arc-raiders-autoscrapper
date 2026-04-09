"""Shared utilities for lint-and-validate scripts."""

import sys


def fix_windows_console_encoding() -> None:
    """Fix Windows console encoding for Unicode output."""
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass  # Python < 3.7
