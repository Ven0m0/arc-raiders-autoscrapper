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

## Coordinate space invariant
Inside `inventory_vision.py`, two coordinate spaces coexist:
- **Original space**: the raw window crop dimensions
- **2x-upscaled space**: output of `preprocess_for_ocr()`, used for Tesseract OCR

Any bbox returned from OCR over a 2x image must be halved before applying to the original-space infobox rect. `find_action_bbox_by_ocr` handles this division internally — callers receive original-space coords.

## Debug output
OCR debug images land in `ocr_debug/` (timestamped PNGs). After a dry-run, inspect:
- `*_infobox_detect_overlay.png` — infobox detection result
- `*_ctx_menu_processed.png` — context menu crop and binarization
- `*_infobox_action_sell_processed.png` — sell/recycle button OCR region

## Session state
`inventory_vision.py` holds module-level caches (`_last_roi_hash`, `_last_ocr_result`, `_ITEM_NAMES`). `reset_ocr_caches()` clears them and is called automatically at `scan_pages()` start. `_ScanRunner._detected_ui_mode` resets per page to allow UI mode re-detection.

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
- Do not hand-edit `src/autoscrapper/progress/data/*.json` or `src/autoscrapper/items/items_rules.default.json` — these are generated outputs.

## Recommended automations

### Hooks (add to `.claude/settings.json`)
Auto-lint on edit:
```json
{"PostToolUse": [{"matcher": {"tool_name": "Edit", "file_paths": ["src/**/*.py"]}, "hooks": [{"type": "command", "command": "uv run ruff check --fix \"$CLAUDE_TOOL_INPUT_FILE_PATH\""}]}]}
```
Block direct edits to generated data files:
```json
{"PreToolUse": [{"matcher": {"tool_name": "Edit", "file_paths": ["src/**/progress/data/**", "src/**/items/items_rules.default.json"]}, "hooks": [{"type": "command", "command": "echo 'BLOCK: use uv run python scripts/update_snapshot_and_defaults.py' && exit 1"}]}]}
```

### Subagent (`.claude/agents/ocr-reviewer.md`)
Specialized reviewer for OCR/scanner changes — checks coordinate space consistency, upscale artifacts, shape assumptions, and cache reset paths.

### MCP Server
`context7` for live Textual/OpenCV/rapidfuzz API docs: `claude mcp add context7 -- npx -y @upstash/context7-mcp`
