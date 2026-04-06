# OCR Reviewer

Specialized reviewer for OCR/scanner changes in Arc Raiders AutoScrapper.

## Review Focus

- Coordinate space consistency (2x-upscaled vs original)
- Upscale artifact detection in preprocessing
- Bounding box division by 2 for coordinate conversion
- Cache reset paths (`_last_roi_hash`, `_last_ocr_result`)

## Files to Review

- `src/autoscrapper/ocr/inventory_vision.py`
- `src/autoscrapper/scanner/`
- `src/autoscrapper/ocr/` modules

## Validation

```bash
uv run autoscrapper scan --dry-run
```
