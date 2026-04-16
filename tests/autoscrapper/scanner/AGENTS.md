<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-15 | Updated: 2026-04-15 -->

# tests/autoscrapper/scanner/

## Purpose
Tests for `src/autoscrapper/scanner/` — scan loop behavior, engine lifecycle, report formatting, and empty slot detection.

## Key Files

| File | Description |
|------|-------------|
| `test_scan_loop.py` | Tests for `scan_loop.py`: cache reset on start, page iteration, OCR→action dispatch, dry-run suppression. |
| `test_engine.py` | Tests for `engine.py`: thread start/stop, stop event propagation. |
| `test_report.py` | Tests for `report.py`: outcome counts, report text formatting. |
| `test_detect_empty.py` | Tests for empty slot detection heuristics. |

## For AI Agents

### Working In This Directory
- `test_scan_loop.py` must verify that `reset_ocr_caches()` is called at the top of each scan — this is a critical invariant.
- Mock all `input_driver` calls — tests must never send real input events.
- `--dry-run` behavior must be covered: actions logged but not executed.

### Testing Requirements
Run: `uv run pytest tests/autoscrapper/scanner/ -x -q`
Live validation (not automated): `uv run autoscrapper scan --dry-run`
