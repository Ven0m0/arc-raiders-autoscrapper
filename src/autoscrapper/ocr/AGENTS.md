<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-15 | Updated: 2026-04-15 -->

# ocr/

## Purpose
Tesseract initialization, image preprocessing, and item/infobox OCR extraction. This is the hottest and most calibration-sensitive module in the codebase (50 commits in 30 days). Changes here require corpus replay validation.

## Key Files

| File | Description |
|------|-------------|
| `inventory_vision.py` | **Primary hotspot.** Infobox detection, title strip OCR, context menu OCR, action bbox detection. Contains all `_CONTEXT_MENU_*` and `_TITLE_STRIP_*` constants. |
| `tesseract.py` | `initialize_ocr()` — must be called on the main thread before the scan thread starts. Wraps `tesserocr` init. |
| `failure_corpus.py` | `OcrFailureSample` dataclass and corpus I/O. Schema version 2. Used by `scripts/capture_ocr_fixture.py` and `scripts/replay_ocr_failure_corpus.py`. |
| `__init__.py` | Package init — no side effects. |

## For AI Agents

### Coordinate Spaces
Two spaces coexist — mixing them is the #1 source of bugs:

- **Original space** — raw window crop dimensions (input to preprocessing)
- **2x-upscaled space** — output of `preprocess_for_ocr()`, passed to Tesseract

Any bbox returned from Tesseract over a 2x image **must be halved** before use in original-space operations. `find_action_bbox_by_ocr` handles this internally.

### Preprocessing Pipeline Order
Must be exactly: `BGR → grayscale → upscale 2x → Otsu binarization → morphological ops → Tesseract`

Binarization must happen **before** morphological ops. Raw BGR must never go to Tesseract.

### Cache State
Module-level caches in `inventory_vision.py`:
- `_last_roi_hash` — skips re-OCR if region unchanged
- `_last_ocr_result` — cached result for current ROI
- `_ITEM_NAMES` — item name list for fuzzy matching

`reset_ocr_caches()` clears all three. Called at the start of `scan_pages()`.

### Unavailable Guard
`ocr_context_menu` rejects any match where `result.matched_name.lower().startswith("unavailable")`. If this recurs, check whether the guard was removed. `_ACTION_PREFIXES` must also include `"unavailable"` as a line-level prefix skip (runs before fuzzy matching).

### Field Naming
`ItemNameMatchResult` has both `chosen_name` (always a string; equals cleaned OCR text on no-match) and `matched_name` (None on no-match). These serve different purposes — do not conflate them.

### Testing Requirements
- `tests/autoscrapper/ocr/test_inventory_vision.py` — unit tests
- `tests/autoscrapper/ocr/test_failure_corpus.py` — corpus schema tests
- `tests/autoscrapper/ocr/test_tesseract.py` — Tesseract init tests
- `tests/autoscrapper/ocr/test_ocr_fixtures.py` — fixture image tests (skipped if Tesseract absent)
- Corpus replay: `uv run python scripts/replay_ocr_failure_corpus.py`

**After any threshold or preprocessing change** — run corpus replay before shipping (T001).

### Common Patterns
- `ocr_title_strip` retries automatically with `upscale=False` when the first pass returns empty.
- Debug images land in `ocr_debug/` (timestamped PNGs) — safe to clear between sessions.
- No-upscale fallback: if debug images show interpolation artefacts on thin strokes, the fallback path is active.

## Dependencies

### Internal
- `src/autoscrapper/interaction/ui_windows.py` — provides the capture frame
- `src/autoscrapper/core/item_actions.py` — consumes `matched_name` for rule lookup

### External
- `tesserocr` — Python wrapper for Tesseract OCR
- `opencv-python-headless` — image preprocessing (grayscale, binarization, morphological ops)
- `Pillow` — image I/O bridge between OpenCV and Tesseract
- `rapidfuzz` — fuzzy item name matching
