import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from autoscrapper.interaction.inventory_grid import _detect_cells_by_contours
from autoscrapper.ocr import inventory_vision as vision
from autoscrapper.ocr import tesseract as ocr


class OcrCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        image = Image.new("RGB", (600, 140), "white")
        ImageDraw.Draw(image).text(
            (20, 35),
            "ARC RAIDERS 123",
            font=ImageFont.load_default(size=48),
            fill="black",
        )
        cls.bgr = np.asarray(image)[:, :, ::-1].copy()

    def test_recognition_and_word_coordinates(self):
        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(self._check_recognition_and_word_coordinates).result()

    def _check_recognition_and_word_coordinates(self):
        self.assertIn("eng", ocr.initialize_ocr().languages)
        gray = vision.preprocess_for_ocr(self.bgr)
        self.assertEqual(gray.shape, (140, 600))
        self.assertEqual(set(np.unique(gray)), {0, 255})
        bgra = cv2.cvtColor(self.bgr, cv2.COLOR_BGR2BGRA)
        for image in (self.bgr, gray, bgra):
            with self.subTest(shape=image.shape):
                text = ocr.image_to_string(image)
                self.assertIn("ARC", text)
                self.assertIn("123", text)

        data = ocr.image_to_data(self.bgr)
        self.assertIn("ARC", data["text"])
        count = len(data["text"])
        self.assertTrue(all(len(values) == count for values in data.values()))
        for index in range(count):
            self.assertGreater(float(data["conf"][index]), 0)
            x, y = data["left"][index], data["top"][index]
            width, height = data["width"][index], data["height"][index]
            self.assertGreater(width, 0)
            self.assertGreater(height, 0)
            self.assertTrue(0 <= x < x + width <= 600)
            self.assertTrue(0 <= y < y + height <= 140)

    def test_infobox_and_inventory_cell_detection(self):
        self.assertTrue(vision.is_slot_empty(np.zeros((100, 100, 3), np.uint8)))
        self.assertFalse(vision.is_slot_empty(self.bgr))

        scene = np.zeros((400, 500, 3), np.uint8)
        scene[50:350, 100:400] = vision.INFOBOX_COLOR_BGR
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(vision, "_OCR_DEBUG_DIR", Path(directory)):
                panel = vision.find_infobox_with_debug(scene)
                self.assertIsNotNone(panel.rect)
                x, y, width, height = panel.rect
                self.assertTrue(x < 250 < x + width)
                self.assertTrue(y < 200 < y + height)
                self.assertTrue(list(Path(directory).glob("*.png")))

        cells = np.zeros((300, 300, 3), np.uint8)
        cv2.rectangle(cells, (20, 20), (115, 115), (255, 255, 255), 2)
        detected = _detect_cells_by_contours(cells, 95)
        self.assertTrue(detected)
        self.assertTrue(
            any(
                cell["x"] < 65 < cell["x"] + cell["w"]
                and cell["y"] < 65 < cell["y"] + cell["h"]
                for cell in detected
            )
        )
