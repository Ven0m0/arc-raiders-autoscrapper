# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Setup (first time, Windows)
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\setup-windows.ps1

# Setup (Linux)
bash scripts/setup-linux.sh

# Run TUI
uv run autoscrapper

# Run scan directly
uv run autoscrapper scan
uv run autoscrapper scan --dry-run

# Format + lint
uv run ruff format src/
uv run ruff check src/
uv run ruff check --fix src/

# Pre-commit (runs ruff)
uv run pre-commit run --all-files

# Update game data snapshots (items.json, quests.json, default rules)
uv run python scripts/update_snapshot_and_defaults.py
```

There is no test suite yet. Verification is done via `--dry-run` scan against a live game window.

## Architecture

The tool captures the Arc Raiders inventory screen, OCR-reads each item name, looks up a keep/sell/recycle decision, and optionally clicks the appropriate button.

**Scan flow:**
1. `scanner/engine.py` waits for the game window and initialises Tesseract OCR
2. `interaction/inventory_grid.py` uses OpenCV contour detection to locate the 4×5 grid cells
3. For each cell: click → capture infobox region → OCR the title strip (`ocr/inventory_vision.py`) → clean text
4. `core/item_actions.py` looks up the cleaned name in `items_rules.*.json` (exact match, then `rapidfuzz` WRatio fuzzy fallback at threshold 85)
5. `progress/decision_engine.py` evaluates quest/crafting dependencies for ambiguous items
6. `scanner/actions.py` executes the click action (or skips in `--dry-run`)

**Key modules:**
- `ocr/tesseract.py` — thread-safe Tesseract singleton; PSM=SINGLE_LINE; character whitelist; lazy init with multiple tessdata path fallbacks
- `ocr/inventory_vision.py` — infobox detection by BGR colour `(236, 246, 253)` ±30 tolerance; title ROI is top ~18% of infobox; 2× INTER_CUBIC upscale before threshold
- `core/item_actions.py` — `ActionMap` (dict of normalised name → decisions); `match_item_name()` for fuzzy fallback
- `progress/decision_engine.py` — per-item KEEP/SELL/RECYCLE reasoning considering quests, recipes, recycle value
- `items/rules_store.py` — loads `items_rules.custom.json` (user) → falls back to `items_rules.default.json` (generated)
- `config.py` — persisted to `%APPDATA%/AutoScrapper/config.json` (Windows) or `~/.autoscrapper/` (Linux); `CONFIG_VERSION=5`
- `tui/` — Textual TUI with screens for scan, settings, rules editor, progress review
- `scripts/update_snapshot_and_defaults.py` — fetches Metaforge API → writes `progress/data/*.json` + regenerates default rules; runs daily via GitHub Actions

**Platform input:** `pydirectinput-rgx` on Windows, `pynput` on Linux (abstracted in `interaction/input_driver.py`).

**Package data** (bundled in wheel): `items_rules.default.json`, `progress/data/*.json`, TUI CSS stylesheets.

## Active Work

`TODO.md` tracks pending items. `PLAN.md` contains the root-cause analysis and fix plan for OCR/item-detection failures. Key pending areas: infobox title crop, OCR result caching, config upper-bound validation, config version migration, duplicate delay constants in `scanner/actions.py`, and several rules mismatches (`fabric`, `rusted-tools`, light-sticks, `stitcher-i/ii`).
