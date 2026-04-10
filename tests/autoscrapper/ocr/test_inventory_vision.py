"""Tests for ocr/inventory_vision.py — pure functions and bug-fix regressions."""

import sys
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

# ---------------------------------------------------------------------------
# Stub heavy platform deps before any autoscrapper import
# ---------------------------------------------------------------------------
sys.modules.setdefault("pywinctl", MagicMock())
sys.modules.setdefault("pymonctl", MagicMock())
sys.modules.setdefault("pynput", MagicMock())
sys.modules.setdefault("pynput.keyboard", MagicMock())
sys.modules.setdefault("pynput.mouse", MagicMock())

from autoscrapper.ocr.inventory_vision import (  # noqa: E402
    _extract_cropped_title_from_data,
    _extract_title_from_data,
    preprocess_for_ocr,
    reset_ocr_caches,
    title_roi,
)
import autoscrapper.ocr.inventory_vision as _vision  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ocr_data(*words):
    """Build a Tesseract-style data dict from (text, conf, top, height) tuples.

    All words share page/block/par/line = 1 so they form a single group.
    """
    keys = ["text", "conf", "top", "height", "page_num", "block_num", "par_num", "line_num"]
    result = {k: [] for k in keys}
    for text, conf, top, height in words:
        result["text"].append(text)
        result["conf"].append(conf)
        result["top"].append(top)
        result["height"].append(height)
        result["page_num"].append(1)
        result["block_num"].append(1)
        result["par_num"].append(1)
        result["line_num"].append(1)
    return result


def _solid_bgr(h, w, color=(128, 128, 128)):
    img = np.full((h, w, 3), color, dtype=np.uint8)
    return img


# ---------------------------------------------------------------------------
# preprocess_for_ocr — Bug 1 & 2 regression
# ---------------------------------------------------------------------------

class TestPreprocessForOcr:
    def test_zero_size_raises_value_error(self):
        """Bug 1: zero-size input must raise ValueError before cv2 crashes."""
        with pytest.raises(ValueError, match="empty input"):
            preprocess_for_ocr(np.zeros((0, 10, 3), dtype=np.uint8))

    def test_zero_height_raises_value_error(self):
        with pytest.raises(ValueError, match="empty input"):
            preprocess_for_ocr(np.zeros((10, 0, 3), dtype=np.uint8))

    def test_output_is_2x_input_size(self):
        img = _solid_bgr(20, 40)
        out = preprocess_for_ocr(img)
        assert out.shape == (40, 80), f"expected (40,80), got {out.shape}"

    def test_output_is_binary(self):
        img = _solid_bgr(20, 40)
        out = preprocess_for_ocr(img)
        unique = set(np.unique(out).tolist())
        assert unique.issubset({0, 255}), f"non-binary values: {unique - {0, 255}}"

    def test_restrict_otsu_to_left_normal_image(self):
        """restrict_otsu_to_left should not crash on a normal-width image."""
        img = _solid_bgr(20, 40)
        out = preprocess_for_ocr(img, restrict_otsu_to_left=True)
        assert out.shape == (40, 80)

    def test_restrict_otsu_to_left_width_one_input(self):
        """Bug 2: width-1 input (→ w_g=2, half=1) must not crash."""
        img = _solid_bgr(20, 1)
        out = preprocess_for_ocr(img, restrict_otsu_to_left=True)
        assert out.shape == (40, 2)


# ---------------------------------------------------------------------------
# title_roi — pure coordinate math
# ---------------------------------------------------------------------------

class TestTitleRoi:
    def test_returns_same_x_y(self):
        rect = (10, 20, 200, 100)
        x, y, *_ = title_roi(rect)
        assert x == 10
        assert y == 20

    def test_width_preserved(self):
        rect = (0, 0, 300, 80)
        _, _, w, _ = title_roi(rect)
        assert w == 300

    def test_height_is_fraction_of_infobox_height(self):
        from autoscrapper.ocr.inventory_vision import TITLE_HEIGHT_REL
        _, _, _, h_title = title_roi((0, 0, 100, 100))
        assert h_title == max(1, int(TITLE_HEIGHT_REL * 100))

    def test_minimum_height_is_one(self):
        """Very short infobox must still produce height >= 1."""
        _, _, _, h = title_roi((0, 0, 100, 1))
        assert h >= 1


# ---------------------------------------------------------------------------
# _extract_title_from_data — coordinate-space regression (Bug 3 from review 2)
# ---------------------------------------------------------------------------

