# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Does

Arc Raiders AutoScrapper is a screen-capture + OCR automation tool that scans the Arc Raiders game inventory, reads item names via Tesseract, matches them against user-defined rules, and executes sell/recycle actions via mouse/keyboard simulation. It does **not** hook into the game process.

## Commands

```bash
# Setup (after clone)
uv sync

# Run (TUI)
uv run autoscrapper

# Run scanner directly
uv run autoscrapper scan
uv run autoscrapper scan --dry-run   # validate without executing actions

# Lint / format
uv run ruff check src/
uv run ruff format src/

# Tests
uv run pytest                        # all tests
uv run pytest tests/path/to/test_file.py::test_name   # single test

# Pre-commit (runs ruff + other checks)
uv run prek run --all-files

# Refresh game data snapshots and default rules
uv run python scripts/update_snapshot_and_defaults.py
uv run python scripts/update_snapshot_and_defaults.py --dry-run
```

## Architecture

The app has seven modules under `src/autoscrapper/`:

### Scan Pipeline (hot path)

1. **`tui/`** — Textual TUI. `scan.py` (scan screen), `rules.py` (rules editor), `settings.py` (scanner settings), `maintenance.py` (data refresh UI). `scan.py` drives the scanner engine.
2. **`scanner/engine.py`** — Orchestrates a full scan: validates settings, initializes OCR, waits for the game window, loops over pages.
3. **`scanner/scan_loop.py`** — Page-level scanning. For each grid cell: open infobox → OCR → rule lookup → execute action → scroll.
4. **`interaction/`**
   - `ui_windows.py` — Window capture (mss), mouse/keyboard control, infobox open/close, scrolling.
   - `inventory_grid.py` — Contour-based 4×5 grid detection; resolution-agnostic, handles carousel scroll.
   - `input_driver.py` — Platform-specific input (Windows: pydirectinput-rgx; Linux: pynput).
5. **`ocr/`**
   - `tesseract.py` — Thread-safe PyTessBaseAPI wrapper with tessdata auto-discovery.
   - `inventory_vision.py` — Image preprocessing, infobox region detection, item name extraction. **Hottest file (229 edits).**
   - `failure_corpus.py` — OCR error tracking.
6. **`scanner/actions.py`** — Executes the resolved action (sell/recycle keystrokes).

### Rule Engine

- **`core/item_actions.py`** — Loads rules and maps item names → `KEEP | SELL | RECYCLE` decisions using rapidfuzz fuzzy matching.
- **`items/rules_store.py`** — Loads/saves `items_rules.json` (custom file overrides bundled default).
- **`items/rules_diff.py`** — Diffs rule sets.

### Progress / Data Generation

- **`progress/`** — Loads game data snapshots (quests, hideout, crafting), infers quest completion, and **auto-generates default rules** via `rules_generator.py`. Run the updater script after game patches.

### Config

- **`config.py`** — `ScanSettings`, `ProgressSettings`, `UiSettings` dataclasses. Persisted to `~/.AutoScrapper/config.json` (Windows) or `~/.autoscrapper/` (Linux). Config versioning is load-bearing — bump the version constant when adding fields.

## Key Dependencies

| Package | Purpose |
|---|---|
| `tesserocr` | Tesseract OCR bindings |
| `opencv-python-headless` | Image processing for grid/infobox detection |
| `mss` | Fast screen capture |
| `pydirectinput-rgx` / `pynput` | Input simulation (Windows/Linux) |
| `rapidfuzz` | Fuzzy item name matching |
| `textual` | TUI framework |

## Coordinate Spaces

All image coordinates are in **capture-space pixels** (the raw screenshot dimensions). The grid detector works in this space. Do not mix with screen-space coordinates used by the input driver — `ui_windows.py` handles the translation.

## Context Menu Geometry

The dark context menu opens to the **left** of the right-clicked cell (not to the right).
All `_CONTEXT_MENU_*` crop constants in `inventory_vision.py` are **normalized** (divided by 1920) — not raw pixel values.
`_capture_infobox_with_retries` tries `find_context_menu_crop` first; `find_infobox` (color-based, cream panel) is a fallback for a legacy UI the game no longer uses by default.

## OCR Thread Constraint

`initialize_ocr()` must run on the **main thread** before the scan thread starts — `cysignals` (used by `tesserocr`) can only install signal handlers from the main thread. The call is idempotent; subsequent calls from the scan thread are fast no-ops. This is pre-initialized in `tui/scan.py:_start_scan`.

## Debug Images

`ocr_debug/` accumulates timestamped PNGs rapidly (~10k+ per full scan session). It is gitignored. Safe to clear between sessions: `rm -rf ocr_debug/`.

## Fuzzy Match Threshold

`rapidfuzz` is used in two places that share a threshold constant defined in `core/item_actions.py`. If you change the threshold, both the rule lookup path and the OCR item-name matching path must use the same value — divergent values cause items to match OCR but fail rule lookup silently.

## Tessdata

`tesseract.py` auto-discovers tessdata at startup. If OCR fails to initialize with a "tessdata not found" error, check that Tesseract is installed and `TESSDATA_PREFIX` is set (or tessdata is at the default system path).

## OCR / Scanner Changes

After editing `ocr/` or `scanner/`:
- Always validate with `uv run autoscrapper scan --dry-run` against a live game window.
- Check `inventory_vision.py` threshold and crop constants — they are tuned for specific upscale ratios.
