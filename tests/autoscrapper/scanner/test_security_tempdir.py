import os
import stat
import tempfile
from pathlib import Path
from unittest.mock import MagicMock
import sys

# Mocking to avoid X11/pynput issues in CI
sys.modules["pywinctl"] = MagicMock()
sys.modules["pymonctl"] = MagicMock()
sys.modules["pynput"] = MagicMock()
sys.modules["pynput.keyboard"] = MagicMock()
sys.modules["pynput.mouse"] = MagicMock()
# ruff: noqa: E402

from autoscrapper.scanner.scan_loop import _init_decision_log, _close_decision_log


def test_init_decision_log_security():
    """
    Test that the decision log directory is created securely.
    """
    try:
        # 1. Initialize the decision log
        log_file_path_str = _init_decision_log()
        assert log_file_path_str is not None

        log_file_path = Path(log_file_path_str)
        log_dir = log_file_path.parent

        # 2. Check if the directory is within the system temp directory
        temp_dir = tempfile.gettempdir()
        assert str(log_dir).startswith(temp_dir)

        # 3. Check for secure permissions (mode 0o700)
        mode = os.stat(log_dir).st_mode
        # Mask with 0o777 to get just the permission bits
        permissions = stat.S_IMODE(mode)

        # Current code might fail this if it doesn't set permissions explicitly
        # and relies on default umask, or if it uses a shared directory.
        assert permissions == 0o700, f"Expected 0o700 permissions, got {oct(permissions)}"

        # 4. Check for unpredictable name
        # The current code uses "autoscrapper_decisions" which is predictable.
        # mkdtemp creates a unique name.
        assert log_dir.name != "autoscrapper_decisions", "Directory name is predictable 'autoscrapper_decisions'"
        assert log_dir.name.startswith("autoscrapper_decisions_"), f"Unexpected directory name: {log_dir.name}"

    finally:
        _close_decision_log()
        # Note: mkdtemp won't be automatically cleaned up by _close_decision_log
        # because the current _close_decision_log only closes the file handle.
        # However, for the test we might want to manually clean up if we really wanted to,
        # but let's see how the implementation goes.
