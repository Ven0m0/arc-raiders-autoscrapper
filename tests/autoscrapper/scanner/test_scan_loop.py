import pytest
from itertools import islice

# We need to mock pywinctl and pynput to avoid X11 errors in headless environment
import sys
from unittest.mock import MagicMock

sys.modules["pywinctl"] = MagicMock()
sys.modules["pymonctl"] = MagicMock()
sys.modules["pynput"] = MagicMock()
sys.modules["pynput.keyboard"] = MagicMock()
sys.modules["pynput.mouse"] = MagicMock()

# ruff: noqa: E402
from autoscrapper.scanner.scan_loop import _scroll_clicks_sequence


def test_scroll_clicks_sequence_happy_path():
    """Test that the sequence repeats correctly."""
    pattern = [1, 2, 3]
    seq = _scroll_clicks_sequence(pattern)

    # Take first 7 elements to ensure it cycles multiple times
    result = list(islice(seq, 7))
    assert result == [1, 2, 3, 1, 2, 3, 1]


def test_scroll_clicks_sequence_empty_pattern():
    """Test that empty pattern raises ValueError."""
    with pytest.raises(ValueError, match="scroll click pattern must not be empty"):
        _scroll_clicks_sequence([])


def test_scroll_clicks_sequence_zero_values():
    """Test that pattern with zero values raises ValueError."""
    with pytest.raises(ValueError, match="scroll click pattern values must be > 0"):
        _scroll_clicks_sequence([1, 0, 2])


def test_scroll_clicks_sequence_negative_values():
    """Test that pattern with negative values raises ValueError."""
    with pytest.raises(ValueError, match="scroll click pattern values must be > 0"):
        _scroll_clicks_sequence([1, -1, 2])


def test_scroll_clicks_sequence_with_strings_convertible_to_int():
    """Test that the sequence accepts elements convertible to int."""
    pattern = ["1", "2"]
    seq = _scroll_clicks_sequence(pattern)
    result = list(islice(seq, 3))
    assert result == [1, 2, 1]


def test_scroll_clicks_sequence_with_strings_not_convertible_to_int():
    """Test that the sequence raises ValueError if elements cannot be converted to int."""
    pattern = ["1", "a"]
    with pytest.raises(ValueError):
        _scroll_clicks_sequence(pattern)
