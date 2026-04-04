import pytest
from itertools import islice

from autoscrapper.scanner.scan_loop import _scroll_clicks_sequence


def test_scroll_clicks_sequence_happy_path():
    # Test with a regular list
    seq = _scroll_clicks_sequence([1, 2, 3])
    assert list(islice(seq, 7)) == [1, 2, 3, 1, 2, 3, 1]


def test_scroll_clicks_sequence_generator():
    # Test with a generator to ensure it's consumed correctly and can repeat
    def gen():
        yield 4
        yield 5

    seq = _scroll_clicks_sequence(gen())
    assert list(islice(seq, 5)) == [4, 5, 4, 5, 4]


def test_scroll_clicks_sequence_empty():
    # Empty pattern should raise ValueError
    with pytest.raises(ValueError, match="scroll click pattern must not be empty"):
        _scroll_clicks_sequence([])

    with pytest.raises(ValueError, match="scroll click pattern must not be empty"):
        _scroll_clicks_sequence(iter([]))


def test_scroll_clicks_sequence_zero_or_negative():
    # Pattern with 0 should raise ValueError
    with pytest.raises(ValueError, match="scroll click pattern values must be > 0"):
        _scroll_clicks_sequence([1, 0, 2])

    # Pattern with negative should raise ValueError
    with pytest.raises(ValueError, match="scroll click pattern values must be > 0"):
        _scroll_clicks_sequence([-1, 2])

    # Pattern with all negative
    with pytest.raises(ValueError, match="scroll click pattern values must be > 0"):
        _scroll_clicks_sequence([-5])

    # Pattern with valid float that is evaluated to 0 when converted to int
    with pytest.raises(ValueError, match="scroll click pattern values must be > 0"):
        _scroll_clicks_sequence([0.5, 2.0])

def test_scroll_clicks_sequence_string_conversion():
    # Valid strings should be converted to ints
    seq = _scroll_clicks_sequence(["1", "2"])
    assert list(islice(seq, 3)) == [1, 2, 1]

    # Invalid strings should raise ValueError due to int conversion
    with pytest.raises(ValueError):
        _scroll_clicks_sequence(["a"])
