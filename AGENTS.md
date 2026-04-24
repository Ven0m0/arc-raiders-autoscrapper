## Repository Guide - Arc Raiders AutoScrapper

This is the canonical repository guide for contributors and coding agents working in Arc Raiders AutoScrapper. Keep `CLAUDE.md` as a symlink to this file. Keep `.github/copilot-instructions.md` short and startup-focused; put path-specific rules in `.github/instructions/*.instructions.md`.

### Quick Start

- **Python**: 3.13
- **Package manager**: `uv` (prefer `uv ...` in automation — uv may not be on PATH)
- **UI**: Textual (TUI)
- **Runtime**: Desktop automation for Arc Raiders inventory management (no game process hooking)

### Project Overview

Arc Raiders AutoScrapper automates inventory management via:
- **Textual** TUI screens
- **OCR** (tesserocr + tessdata.fast-eng) for item detection
- **Vision** (OpenCV, Pillow, mss) for screen capture and grid detection
- **Fuzzy matching** (rapidfuzz) for item name normalization
- **Rule lookup** (`KEEP | SELL | RECYCLE`) with progress-based overrides
- **Optional desktop input** (pydirectinput-rgx on Windows, pynput on Linux)

**Dependencies**
- OCR: tesserocr, tessdata.fast-eng
- Vision: opencv-python-headless, Pillow, mss
- Matching: rapidfuzz
- Input: pydirectinput-rgx (Windows), pynput via linux-input (Linux)

### Repository Map

| Path | Purpose |
|------|---------|
| `src/autoscrapper/tui/` | Textual screens; `scan.py` starts scan flow |
| `src/autoscrapper/scanner/` | Scan engine, page loop, reporting, action execution |
| `src/autoscrapper/interaction/` | Screen capture, grid detection, platform input |
| `src/autoscrapper/ocr/` | Tesseract init, preprocessing, infobox/item extraction |
| `src/autoscrapper/core/item_actions.py` | Rule lookup and fuzzy decision logic |
| `src/autoscrapper/items/rules_store.py` | Load/save custom rules; overrides bundled defaults |
| `src/autoscrapper/progress/` | Quest, hideout, crafting data and default-rule generation |
| `scripts/update_snapshot_and_defaults.py` | Regenerates bundled progress data and default rules |
| `src/autoscrapper/config.py` | Persisted config dataclasses and versioning |
| `tests/` | Pytest suite |

### Daily Commands

| Task | Command |
|------|---------|
| Install dependencies | `uv sync` |
| Install Linux input extra | `uv sync --extra linux-input` |
| Run TUI | `uv run autoscrapper` |
| Run scan | `uv run autoscrapper scan` |
| Run dry-run scan | `uv run autoscrapper scan --dry-run` |
| Lint Python | `uv run ruff check src/ tests/ scripts/` |
| Format Python | `uv run ruff format src/ tests/ scripts/` |
| Type-check Python | `uv run basedpyright src/` |
| Run tests | `uv run pytest` |
| Validate workflow | `uv run prek run --files .github/workflows/<name>.yml` |
| Run repo checks | `uv run prek run --all-files` |
| Refresh generated data | `uv run python scripts/update_snapshot_and_defaults.py` |
| Dry-run data refresh | `uv run python scripts/update_snapshot_and_defaults.py --dry-run` |

If `uv run <cmd>` fails with `No module named uv`, use `uv run <cmd>` directly.

### Validation Expectations

| Change Type | Minimum Validation |
|-------------|-------------------|
| Python source | `ruff check` + `basedpyright` + `pytest` |
| Workflow files | `prek run --files .github/workflows/<name>.yml` |
| Generated data/rules | Use updater script (with `--dry-run` first) |
| Docs/agent guidance | Verify paths, commands, links, hierarchy |
| OCR/scanner/interaction/input | Standard validation + `autoscrapper scan --dry-run` |

- **Do not claim end-to-end OCR/scanner validation without a live Arc Raiders window.**
- **Prefer `--dry-run` before anything that could click in-game.**

### Generated Files & Persisted Config

- **Never hand-edit** `src/autoscrapper/progress/data/`.
- **Never hand-edit** `src/autoscrapper/items/items_rules.default.json`.
- Regenerate both via `scripts/update_snapshot_and_defaults.py`.
- On config field changes: bump `CONFIG_VERSION` in `src/autoscrapper/config.py` and add a migration.
- Preserve custom-over-default rule precedence.

### OCR & Interaction Invariants (High-Risk)

Changes in these areas require extra caution, live validation, or corpus replay:

1. `initialize_ocr()` must run on the **main thread** before scan threads start.
2. Keep the four Tesseract API locks separate: `_api_lock`, `_api_line_lock`, `_api_single_word_lock`, `_api_sparse_lock`.
3. Keep capture-space image coordinates separate from screen-space input coordinates. Screen translation belongs in `src/autoscrapper/interaction/ui_windows.py`.
4. `inventory_vision.py` upscales OCR images by 2×. Convert OCR boxes back to original-space coordinates before reuse.
5. The dark context menu opens to the left of the clicked cell. The `_CONTEXT_MENU_` constants in `inventory_vision.py` are normalized to 1920×1080.
6. Prefer `ocr_infobox_with_context(window_bgr, rect)` when the full window is available.
7. `find_context_menu_crop` rejects crops with `dark_fraction < 0.20` on the left half. Treat that threshold as calibration-sensitive.
8. Keep the fuzzy-match threshold shared between OCR item matching and rule lookup. Changing threshold or `score_cutoff` values requires corpus replay before shipping.

### Hotspots

Focus extra review time on these critical files:
- `src/autoscrapper/ocr/inventory_vision.py`
- `src/autoscrapper/scanner/`
- `src/autoscrapper/core/item_actions.py`
- `src/autoscrapper/items/rules_store.py`
- `src/autoscrapper/config.py`

### Available Skills

Use these built-in skills for common workflows:

- `verify` — Full validation (lint + types + tests)
- `dead-code-sweep` — Find/remove dead code
- `add-rule` — Add/edit custom item rules
- `threshold-change` — Safe threshold/sensitivity changes (requires corpus replay)
- `ocr-corpus-replay` — Validate OCR changes against failure corpus
- `config-bump` — Safely add/rename/remove persisted config fields
- `calibrate-vision` — Recalibrate context-menu crop constants
- `data-snapshot-updater` — Update Metaforge snapshots and bundled default rules
- `patch-update` — Full new-game-patch pipeline
- `scan-failed` — Diagnose scan failures (wrong decisions despite correct OCR)
- `ocr-unavailable` — Triaging "UNAVAILABLE" misreads
- `benchmark` — Tesseract model variant benchmarking

### Git & Remote Rules

- **Only permitted remote:** `https://github.com/Ven0m0/arc-raiders-autoscrapper` (personal fork).
- **Never push** to upstream `https://github.com/zappybiby/ArcRaiders-AutoScrapper`.
- If `gh pr create` would default to upstream, pass `--repo Ven0m0/arc-raiders-autoscrapper` or push without opening a PR.

### Code Quality

Run before committing:
```bash
uv run ruff check src/ tests/ scripts/
uv run ruff format src/ tests/ scripts/
uv run basedpyright src/
uv run pytest
```

### Documentation Updates

- Keep the hierarchy clear: stable repo-wide rules here, startup guidance in `.github/copilot-instructions.md`, path-specific rules in `.github/instructions/*.instructions.md`.
- Avoid duplicating large rule blocks across multiple files.