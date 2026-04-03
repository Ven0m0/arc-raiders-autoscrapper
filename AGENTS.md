# Agent Instructions

## Repository purpose
Arc Raiders AutoScrapper is a Python 3.14 desktop automation tool for Arc Raiders inventory management. It captures the game window, OCR-reads item names, decides whether to keep, sell, or recycle them, and can optionally perform the click action.

## Stack
- Python 3.14
- `uv` for setup and command execution
- Textual for the TUI
- `mss`, Pillow, OpenCV, and `pywinctl` for capture and window handling
- Tesseract / `tesserocr` for OCR
- `rapidfuzz` for fuzzy item-name matching
- Ruff and pre-commit for code quality

## Primary commands
```bash
# Setup
bash scripts/setup-linux.sh
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/setup-windows.ps1

# Run the app
uv run autoscrapper
uv run autoscrapper scan
uv run autoscrapper scan --dry-run

# Code quality
uv run ruff format src/
uv run ruff check src/
uv run ruff check --fix src/
uv run pre-commit run --all-files

# Refresh generated data and default rules
uv run python scripts/update_snapshot_and_defaults.py
uv run python scripts/update_snapshot_and_defaults.py --dry-run
```

## Validation expectations
Use the cheapest validation that matches the change:
- Python source changes: `uv run ruff check src/`
- Broad repository changes: `uv run pre-commit run --all-files`
- OCR, scanner, grid detection, or input-driver changes: `uv run autoscrapper scan --dry-run`
- Snapshot or default-rules changes: `uv run python scripts/update_snapshot_and_defaults.py --dry-run`

There is no automated test suite. End-to-end verification requires a live Arc Raiders window, so do not claim runtime validation unless it was actually performed.

## Architecture hotspots
- `src/autoscrapper/scanner/` orchestrates scans, OCR initialisation, and action execution.
- `src/autoscrapper/interaction/` handles grid detection, window targeting, and platform input.
- `src/autoscrapper/ocr/` contains OCR preprocessing, title-strip extraction, and Tesseract integration.
- `src/autoscrapper/core/item_actions.py` and `src/autoscrapper/items/rules_store.py` load rules and resolve keep/sell/recycle actions.
- `src/autoscrapper/progress/` contains quest and crafting-aware decision logic plus generated data.
- `scripts/update_snapshot_and_defaults.py` is the source of truth for generated snapshot data and `items_rules.default.json`.
- `src/autoscrapper/config.py` owns persisted config schema and migrations.

## Working guidelines
- Prefer small, targeted edits in OCR, scanner, and input code; these paths are tightly coupled and easy to regress.
- Prefer `--dry-run` before any change that could trigger clicks.
- If generated data or default rules need to change, update them through the script instead of hand-editing generated outputs.
- Keep README, AGENTS.md, and `.github/copilot-instructions.md` aligned when commands or workflows change.
- Check `TODO.md` before changing fuzzy thresholds, OCR heuristics, or rule exceptions.

## Guardrails
- Preserve custom rule precedence over default rules.
- Preserve the scheduled workflow contract that regenerates `progress/data/*.json` and `items_rules.default.json`.
- Do not casually change OCR thresholds, fuzzy thresholds, or click timing without a reason tied to observed behavior.
- Be explicit about any verification limits caused by platform or live-window constraints.