class TestExtractTitleFromData:
    """Tesseract returns coords in 2x-upscaled space; image_height must match."""

    def test_word_in_upper_half_included(self):
        """A word whose center_y is within the top fraction is kept."""
        # 2x image height = 40; top_fraction = 0.5 → cutoff = 20
        # Word at top=5, height=10 → center_y = 10 ≤ 20 → included
        data = _make_ocr_data(("Hello", 90, 5, 10))
        with patch.object(_vision, "match_item_name", return_value="Hello"):
            _, raw = _extract_title_from_data(data, image_height=40, top_fraction=0.5)
        assert "Hello" in raw

    def test_word_in_lower_half_excluded(self):
        """A word whose center_y exceeds the cutoff is filtered out."""
        # 2x image height = 40; top_fraction = 0.5 → cutoff = 20
        # Word at top=16, height=10 → center_y = 21 > 20 → excluded
        data = _make_ocr_data(("Hidden", 90, 16, 10))
        with patch.object(_vision, "match_item_name", return_value=""):
            _, raw = _extract_title_from_data(data, image_height=40, top_fraction=0.5)
        assert "Hidden" not in raw

    def test_2x_height_keeps_word_original_height_would_drop(self):
        """Demonstrate why image_height must be the 2x height.

        Word at top=8, height=10 → center_y = 13.
        With 2x height (40) and top_fraction 0.5: cutoff=20 → included.
        With original height (20) and top_fraction 0.5: cutoff=10 → excluded.
        Passing processed.shape[0] (2x) is therefore the correct behaviour.
        """
        data = _make_ocr_data(("Arc", 90, 8, 10))
        with patch.object(_vision, "match_item_name", return_value="Arc"):
            _, raw_2x = _extract_title_from_data(data, image_height=40, top_fraction=0.5)
            _, raw_orig = _extract_title_from_data(data, image_height=20, top_fraction=0.5)
        assert "Arc" in raw_2x, "2x height should include word in lower portion"
        assert "Arc" not in raw_orig, "original height cutoff would incorrectly drop the word"

    def test_empty_data_returns_empty_strings(self):
        assert _extract_title_from_data({}, image_height=40) == ("", "")

    def test_no_texts_returns_empty_strings(self):
        data = _make_ocr_data()
        with patch.object(_vision, "match_item_name", return_value=""):
            result = _extract_title_from_data(data, image_height=40)
        assert result == ("", "")


# ---------------------------------------------------------------------------
# _extract_cropped_title_from_data — delegates with top_fraction=1.0
# ---------------------------------------------------------------------------

class TestExtractCroppedTitleFromData:
    def test_top_fraction_one_includes_all_words(self):
        """top_fraction=1.0 means the cutoff equals image_height — all words pass."""
        # center_y = top + height/2 = 30 + 5 = 35; image_height = 40; cutoff = 40 → passes
        data = _make_ocr_data(("Alloy", 90, 30, 10))
        with patch.object(_vision, "match_item_name", return_value="Alloy"):
            _, raw = _extract_cropped_title_from_data(data, image_height=40)
        assert "Alloy" in raw


# ---------------------------------------------------------------------------
# ocr_title_strip — cache does not store empty item_name (Bug 5 regression)
# ---------------------------------------------------------------------------

class TestOcrTitleStripCache:
    def _make_image(self):
        return _solid_bgr(30, 100)

    def test_empty_result_not_cached(self):
        """When item_name is empty, the cache must NOT be updated.

        A subsequent call with the same image must re-invoke image_to_data.
        """
        reset_ocr_caches()
        img = self._make_image()
        empty_data = _make_ocr_data()  # no words → item_name will be ""

        with patch.object(_vision, "image_to_data", return_value=empty_data) as mock_ocr, \
             patch.object(_vision, "match_item_name", return_value=""):
            _vision.ocr_title_strip(img)
            _vision.ocr_title_strip(img)  # same image

        assert mock_ocr.call_count == 2, (
            "image_to_data should be called twice when the first result was empty"
        )

    def test_non_empty_result_is_cached(self):
        """When item_name is non-empty, the second call must use the cache."""
        reset_ocr_caches()
        img = self._make_image()
        data = _make_ocr_data(("Arc Alloy", 90, 2, 8))

        with patch.object(_vision, "image_to_data", return_value=data) as mock_ocr, \
             patch.object(_vision, "match_item_name", return_value="Arc Alloy"):
            _vision.ocr_title_strip(img)
            _vision.ocr_title_strip(img)  # same image — should hit cache

        assert mock_ocr.call_count == 1, (
            "image_to_data should only be called once when result was cached"
        )


# ---------------------------------------------------------------------------
# reset_ocr_caches
# ---------------------------------------------------------------------------

class TestResetOcrCaches:
    def test_clears_all_three_caches(self):
        # Prime the caches artificially
        _vision._last_roi_hash = b"fake"
        _vision._last_ocr_result = ("Item", "Item")
        _vision._ITEM_NAMES = ("Item A", "Item B")

        reset_ocr_caches()

        assert _vision._last_roi_hash is None
        assert _vision._last_ocr_result is None
        assert _vision._ITEM_NAMES is None
