<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-15 | Updated: 2026-04-15 -->

# tests/autoscrapper/ocr/

## Purpose
Tests for `src/autoscrapper/ocr/` — OCR pipeline, failure corpus schema, Tesseract initialization, and fixture image processing. This is the most active test directory; changes to OCR logic require updating tests here and running corpus replay.

## Key Files

| File | Description |
|------|-------------|
| `test_inventory_vision.py` | Unit tests for `inventory_vision.py`: title strip parsing, context menu OCR, unavailable guard, cache reset, coordinate space conversions. |
| `test_failure_corpus.py` | Tests for `failure_corpus.py`: `OcrFailureSample` schema (version 2), serialization, path traversal guard, capture path defaults. |
| `test_tesseract.py` | Tests for `tesseract.py`: initialization ordering, thread-safety assertions. |
| `test_ocr_fixtures.py` | Fixture image smoke tests — skipped if Tesseract is not installed. |

## For AI Agents

### Working In This Directory
- After any change to `ItemNameMatchResult` field names (`chosen_name`, `matched_name`), update all test assertions that reference those fields.
- `test_failure_corpus.py` must use `schema_version=2` when constructing `OcrFailureSample` directly.
- Fixture image tests are skipped automatically on CI when Tesseract is absent — this is expected.
- The corpus replay is a separate validation step: `uv run python scripts/replay_ocr_failure_corpus.py`

### Testing Requirements
Run: `uv run pytest tests/autoscrapper/ocr/ -x -q`
Full OCR validation: also run corpus replay after threshold/preprocessing changes.
