import pytest

# ruff: noqa: E402
import sys
from unittest.mock import MagicMock

# Mock required UI libraries before importing module under test
sys.modules["pywinctl"] = MagicMock()
sys.modules["mss"] = MagicMock()
sys.modules["pynput"] = MagicMock()
sys.modules["pynput.keyboard"] = MagicMock()
sys.modules["pynput.mouse"] = MagicMock()

from autoscrapper.interaction.ui_windows import _is_mss_thread_handle_error


def test_is_mss_thread_handle_error_with_srcdc():
    # Test typical srcdc error case (exact or similar)
    exc = Exception("Screen capture failed: invalid srcdc")
    assert _is_mss_thread_handle_error(exc) is True


def test_is_mss_thread_handle_error_with_thread_local():
    # Test thread._local error case
    exc = Exception("AttributeError: '_thread._local' object has no attribute 'instance'")
    assert _is_mss_thread_handle_error(exc) is True


def test_is_mss_thread_handle_error_case_insensitive():
    # Test case insensitivity
    exc = Exception("Error regarding SRCDC handle")
    assert _is_mss_thread_handle_error(exc) is True

    exc2 = Exception("THREAD._LOCAL error")
    assert _is_mss_thread_handle_error(exc2) is True


def test_is_mss_thread_handle_error_negative_cases():
    # Test common non-mss handle errors
    exc1 = Exception("ValueError: Invalid region")
    assert _is_mss_thread_handle_error(exc1) is False

    exc2 = RuntimeError("Timeout waiting for target window")
    assert _is_mss_thread_handle_error(exc2) is False

    exc3 = KeyboardInterrupt()
    assert _is_mss_thread_handle_error(exc3) is False

    exc4 = Exception("")
    assert _is_mss_thread_handle_error(exc4) is False
