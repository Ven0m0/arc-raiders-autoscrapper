"""Tests for _detect_consecutive_empty_stop_idx — prev_empty regression."""

import sys
from dataclasses import dataclass
from typing import Tuple
from unittest.mock import MagicMock, patch

import numpy as np

# ---------------------------------------------------------------------------
# Stub platform deps before importing scanner modules
# ---------------------------------------------------------------------------
sys.modules.setdefault("pywinctl", MagicMock())
sys.modules.setdefault("pymonctl", MagicMock())
sys.modules.setdefault("pynput", MagicMock())
sys.modules.setdefault("pynput.keyboard", MagicMock())
sys.modules.setdefault("pynput.mouse", MagicMock())

from autoscrapper.scanner.scan_loop import _detect_consecutive_empty_stop_idx  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@dataclass
class _Cell:
    index: int
    safe_rect: Tuple[int, int, int, int]


_WINDOW = np.zeros((50, 50, 3), dtype=np.uint8)


def _run(page, cells, cells_per_page, *, is_empty_seq, window=_WINDOW):
    """Run the function with all platform calls mocked."""
    call_iter = iter(is_empty_seq)

    def _is_empty(_bgr):  # noqa: ARG001
        return next(call_iter)

    with (
        patch("autoscrapper.scanner.scan_loop.capture_region", return_value=window),
        patch("autoscrapper.scanner.scan_loop.move_absolute"),
        patch("autoscrapper.scanner.scan_loop.pause_action"),
        patch("autoscrapper.scanner.scan_loop.abort_if_escape_pressed"),
        patch("autoscrapper.scanner.scan_loop.is_slot_empty", side_effect=_is_empty),
    ):
        return _detect_consecutive_empty_stop_idx(
            page,
            cells,
            cells_per_page,
            0,
            0,
            50,
            50,  # window_left, window_top, window_width, window_height
            (0, 0),  # safe_point_abs
            "esc",  # stop_key
            0.0,  # action_delay
        )


# ---------------------------------------------------------------------------
# Bug-fix regression: zero-size crop must reset prev_empty
# ---------------------------------------------------------------------------


class TestZeroSizeCropResetsPrevEmpty:
    """Verifies the fix: prev_empty = False on zero-size crop.

    Without the fix, an empty reading before a zero-size gap carries over and
    causes a false stop when the next valid cell is also empty.
    """

    def test_no_false_stop_after_zero_size_gap(self):
        """empty → [zero-size gap] → empty  must NOT trigger a stop."""
        cells = [
            _Cell(index=0, safe_rect=(0, 0, 10, 10)),  # valid → empty
            _Cell(index=1, safe_rect=(0, 100, 10, 10)),  # y=100 > 50 → zero-size
            _Cell(index=2, safe_rect=(10, 0, 10, 10)),  # valid → empty
        ]
        # is_slot_empty called only for cells 0 and 2
        result = _run(0, cells, 20, is_empty_seq=[True, True])

        assert result is None, (
            "A zero-size crop between two empty cells must reset prev_empty "
            "so the second empty cell is not treated as a consecutive pair"
        )

    def test_false_stop_would_occur_without_fix(self):
        """Illustrate the pre-fix behaviour: stop wrongly fires at index 2.

        We replicate the broken logic manually to document the invariant.
        """
        cells = [
            _Cell(index=0, safe_rect=(0, 0, 10, 10)),
            _Cell(index=1, safe_rect=(0, 100, 10, 10)),  # zero-size
            _Cell(index=2, safe_rect=(10, 0, 10, 10)),
        ]
        page, cells_per_page = 0, 20
        window = _WINDOW

        # Pre-fix logic: no prev_empty reset on zero-size
        prev_empty = False
        result = None
        call_iter = iter([True, True])
        for cell in cells:
            x, y, w, h = cell.safe_rect
            slot = window[y : y + h, x : x + w]
            if slot.size == 0:
                continue  # pre-fix: prev_empty not reset
            is_empty = next(call_iter)
            if is_empty and prev_empty:
                result = page * cells_per_page + cell.index
                break
            prev_empty = is_empty

        assert result == 2, "Pre-fix logic incorrectly returns 2"


# ---------------------------------------------------------------------------
# Correct stop detection (normal cases)
# ---------------------------------------------------------------------------


class TestNormalStopDetection:
    def test_two_consecutive_empty_returns_second_index(self):
        cells = [
            _Cell(index=0, safe_rect=(0, 0, 10, 10)),  # not empty
            _Cell(index=1, safe_rect=(10, 0, 10, 10)),  # empty
            _Cell(index=2, safe_rect=(20, 0, 10, 10)),  # empty → stop
        ]
        result = _run(0, cells, 20, is_empty_seq=[False, True, True])
        assert result == 2

    def test_page_offset_applied_to_result(self):
        cells = [
            _Cell(index=0, safe_rect=(0, 0, 10, 10)),  # empty
            _Cell(index=1, safe_rect=(10, 0, 10, 10)),  # empty → stop
        ]
        result = _run(2, cells, 10, is_empty_seq=[True, True])
        assert result == 2 * 10 + 1  # = 21

    def test_no_consecutive_empty_returns_none(self):
        cells = [
            _Cell(index=0, safe_rect=(0, 0, 10, 10)),
            _Cell(index=1, safe_rect=(10, 0, 10, 10)),
            _Cell(index=2, safe_rect=(20, 0, 10, 10)),
        ]
        result = _run(0, cells, 20, is_empty_seq=[False, True, False])
        assert result is None

    def test_all_filled_returns_none(self):
        cells = [_Cell(index=i, safe_rect=(i * 10, 0, 10, 10)) for i in range(3)]
        result = _run(0, cells, 20, is_empty_seq=[False, False, False])
        assert result is None

    def test_empty_cell_list_returns_none(self):
        result = _run(0, [], 20, is_empty_seq=[])
        assert result is None

    def test_all_zero_size_crops_returns_none(self):
        """All cells produce zero-size crops → prev_empty stays False, no stop."""
        cells = [_Cell(index=i, safe_rect=(0, 100, 10, 10)) for i in range(4)]
        result = _run(0, cells, 20, is_empty_seq=[])
        assert result is None
