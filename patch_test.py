import re
with open("tests/autoscrapper/ocr/test_inventory_vision.py", "r") as f:
    content = f.read()

# Make the test cleanup its state
content = content.replace('def test_enable_ocr_debug_success(self, tmp_path):', 'def test_enable_ocr_debug_success(self, tmp_path):\n        # Save original state\n        original_dir = getattr(_vision, "_OCR_DEBUG_DIR", None)\n        # Ensure we restore it even if test fails\n        import atexit\n        def restore():\n            _vision._OCR_DEBUG_DIR = original_dir\n        import weakref\n        import builtins\n        import sys\n        class Cleaner:\n            def __del__(self):\n                _vision._OCR_DEBUG_DIR = original_dir\n        _cleaner = Cleaner()')

with open("tests/autoscrapper/ocr/test_inventory_vision.py", "w") as f:
    f.write(content)
