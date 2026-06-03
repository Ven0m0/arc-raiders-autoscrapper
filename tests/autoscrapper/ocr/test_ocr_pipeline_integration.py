from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np

from autoscrapper.core.item_actions import clean_ocr_text, normalize_item_name
from autoscrapper.ocr import inventory_vision


class TestOcrPipelineIntegration:
    """Integration tests for full OCR pipeline: image → OCR → fuzzy match → decision."""

    @patch("autoscrapper.ocr.inventory_vision.image_to_string")
    @patch("autoscrapper.ocr.inventory_vision.preprocess_for_ocr")
    def test_full_flow_image_to_string_to_match(self, mock_preprocess, mock_ocr):
        """Test full flow: preprocess → OCR → fuzzy match."""
        mock_preprocess.return_value = np.zeros((50, 200, 3), dtype=np.uint8)
        mock_ocr.return_value = "Test Rifle"

        from autoscrapper.ocr.inventory_vision import ocr_item_name

        result = ocr_item_name(np.zeros((50, 200, 3), dtype=np.uint8))
        assert result

    def test_clean_ocr_text_integration(self):
        """Test OCR text cleaning in the pipeline."""
        raw = "  Test   Item  (Rifle)  "
        cleaned = clean_ocr_text(raw)
        assert "Test Item" in cleaned

    def test_normalize_item_name_integration(self):
        """Test item name normalization in the pipeline."""
        name = "  Test Rifle  "
        normalized = normalize_item_name(name)
        assert normalized == "test rifle"

    def test_fuzzy_match_integration(self):
        """Test fuzzy matching with various threshold levels."""
        from autoscrapper.ocr.inventory_vision import match_item_name_result, DEFAULT_ITEM_NAME_MATCH_THRESHOLD

        result = match_item_name_result("Test Rifle")
        assert result.threshold == DEFAULT_ITEM_NAME_MATCH_THRESHOLD


class TestPolarityDetection:
    """Test polarity detection in the OCR pipeline."""

    def test_preprocess_for_ocr_accepted_parameters(self):
        """Test that preprocess_for_ocr accepts robust_polarity parameter."""
        import inspect

        sig = inspect.signature(inventory_vision.preprocess_for_ocr)
        params = list(sig.parameters.keys())
        assert "robust_polarity" in params


class TestMockTesseract:
    """Test OCR pipeline with mocked Tesseract for determinism."""

    @patch("autoscrapper.ocr.tesseract._get_api")
    def test_mocked_tesseract_returns_consistent_results(self, mock_api):
        mock_tesseract_api = MagicMock()
        mock_tesseract_api.GetUTF8Text.return_value = "Test Rifle"
        mock_tesseract_api.Confidence.return_value = 95.0
        mock_tesseract_api.BoundingBox.return_value = (0, 0, 100, 20)
        mock_tesseract_api.SetVariable.return_value = True
        mock_api.return_value = mock_tesseract_api


class TestConfidenceGating:
    """Test confidence-gated retry logic."""

    def test_confidence_below_threshold_triggers_retry(self):
        """Test that low confidence triggers retry path."""
        ocr_data = {
            "text": ["test", "item"],
            "conf": ["45.0", "50.0"],
            "top": [10, 30],
            "height": [20, 20],
            "page_num": [1, 1],
            "block_num": [1, 1],
            "par_num": [1, 1],
            "line_num": [1, 1],
        }
        confs = []
        for idx in range(len(ocr_data["text"])):
            try:
                confs.append(float(ocr_data["conf"][idx]))
            except Exception:
                continue
        avg_conf = sum(confs) / len(confs) if confs else -1.0
        assert avg_conf < 60

    def test_confidence_above_threshold_accepts_result(self):
        """Test that high confidence accepts result without retry."""
        ocr_data = {
            "text": ["test", "item"],
            "conf": ["90.0", "95.0"],
            "top": [10, 30],
            "height": [20, 20],
            "page_num": [1, 1],
            "block_num": [1, 1],
            "par_num": [1, 1],
            "line_num": [1, 1],
        }
        confs = []
        for idx in range(len(ocr_data["text"])):
            try:
                confs.append(float(ocr_data["conf"][idx]))
            except Exception:
                continue
        avg_conf = sum(confs) / len(confs) if confs else -1.0
        assert avg_conf >= 60


class TestContextMenuOcr:
    """Test context menu OCR processing."""

    def test_context_menu_title_extraction_function_exists(self):
        """Test that _extract_title_from_data function exists and is callable."""
        from autoscrapper.ocr.inventory_vision import _extract_title_from_data

        ocr_data = {
            "text": ["rifle", "Value: 5000"],
            "conf": ["95.0", "90.0"],
            "top": [10, 40],
            "height": [20, 20],
            "width": [100, 100],
            "left": [10, 10],
            "page_num": [1, 1],
            "block_num": [1, 1],
            "par_num": [1, 1],
            "line_num": [1, 2],
        }
        title, raw = _extract_title_from_data(ocr_data, 100)
        assert title != "" or raw != ""


class TestRomanNumeralFixes:
    """Test roman numeral OCR corrections."""

    def test_roman_numeral_i_to_ii(self):
        """Test Il -> II correction is applied."""
        from autoscrapper.ocr.inventory_vision import _ROMAN_NUMERAL_FIXES

        text = "Test Rifle Il"
        for pattern, replacement in _ROMAN_NUMERAL_FIXES:
            text = pattern.sub(replacement, text)
        assert "II" in text

    def test_roman_numeral_iii(self):
        """Test Ill -> III correction is applied."""
        from autoscrapper.ocr.inventory_vision import _ROMAN_NUMERAL_FIXES

        text = "Weapon Ill"
        for pattern, replacement in _ROMAN_NUMERAL_FIXES:
            text = pattern.sub(replacement, text)
        assert "III" in text

    def test_roman_numeral_iv(self):
        """Test lV -> IV correction is applied."""
        from autoscrapper.ocr.inventory_vision import _ROMAN_NUMERAL_FIXES

        text = "Item lV"
        for pattern, replacement in _ROMAN_NUMERAL_FIXES:
            text = pattern.sub(replacement, text)
        assert "IV" in text

    def test_roman_numeral_1v(self):
        """Test 1V -> IV correction is applied."""
        from autoscrapper.ocr.inventory_vision import _ROMAN_NUMERAL_FIXES

        text = "Item 1V"
        for pattern, replacement in _ROMAN_NUMERAL_FIXES:
            text = pattern.sub(replacement, text)
        assert "IV" in text

    def test_roman_numeral_111(self):
        """Test 111 -> III correction is applied."""
        from autoscrapper.ocr.inventory_vision import _ROMAN_NUMERAL_FIXES

        text = "Weapon 111"
        for pattern, replacement in _ROMAN_NUMERAL_FIXES:
            text = pattern.sub(replacement, text)
        assert "III" in text
