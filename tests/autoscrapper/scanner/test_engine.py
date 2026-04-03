import sys
from unittest.mock import MagicMock
import pytest

# Mock UI dependencies to prevent display/X11 errors in tests
sys.modules['pywinctl'] = MagicMock()
sys.modules['mss'] = MagicMock()
sys.modules['pynput'] = MagicMock()
sys.modules['pynput.keyboard'] = MagicMock()
sys.modules['pynput.mouse'] = MagicMock()

# ruff: noqa: E402
from autoscrapper.scanner.engine import _validate_scan_args

def test_validate_scan_args_valid():
    """Test _validate_scan_args with valid minimum threshold values."""
    _validate_scan_args(
        infobox_retries=1,
        infobox_retry_interval_ms=0,
        ocr_unreadable_retries=0,
        ocr_retry_interval_ms=0,
        input_action_delay_ms=0,
        cell_infobox_left_right_click_gap_ms=0,
        item_infobox_settle_delay_ms=0,
        post_sell_recycle_delay_ms=0,
        pages=None,
    )

    # Test with valid 'pages' value
    _validate_scan_args(
        infobox_retries=5,
        infobox_retry_interval_ms=10,
        ocr_unreadable_retries=10,
        ocr_retry_interval_ms=10,
        input_action_delay_ms=10,
        cell_infobox_left_right_click_gap_ms=10,
        item_infobox_settle_delay_ms=10,
        post_sell_recycle_delay_ms=10,
        pages=1,
    )

def test_validate_scan_args_invalid_infobox_retries():
    with pytest.raises(ValueError, match="infobox_retries must be >= 1"):
        _validate_scan_args(
            infobox_retries=0,
            infobox_retry_interval_ms=0,
            ocr_unreadable_retries=0,
            ocr_retry_interval_ms=0,
            input_action_delay_ms=0,
            cell_infobox_left_right_click_gap_ms=0,
            item_infobox_settle_delay_ms=0,
            post_sell_recycle_delay_ms=0,
            pages=None,
        )

def test_validate_scan_args_invalid_infobox_retry_interval_ms():
    with pytest.raises(ValueError, match="infobox_retry_interval_ms must be >= 0"):
        _validate_scan_args(
            infobox_retries=1,
            infobox_retry_interval_ms=-1,
            ocr_unreadable_retries=0,
            ocr_retry_interval_ms=0,
            input_action_delay_ms=0,
            cell_infobox_left_right_click_gap_ms=0,
            item_infobox_settle_delay_ms=0,
            post_sell_recycle_delay_ms=0,
            pages=None,
        )

def test_validate_scan_args_invalid_ocr_unreadable_retries():
    with pytest.raises(ValueError, match="ocr_unreadable_retries must be >= 0"):
        _validate_scan_args(
            infobox_retries=1,
            infobox_retry_interval_ms=0,
            ocr_unreadable_retries=-1,
            ocr_retry_interval_ms=0,
            input_action_delay_ms=0,
            cell_infobox_left_right_click_gap_ms=0,
            item_infobox_settle_delay_ms=0,
            post_sell_recycle_delay_ms=0,
            pages=None,
        )

def test_validate_scan_args_invalid_ocr_retry_interval_ms():
    with pytest.raises(ValueError, match="ocr_retry_interval_ms must be >= 0"):
        _validate_scan_args(
            infobox_retries=1,
            infobox_retry_interval_ms=0,
            ocr_unreadable_retries=0,
            ocr_retry_interval_ms=-1,
            input_action_delay_ms=0,
            cell_infobox_left_right_click_gap_ms=0,
            item_infobox_settle_delay_ms=0,
            post_sell_recycle_delay_ms=0,
            pages=None,
        )

def test_validate_scan_args_invalid_input_action_delay_ms():
    with pytest.raises(ValueError, match="input_action_delay_ms must be >= 0"):
        _validate_scan_args(
            infobox_retries=1,
            infobox_retry_interval_ms=0,
            ocr_unreadable_retries=0,
            ocr_retry_interval_ms=0,
            input_action_delay_ms=-1,
            cell_infobox_left_right_click_gap_ms=0,
            item_infobox_settle_delay_ms=0,
            post_sell_recycle_delay_ms=0,
            pages=None,
        )

def test_validate_scan_args_invalid_cell_infobox_left_right_click_gap_ms():
    with pytest.raises(ValueError, match="cell_infobox_left_right_click_gap_ms must be >= 0"):
        _validate_scan_args(
            infobox_retries=1,
            infobox_retry_interval_ms=0,
            ocr_unreadable_retries=0,
            ocr_retry_interval_ms=0,
            input_action_delay_ms=0,
            cell_infobox_left_right_click_gap_ms=-1,
            item_infobox_settle_delay_ms=0,
            post_sell_recycle_delay_ms=0,
            pages=None,
        )

def test_validate_scan_args_invalid_item_infobox_settle_delay_ms():
    with pytest.raises(ValueError, match="item_infobox_settle_delay_ms must be >= 0"):
        _validate_scan_args(
            infobox_retries=1,
            infobox_retry_interval_ms=0,
            ocr_unreadable_retries=0,
            ocr_retry_interval_ms=0,
            input_action_delay_ms=0,
            cell_infobox_left_right_click_gap_ms=0,
            item_infobox_settle_delay_ms=-1,
            post_sell_recycle_delay_ms=0,
            pages=None,
        )

def test_validate_scan_args_invalid_post_sell_recycle_delay_ms():
    with pytest.raises(ValueError, match="post_sell_recycle_delay_ms must be >= 0"):
        _validate_scan_args(
            infobox_retries=1,
            infobox_retry_interval_ms=0,
            ocr_unreadable_retries=0,
            ocr_retry_interval_ms=0,
            input_action_delay_ms=0,
            cell_infobox_left_right_click_gap_ms=0,
            item_infobox_settle_delay_ms=0,
            post_sell_recycle_delay_ms=-1,
            pages=None,
        )

def test_validate_scan_args_invalid_pages():
    with pytest.raises(ValueError, match="pages must be >= 1"):
        _validate_scan_args(
            infobox_retries=1,
            infobox_retry_interval_ms=0,
            ocr_unreadable_retries=0,
            ocr_retry_interval_ms=0,
            input_action_delay_ms=0,
            cell_infobox_left_right_click_gap_ms=0,
            item_infobox_settle_delay_ms=0,
            post_sell_recycle_delay_ms=0,
            pages=0,
        )
    with pytest.raises(ValueError, match="pages must be >= 1"):
        _validate_scan_args(
            infobox_retries=1,
            infobox_retry_interval_ms=0,
            ocr_unreadable_retries=0,
            ocr_retry_interval_ms=0,
            input_action_delay_ms=0,
            cell_infobox_left_right_click_gap_ms=0,
            item_infobox_settle_delay_ms=0,
            post_sell_recycle_delay_ms=0,
            pages=-1,
        )
