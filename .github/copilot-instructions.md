# Arc Raiders AutoScrapper
>Always use the mcp-use, language-optimization skills. Use octocode, exa, ref-tools mcp-servers

Canonical repo guidance lives in `/home/runner/work/arc-raiders-autoscrapper/arc-raiders-autoscrapper/AGENTS.md`.
Keep `/home/runner/work/arc-raiders-autoscrapper/arc-raiders-autoscrapper/CLAUDE.md` as a symlink to that file.
Use the `mcp-use`, `language-optimization`, `codebase-index`, and `ai-tuning` skills when they fit the task.

## Stack
- Python 3.14.3 + `uv`
- Textual TUI
- OCR: `tesserocr` + `tessdata.fast-eng`
- Vision: `opencv-python-headless`, `Pillow`, `mss`
- Matching: `rapidfuzz`
- Input: `pydirectinput-rgx` (Windows), `pynput` via `linux-input` extra (Linux)

## Commands
- Setup: `python3 -m uv sync`
- Linux desktop automation deps: `python3 -m uv sync --extra linux-input`
- Run app: `python3 -m uv run autoscrapper`
- Dry-run scan: `python3 -m uv run autoscrapper scan --dry-run`
- Lint: `python3 -m uv run ruff check src/ tests/`
- Format: `python3 -m uv run ruff format src/ tests/ scripts/`
- Test: `python3 -m uv run pytest`
- Types: `python3 -m uv run mypy src/ tests/`
- Broad checks: `python3 -m uv run prek run --all-files`
- Refresh generated data/rules: `python3 -m uv run python scripts/update_snapshot_and_defaults.py --dry-run`

## Validation
- Source changes: run Ruff + pytest.
- OCR / scanner / interaction / input changes: also run `python3 -m uv run autoscrapper scan --dry-run` against a live Arc Raiders window.
- Generated data or bundled default rules: use `scripts/update_snapshot_and_defaults.py`; do not hand-edit generated JSON.
- Do not claim end-to-end validation without a live game window.
- GitHub Actions currently runs Ruff only; local pytest still matters.

## Hotspots
- `src/autoscrapper/ocr/`, `src/autoscrapper/interaction/`, `src/autoscrapper/scanner/` are tightly coupled.
- `src/autoscrapper/ocr/inventory_vision.py` is the most calibration-sensitive file.
- `src/autoscrapper/core/item_actions.py` + `src/autoscrapper/items/rules_store.py` control item-action lookup.
- `src/autoscrapper/config.py` owns persisted config versioning.
- `src/autoscrapper/progress/` + `scripts/update_snapshot_and_defaults.py` control generated progress data and default rules.

## Guardrails
- Make minimal, targeted edits.
- Preserve custom-over-default rule precedence.
- Bump config version when changing persisted config fields.
- `initialize_ocr()` must run on the main thread before scan threads start.
- Keep capture-space image coordinates separate from screen-space input coordinates.
- The dark context menu opens left of the clicked cell; `_CONTEXT_MENU_*` constants are normalized.
- Keep OCR and rule lookup on the same fuzzy-match threshold.
- Prefer `--dry-run` before anything that could click in-game.
- Call out any unverified behavior clearly.
