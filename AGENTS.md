# AGENTS.md

Canonical agent guide for this repository.
Keep `/home/runner/work/arc-raiders-autoscrapper/arc-raiders-autoscrapper/CLAUDE.md` as a symlink to this file; do not maintain separate content.

## Project

Arc Raiders AutoScrapper is a Python 3.14.3 desktop automation app for Arc Raiders inventory management.
It uses Textual for the TUI, screen capture + OCR for item detection, rule lookup for `KEEP | SELL | RECYCLE`, and optional desktop input automation.
It does **not** hook into the game process.

## Stack

| Area | Details |
| --- | --- |
| Runtime | Python 3.14.3, `uv` |
| UI | `textual` |
| OCR | `tesserocr`, `tessdata.fast-eng` |
| Vision | `opencv-python-headless`, `Pillow`, `mss` |
| Matching | `rapidfuzz` |
| Input | `pydirectinput-rgx` (Windows), `pynput` via `linux-input` extra (Linux) |

## Commands

Prefer `python3 -m uv ...` in automation because `uv` may not be on `PATH`.

| Task | Command |
| --- | --- |
| Setup | `python3 -m uv sync` |
| Setup with Linux input | `python3 -m uv sync --extra linux-input` |
| Run TUI | `python3 -m uv run autoscrapper` |
| Scan | `python3 -m uv run autoscrapper scan` |
| Safe scan validation | `python3 -m uv run autoscrapper scan --dry-run` |
| Lint | `python3 -m uv run ruff check src/ tests/` |
| Format | `python3 -m uv run ruff format src/ tests/ scripts/` |
| Tests | `python3 -m uv run pytest` |
| Types | `python3 -m uv run mypy src/ tests/` |
| Broad repo checks | `python3 -m uv run prek run --all-files` |
| Refresh generated data/rules | `python3 -m uv run python scripts/update_snapshot_and_defaults.py` |
| Dry-run data refresh | `python3 -m uv run python scripts/update_snapshot_and_defaults.py --dry-run` |

## Validation

| Change type | Minimum validation |
| --- | --- |
| Python source | `python3 -m uv run ruff check src/ tests/` + `python3 -m uv run pytest` |
| OCR / scanner / interaction / input | Standard validation + `python3 -m uv run autoscrapper scan --dry-run` against a live Arc Raiders window |
| Generated data / default rules | Use the updater script; usually run `--dry-run` first |
| Docs / agent guidance only | Verify affected files, links, and instructions stay accurate |

Notes:
- Local tests exist and should be run for code changes even though GitHub Actions currently runs Ruff only.
- Do not claim end-to-end validation unless a live Arc Raiders window was used.
- Prefer `--dry-run` before anything that could click in-game.

## Repository Map

| Path | Purpose |
| --- | --- |
| `src/autoscrapper/tui/` | Textual screens; `scan.py` starts the scan flow |
| `src/autoscrapper/scanner/` | Engine, page loop, reporting, action execution |
| `src/autoscrapper/interaction/` | Screen capture, grid detection, platform input |
| `src/autoscrapper/ocr/` | Tesseract init, preprocessing, infobox/item extraction |
| `src/autoscrapper/core/item_actions.py` | Rule lookup and fuzzy decision logic |
| `src/autoscrapper/items/rules_store.py` | Load/save custom rules; custom overrides bundled defaults |
| `src/autoscrapper/progress/` | Quest/hideout/crafting data and default-rule generation |
| `scripts/update_snapshot_and_defaults.py` | Regenerates progress snapshots and bundled default rules |
| `src/autoscrapper/config.py` | Persisted config dataclasses and versioning |
| `tests/` | Pytest suite |

## Critical Invariants

- Preserve custom-over-default rule precedence.
- Do **not** hand-edit `src/autoscrapper/progress/data/*` or `src/autoscrapper/items/items_rules.default.json`; regenerate via `scripts/update_snapshot_and_defaults.py`.
- Bump the config version in `src/autoscrapper/config.py` when changing persisted config fields.
- `initialize_ocr()` must run on the main thread before the scan thread starts.
- Image-processing coordinates are capture-space pixels; screen-space translation belongs in `src/autoscrapper/interaction/ui_windows.py`.
- The dark context menu opens to the **left** of the clicked cell; `_CONTEXT_MENU_*` constants in `inventory_vision.py` are normalized by 1920.
- Keep the fuzzy-match threshold shared between OCR matching and rule lookup.
- `ocr_debug/` is disposable debug output and is safe to clear between sessions.

## Hotspots

- `src/autoscrapper/ocr/`, `src/autoscrapper/interaction/`, and `src/autoscrapper/scanner/` are tightly coupled.
- `src/autoscrapper/ocr/inventory_vision.py` is the hottest and most calibration-sensitive file.
- `src/autoscrapper/core/item_actions.py` and `src/autoscrapper/items/rules_store.py` define action resolution behavior.
- `src/autoscrapper/progress/` changes often imply regenerating bundled data.

## Agent Workflow

- Make minimal, targeted edits.
- Prefer project skills in `.github/skills/` when relevant, especially `mcp-use`, `codebase-index`, `language-optimization`, `ai-tuning`, and `workflow-development`.
- Read the relevant module before editing; update adjacent docs only when the behavior or workflow changes.
- Use script-driven or tool-driven changes instead of manual rewrites for generated assets.
- Call out any unverified behavior clearly in summaries and PR text.
