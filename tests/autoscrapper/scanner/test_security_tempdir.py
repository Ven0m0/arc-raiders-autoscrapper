"""Security tests for decision log temp directory handling."""

import tempfile
from pathlib import Path

from autoscrapper.scanner.scan_loop import _close_decision_log, _init_decision_log


def test_decision_log_uses_secure_tempdir():
    log_path = _init_decision_log()
    try:
        assert log_path is not None
        log_dir = Path(log_path).parent
        # mkdtemp creates a directory inside the system temp dir
        assert log_dir.is_relative_to(Path(tempfile.gettempdir()))
        # Directory must have restricted permissions (not world-readable)
        mode = log_dir.stat().st_mode & 0o777
        assert mode == 0o700, f"Expected 0o700, got {oct(mode)}"
    finally:
        _close_decision_log()


def test_close_decision_log_removes_tempdir():
    log_path = _init_decision_log()
    assert log_path is not None
    log_dir = Path(log_path).parent
    assert log_dir.exists()

    _close_decision_log()
    assert not log_dir.exists()
