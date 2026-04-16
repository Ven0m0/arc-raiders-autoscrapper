<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-15 | Updated: 2026-04-15 -->

# scanner/

## Purpose
Scan engine, page loop, action execution, and reporting. Orchestrates the full scan flow: capture → OCR → decision → action (or dry-run skip). Runs in a background thread while the TUI renders on the main thread.

## Key Files

| File | Description |
|------|-------------|
| `scan_loop.py` | `scan_pages()` — main page loop. Iterates inventory pages, calls OCR, resolves actions, dispatches input. Resets OCR caches at start. |
| `engine.py` | `ScanEngine` — high-level controller. Starts/stops the scan thread, holds the stop event. |
| `actions.py` | Action execution: right-click, context menu selection, key press sequences for sell/recycle/keep. |
| `cli.py` | `autoscrapper scan` CLI entry point. Parses `--dry-run` and other flags. |
| `outcomes.py` | `ScanOutcome` enum and outcome accumulator. |
| `progress.py` | Scan progress tracking (items scanned, actions taken, errors). |
| `report.py` | End-of-scan report formatting (plain text and Rich-formatted). |
| `rich_support.py` | Rich console helpers for live scan output. |
| `live_ui.py` | Optional live Rich UI shown during scan (non-TUI mode). |
| `types.py` | Shared types: `Cell`, `ItemActionResult`, `PageState`. |
| `__init__.py` | Package init — no side effects. |

## For AI Agents

### Working In This Directory
- `scan_pages()` calls `reset_ocr_caches()` at the top — never remove this; stale cache causes same-item-on-every-slot bugs.
- `--dry-run` disables all `input_driver` calls in `actions.py`. Always test with `--dry-run` against a live window before enabling live clicks.
- Page detection state transitions are in `scan_loop.py` — bugs here cause `infobox not found` or timeout failures.
- `scan_loop.py` and `interaction/` are tightly coupled; changes in grid detection constants may require updates here.

### Testing Requirements
- `tests/autoscrapper/scanner/test_scan_loop.py`
- `tests/autoscrapper/scanner/test_engine.py`
- `tests/autoscrapper/scanner/test_report.py`
- `tests/autoscrapper/scanner/test_detect_empty.py`
- Run: `uv run pytest tests/autoscrapper/scanner/ -x -q`
- Live validation: `uv run autoscrapper scan --dry-run`

### Common Patterns
- `Cell` carries `(page, row, col)` plus capture-space bbox — never mix up row/col order.
- `ScanOutcome.SKIP_UNLISTED` means OCR read a name but no rule matched — check rule store and fuzzy threshold.
- `ScanOutcome.SKIP_EMPTY` means the slot appeared empty — expected for grid edge cells.

## Dependencies

### Internal
- `src/autoscrapper/ocr/inventory_vision.py` — item name and action OCR
- `src/autoscrapper/interaction/` — grid detection and input dispatch
- `src/autoscrapper/core/item_actions.py` — action resolution
- `src/autoscrapper/items/rules_store.py` — rule loading
- `src/autoscrapper/progress/decision_engine.py` — progress-based overrides

### External
- `rich` — console output formatting
