# Arc Raiders AutoScrapper
>Always use the mcp-use skill

Arc Raiders AutoScrapper is a Python 3.14 desktop automation app for inventory management. It uses Textual for the UI, screen capture plus OCR to identify items, rule lookup to decide keep/sell/recycle, and optional click automation.

## Use these commands
- Linux setup: `bash scripts/setup-linux.sh`
- Windows setup: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/setup-windows.ps1`
- Run app: `uv run autoscrapper`
- Run scan: `uv run autoscrapper scan`
- Safe scan validation: `uv run autoscrapper scan --dry-run`
- Format: `uv run ruff format src/`
- Lint: `uv run ruff check src/`
- Full checks: `uv run prek run --all-files`
- Refresh generated data/rules: `uv run python scripts/update_snapshot_and_defaults.py`
- Dry-run refresh: `uv run python scripts/update_snapshot_and_defaults.py --dry-run`

## Validation rules
- There is no automated test suite.
- Run Ruff for source changes.
- Prefer `uv run prek run --all-files` for broader changes.
- For OCR, scanner, grid, or input-driver changes, validate with `uv run autoscrapper scan --dry-run`.
- For generated data or rules changes, use the updater script, usually with `--dry-run` first.
- Do not claim end-to-end validation unless a live Arc Raiders window was used.

## Hotspots
- `src/autoscrapper/ocr/`, `src/autoscrapper/interaction/`, and `src/autoscrapper/scanner/` are tightly coupled.
- `src/autoscrapper/core/item_actions.py` and `src/autoscrapper/items/rules_store.py` define rule loading and action lookup.
- `src/autoscrapper/progress/` and `scripts/update_snapshot_and_defaults.py` control generated quest/crafting data and default rules.
- `src/autoscrapper/config.py` is sensitive because it owns persisted config versioning.

## Guardrails
- Prefer minimal, targeted edits.
- Prefer `--dry-run` before anything that could click in-game.
- Preserve custom-over-default rule precedence.
- Prefer script-driven updates over manual edits to generated data.
- Call out any unverified behavior clearly.
