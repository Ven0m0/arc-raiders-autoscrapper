from unittest.mock import MagicMock, patch

import pytest

from autoscrapper import warmup
from autoscrapper.warmup import (
    _get_warmup_error,
    _run_background_warmup,
    _set_warmup_error,
    start_background_warmup,
    warmup_status,
)


@pytest.fixture(autouse=True)
def reset_warmup_state():
    with warmup._WARMUP_LOCK:
        orig_started = warmup._WARMUP_STARTED
        orig_error = warmup._WARMUP_ERROR
        orig_done_is_set = warmup._WARMUP_DONE.is_set()

        warmup._WARMUP_STARTED = False
        warmup._WARMUP_ERROR = None
        warmup._WARMUP_DONE.clear()

    yield

    with warmup._WARMUP_LOCK:
        warmup._WARMUP_STARTED = orig_started
        warmup._WARMUP_ERROR = orig_error
        if orig_done_is_set:
            warmup._WARMUP_DONE.set()
        else:
            warmup._WARMUP_DONE.clear()


def test_warmup_status_initial() -> None:
    status = warmup_status()
    assert not status.started
    assert not status.completed
    assert not status.failed
    assert status.error is None


def test_set_get_warmup_error() -> None:
    assert _get_warmup_error() is None
    _set_warmup_error("some error")
    assert _get_warmup_error() == "some error"

    status = warmup_status()
    assert status.failed
    assert status.error == "some error"


@patch("autoscrapper.warmup.threading.Thread")
def test_start_background_warmup(mock_thread_class: MagicMock) -> None:
    mock_thread = MagicMock()
    mock_thread_class.return_value = mock_thread

    start_background_warmup()

    assert warmup._WARMUP_STARTED is True
    mock_thread_class.assert_called_once_with(
        target=_run_background_warmup,
        name="autoscrapper-warmup",
        daemon=True,
    )
    mock_thread.start.assert_called_once()

    # Calling again should not start a new thread
    start_background_warmup()
    mock_thread_class.assert_called_once()  # Still called once


@patch("autoscrapper.warmup.importlib.import_module")
def test_run_background_warmup_success(mock_import_module: MagicMock) -> None:
    _run_background_warmup()

    # Should call import_module for each item in _HEAVY_MODULES
    assert mock_import_module.call_count == len(warmup._HEAVY_MODULES)
    for module_name in warmup._HEAVY_MODULES:
        mock_import_module.assert_any_call(module_name)

    assert warmup._WARMUP_DONE.is_set()
    assert _get_warmup_error() is None


@patch("autoscrapper.warmup.importlib.import_module")
def test_run_background_warmup_failure(mock_import_module: MagicMock) -> None:
    mock_import_module.side_effect = Exception("test import error")

    _run_background_warmup()

    assert warmup._WARMUP_DONE.is_set()
    assert _get_warmup_error() == "Exception: test import error"
