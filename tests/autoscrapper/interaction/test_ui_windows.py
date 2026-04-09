import sys
from unittest.mock import MagicMock, patch


def get_target_function():
    mock_modules = {
        "pywinctl": MagicMock(),
        "mss": MagicMock(),
        "pynput": MagicMock(),
        "pynput.keyboard": MagicMock(),
        "pynput.mouse": MagicMock(),
    }

    # We need to make sure the target module is not already loaded,
    # otherwise it will use the already loaded version.
    target_module_name = "autoscrapper.interaction.ui_windows"
    if target_module_name in sys.modules:
        del sys.modules[target_module_name]

    with patch.dict(sys.modules, mock_modules):
        import autoscrapper.interaction.ui_windows as ui_windows

        # Save a reference to the function
        func = ui_windows._is_mss_thread_handle_error

    # We must remove it from sys.modules so other tests don't get the mocked version
    if target_module_name in sys.modules:
        del sys.modules[target_module_name]

    return func


def test_is_mss_thread_handle_error_with_srcdc():
    func = get_target_function()
    exc = Exception("Screen capture failed: invalid srcdc")
    assert func(exc) is True


def test_is_mss_thread_handle_error_with_thread_local():
    func = get_target_function()
    exc = Exception(
        "AttributeError: '_thread._local' object has no attribute 'instance'"
    )
    assert func(exc) is True


def test_is_mss_thread_handle_error_case_insensitive():
    func = get_target_function()
    exc = Exception("Error regarding SRCDC handle")
    assert func(exc) is True

    exc2 = Exception("THREAD._LOCAL error")
    assert func(exc2) is True


def test_is_mss_thread_handle_error_negative_cases():
    func = get_target_function()
    exc1 = ValueError("Invalid region")
    assert func(exc1) is False

    exc2 = RuntimeError("Timeout waiting for target window")
    assert func(exc2) is False

    exc3 = KeyError("missing key")
    assert func(exc3) is False

    exc4 = Exception("")
    assert func(exc4) is False
