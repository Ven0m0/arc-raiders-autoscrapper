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
    ItemNameMatchResult,
    _extract_cropped_title_from_data,
    _extract_title_from_data,
    find_context_menu_crop,
    ocr_inventory_count,
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

    By default all words share page/block/par/line = 1 so they form a single
    group. Pass a 5th tuple value to override line_num for multi-line tests.
    """
    keys = ["text", "conf", "top", "height", "page_num", "block_num", "par_num", "line_num"]
    result = {k: [] for k in keys}
    for word in words:
        if len(word) == 4:
            text, conf, top, height = word
            line_num = 1
        else:
            text, conf, top, height, line_num = word
        result["text"].append(text)
        result["conf"].append(conf)
        result["top"].append(top)
        result["height"].append(height)
        result["page_num"].append(1)
        result["block_num"].append(1)
        result["par_num"].append(1)
        result["line_num"].append(line_num)
    return result


def _match_result(
    cleaned_text: str,
    *,
    chosen_name: str | None = None,
    matched_name: str | None = None,
    threshold: int = 75,
) -> ItemNameMatchResult:
    return ItemNameMatchResult(
        cleaned_text=cleaned_text,
        chosen_name=cleaned_text if chosen_name is None else chosen_name,
        matched_name=matched_name,
        threshold=threshold,
    )


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
        with patch.object(
            _vision,
            "match_item_name_result",
            return_value=_match_result("Hello", chosen_name="Hello", matched_name="Hello"),
        ):
            _, raw = _extract_title_from_data(data, image_height=40, top_fraction=0.5)
        assert "Hello" in raw

    def test_word_in_lower_half_excluded(self):
        """A word whose center_y exceeds the cutoff is filtered out."""
        # 2x image height = 40; top_fraction = 0.5 → cutoff = 20
        # Word at top=16, height=10 → center_y = 21 > 20 → excluded
        data = _make_ocr_data(("Hidden", 90, 16, 10))
        with patch.object(
            _vision,
            "match_item_name_result",
            return_value=_match_result("", chosen_name=""),
        ):
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
        with patch.object(
            _vision,
            "match_item_name_result",
            return_value=_match_result("Arc", chosen_name="Arc", matched_name="Arc"),
        ):
            _, raw_2x = _extract_title_from_data(data, image_height=40, top_fraction=0.5)
            _, raw_orig = _extract_title_from_data(data, image_height=20, top_fraction=0.5)
        assert "Arc" in raw_2x, "2x height should include word in lower portion"
        assert "Arc" not in raw_orig, "original height cutoff would incorrectly drop the word"

    def test_empty_data_returns_empty_strings(self):
        assert _extract_title_from_data({}, image_height=40) == ("", "")

    def test_no_texts_returns_empty_strings(self):
        data = _make_ocr_data()
        with patch.object(
            _vision,
            "match_item_name_result",
            return_value=_match_result("", chosen_name=""),
        ):
            result = _extract_title_from_data(data, image_height=40)
        assert result == ("", "")

    def test_stat_line_uses_lower_priority_known_item_fallback(self):
        data = _make_ocr_data(
            ("Damage", 95, 2, 8, 1),
            ("55", 95, 2, 8, 1),
            ("Arc Alloy", 80, 14, 8, 2),
        )

        def _fake_match(text: str) -> ItemNameMatchResult:
            if text == "Damage 55":
                return _match_result("Damage 55")
            if text == "Range 100":
                return _match_result("Range 100")
            if text == "Arc Alloy":
                return _match_result(
                    "Arc Alloy",
                    chosen_name="Arc Alloy",
                    matched_name="Arc Alloy",
                )
            raise AssertionError(f"unexpected OCR text: {text}")

        with patch.object(_vision, "match_item_name_result", side_effect=_fake_match):
            item_name, raw = _extract_title_from_data(data, image_height=120)

        assert item_name == "Arc Alloy"
        assert raw == "Arc Alloy"

    def test_unmatched_non_stat_line_does_not_trigger_fallback(self):
        data = _make_ocr_data(
            ("Arc Allov", 95, 2, 8, 1),
            ("Random Text", 80, 14, 8, 2),
        )

        def _fake_match(text: str) -> ItemNameMatchResult:
            if text == "Arc Allov":
                return _match_result("Arc Allov", chosen_name="Arc Allov")
            if text == "Random Text":
                return _match_result("Random Text", chosen_name="Random Text")
            raise AssertionError(f"unexpected OCR text: {text}")

        with patch.object(_vision, "match_item_name_result", side_effect=_fake_match):
            item_name, raw = _extract_title_from_data(data, image_height=120)

        assert item_name == "Arc Allov"
        assert raw == "Arc Allov"

    def test_fallback_skips_multiple_stat_lines_before_known_item(self):
        data = _make_ocr_data(
            ("Damage", 95, 2, 8, 1),
            ("55", 95, 2, 8, 1),
            ("Range", 90, 12, 8, 2),
            ("100", 90, 12, 8, 2),
            ("Arc Alloy", 80, 22, 8, 3),
        )

        def _fake_match(text: str) -> ItemNameMatchResult:
            if text == "Damage 55":
                return _match_result("Damage 55")
            if text == "Range 100":
                return _match_result("Range 100")
            if text == "Arc Alloy":
                return _match_result(
                    "Arc Alloy",
                    chosen_name="Arc Alloy",
                    matched_name="Arc Alloy",
                )
            raise AssertionError(f"unexpected OCR text: {text}")

        with patch.object(_vision, "match_item_name_result", side_effect=_fake_match):
            item_name, raw = _extract_title_from_data(data, image_height=120)

        assert item_name == "Arc Alloy"
        assert raw == "Arc Alloy"


# ---------------------------------------------------------------------------
# _extract_cropped_title_from_data — delegates with top_fraction=1.0
# ---------------------------------------------------------------------------


class TestExtractCroppedTitleFromData:
    def test_top_fraction_one_includes_all_words(self):
        """top_fraction=1.0 means the cutoff equals image_height — all words pass."""
        # center_y = top + height/2 = 30 + 5 = 35; image_height = 40; cutoff = 40 → passes
        data = _make_ocr_data(("Alloy", 90, 30, 10))
        with patch.object(
            _vision,
            "match_item_name_result",
            return_value=_match_result("Alloy", chosen_name="Alloy", matched_name="Alloy"),
        ):
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
        # no words → item_name will be ""

        with (
            patch.object(_vision, "image_to_string", return_value="") as mock_ocr,
            patch.object(
                _vision,
                "match_item_name_result",
                return_value=_match_result("", chosen_name=""),
            ),
        ):
            _vision.ocr_title_strip(img)
            _vision.ocr_title_strip(img)  # same image

        # Each ocr_title_strip call makes 2 image_to_string calls when empty:
        # once with upscale, once without (no-upscale fallback). 2 × 2 = 4.
        assert mock_ocr.call_count == 4, (
            "image_to_string called 4 times: 2 per invocation (upscale + no-upscale fallback)"
        )

    def test_non_empty_result_is_cached(self):
        """When item_name is non-empty, the second call must use the cache."""
        reset_ocr_caches()
        img = self._make_image()

        with (
            patch.object(_vision, "image_to_string", return_value="FoundItem") as mock_ocr,
            patch.object(
                _vision,
                "match_item_name_result",
                return_value=_match_result(
                    "Arc Alloy",
                    chosen_name="Arc Alloy",
                    matched_name="Arc Alloy",
                ),
            ),
        ):
            _vision.ocr_title_strip(img)
            _vision.ocr_title_strip(img)  # same image — should hit cache

        assert mock_ocr.call_count == 1, "image_to_data should only be called once when result was cached"


# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# ocr_item_name — cache tests
# ---------------------------------------------------------------------------


class TestOcrItemNameCache:
    def _make_image(self):
        return _solid_bgr(30, 100)

    def test_empty_result_not_cached(self):
        reset_ocr_caches()
        img = self._make_image()

        with patch.object(_vision, "image_to_string", return_value="") as mock_ocr:
            _vision.ocr_item_name(img)
            _vision.ocr_item_name(img)

        assert mock_ocr.call_count == 2, "image_to_string should be called twice when the first result was empty"

    def test_non_empty_result_is_cached(self):
        reset_ocr_caches()
        img = self._make_image()

        with (
            patch.object(_vision, "image_to_string", return_value="FoundItem") as mock_ocr,
            patch.object(
                _vision,
                "match_item_name",
                return_value="Arc Alloy",
            ),
        ):
            _vision.ocr_item_name(img)
            _vision.ocr_item_name(img)

        assert mock_ocr.call_count == 1, "image_to_string should only be called once when result was cached"


# reset_ocr_caches
# ---------------------------------------------------------------------------


class TestResetOcrCaches:
    def test_clears_all_three_caches(self):
        # Prime the caches artificially
        _vision._last_roi_hash = b"fake"
        _vision._last_ocr_result = ("Item", "Item")
        _vision.rules_store._ITEM_NAMES = ("Item A", "Item B")

        reset_ocr_caches()

        assert _vision._last_roi_hash is None
        assert _vision._last_ocr_result is None
        assert _vision.rules_store._ITEM_NAMES is None


# ---------------------------------------------------------------------------
# enable_ocr_debug
# ---------------------------------------------------------------------------


class TestEnableOcrDebug:
    def test_enable_ocr_debug_success(self, tmp_path):
        """Test that enable_ocr_debug sets the debug directory and creates it."""
        debug_dir = tmp_path / "ocr_debug"
        original_dir = _vision._OCR_DEBUG_DIR
        try:
            _vision.enable_ocr_debug(debug_dir)
            assert _vision._OCR_DEBUG_DIR == debug_dir
            assert debug_dir.exists()
        finally:
            _vision._OCR_DEBUG_DIR = original_dir

    def test_enable_ocr_debug_mkdir_exception(self, capsys):
        """Test that an exception during directory creation is caught and handled."""
        from pathlib import Path

        mock_path = MagicMock(spec=Path)
        mock_path.mkdir.side_effect = OSError("Permission denied")

        # Use patch to isolate global state and verify it is cleared on failure
        with patch.object(_vision, "_OCR_DEBUG_DIR", Path("/tmp/dummy")):
            _vision.enable_ocr_debug(mock_path)
            assert _vision._OCR_DEBUG_DIR is None

        captured = capsys.readouterr()
        assert "[vision_ocr] failed to enable OCR debug dir: Permission denied" in captured.out


# ---------------------------------------------------------------------------
# ocr_inventory_count — regression tests for the phantom-digit fix
# ---------------------------------------------------------------------------


class TestOcrInventoryCount:
    """Tests for ocr_inventory_count() focusing on the N/M artifact-stripping logic."""

    def _call(self, ocr_text: str):
        """Call ocr_inventory_count with a real dummy image but mocked OCR output."""
        img = _solid_bgr(20, 80)
        with patch("autoscrapper.ocr.inventory_vision.image_to_string", return_value=ocr_text):
            return ocr_inventory_count(img)

    def test_normal_count(self):
        count, raw = self._call("197/232")
        assert count == 197
        assert "197/232" in raw

    def test_current_equals_capacity(self):
        """Full stash — current == capacity is valid."""
        count, _ = self._call("280/280")
        assert count == 280

    def test_phantom_leading_digit_stripped(self):
        """Regression: OCR reads '2251/280'; should recover to 251."""
        count, _ = self._call("2251/280")
        assert count == 251

    def test_artifact_not_stripped_when_same_digit_length(self, capsys):
        """'999/280': same digit length as capacity — no strip, returns None + logs."""
        count, _ = self._call("999/280")
        assert count is None
        out = capsys.readouterr().out
        assert "[vision_ocr] ocr_inventory_count: unrecoverable count" in out

    def test_artifact_not_stripped_when_two_surplus_digits(self, capsys):
        """'22251/280': two surplus digits — conservative, no strip, returns None."""
        count, _ = self._call("22251/280")
        assert count is None
        capsys.readouterr()  # consume log

    def test_no_slash_pattern_falls_through_to_digit_fallback(self):
        """No N/M pattern — falls through to digit extraction path."""
        count, _ = self._call("251")
        assert count == 251

    def test_empty_roi_returns_none(self):
        empty = np.zeros((0, 0, 3), dtype=np.uint8)
        count, raw = ocr_inventory_count(empty)
        assert count is None
        assert raw == ""

    def test_no_digits_returns_none(self):
        count, _ = self._call("no digits here")
        assert count is None


# ---------------------------------------------------------------------------
# find_context_menu_crop — right-edge geometry regression (Bug: title clipped)
# ---------------------------------------------------------------------------


class TestFindContextMenuCrop:
    """Regression tests ensuring the context-menu crop reaches far enough right.

    Root cause: _CONTEXT_MENU_X_OFFSET_NORM was 35/1920 (≈35 px at 1080p),
    so right edge = cell_center_x + 35.  Item titles like "MATRIARCH REACTOR"
    extend ~200-250 px past the cell centre — they were clipped, causing
    title-unreadable / UNAVAILABLE outcomes.

    Fix: X_OFFSET_NORM → 250/1920, WIDTH_NORM → 635/1920.
    The right edge must now be ≥ 200 px past cell_center_x.
    """

    _W = 1920
    _H = 1080

    def _solid(self):
        """Return a non-black 1920×1080 image so brightness guard passes."""
        return np.full((self._H, self._W, 3), 80, dtype=np.uint8)

    def _crop(self, cx: int, cy: int):
        img = self._solid()
        return find_context_menu_crop(img, cx, cy)

    def test_right_edge_extends_at_least_200px_past_cell_centre(self):
        """Right edge of crop must be ≥ 200 px past cell_center_x."""
        cx, cy = 800, 540
        result = self._crop(cx, cy)
        assert result is not None, "crop should succeed on a bright image"
        x, _, w, _ = result
        right_edge = x + w
        assert right_edge >= cx + 200, (
            f"right edge {right_edge} is only {right_edge - cx} px past centre {cx}; title text will be clipped"
        )

    def test_right_edge_extends_at_least_200px_near_left_screen(self):
        """Same geometry holds when cell is near the left screen edge."""
        cx, cy = 200, 300
        result = self._crop(cx, cy)
        assert result is not None
        x, _, w, _ = result
        right_edge = x + w
        # Crop is clamped to screen, but must still extend past centre
        assert right_edge >= cx + 200 or right_edge == self._W, (
            "right edge must reach 200 px past centre or be clamped to screen width"
        )

    def test_crop_stays_within_image_bounds(self):
        """Crop rectangle must not exceed image dimensions."""
        for cx, cy in [(100, 100), (960, 540), (1800, 900)]:
            result = self._crop(cx, cy)
            if result is None:
                continue
            x, y, w, h = result
            assert x >= 0 and y >= 0
            assert x + w <= self._W
            assert y + h <= self._H

    def test_returns_none_on_dark_image(self):
        """Polarity guard: black image (mean < 40) should return None."""
        dark = np.zeros((self._H, self._W, 3), dtype=np.uint8)
        result = find_context_menu_crop(dark, 800, 540)
        assert result is None, "dark crop should be rejected by brightness guard"

    def test_crop_width_large_enough_for_long_titles(self):
        """Crop width must be ≥ 550 px (at 1920) to fit 'MATRIARCH REACTOR' text."""
        result = self._crop(800, 540)
        assert result is not None
        _, _, w, _ = result
        assert w >= 550, f"crop width {w} is too narrow for long item titles"
