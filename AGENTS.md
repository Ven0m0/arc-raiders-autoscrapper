# AGENTS.md

Canonical agent guide for this repository.
Keep `CLAUDE.md` as a symlink to this file; do not maintain separate content.

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
| Serialization | `orjson` |

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

## Instruction Hierarchy

| Layer | Purpose |
| --- | --- |
| `AGENTS.md` | Canonical repo-wide agent guidance; keep broad rules here |
| `.github/copilot-instructions.md` | Concise repository-wide Copilot instructions; defer detail to `AGENTS.md` |
| `.github/instructions/*.instructions.md` | Path- or language-specific guidance for Bash, Python, Markdown, reviews, and token usage |
| `.claude/skills/*/SKILL.md` + `.github/skills/*/SKILL.md` | Task-specific workflows and reusable operational guidance |
| `.claude/agents/*.md` + `.kilo/agents/*.md` | Specialized review/validation agents for hotspot modules |

Keep repo-wide rules in the top layer; avoid duplicating them in narrower instruction files.

## Validation

| Change type | Minimum validation |
| --- | --- |
| Python source | `python3 -m uv run ruff check src/ tests/` + `python3 -m uv run pytest` |
| OCR / scanner / interaction / input | Standard validation + `python3 -m uv run autoscrapper scan --dry-run` against a live Arc Raiders window |
| Generated data / default rules | Use the updater script; usually run `--dry-run` first |
| `config.py` | Bump `CONFIG_VERSION`; add a migration function; run standard validation |
| Docs / agent guidance only | Verify affected files, links, and instructions stay accurate |

Notes:
- Local tests exist and should be run for code changes even though GitHub Actions currently runs Ruff only.
- Do not claim end-to-end validation unless a live Arc Raiders window was used.
- Prefer `--dry-run` before anything that could click in-game.
- `.claude/settings.json` PostToolUse hooks auto-run `ruff check --fix`, `ruff format`, and `mypy` on every edited `.py` file. Edits to `ocr/` files also trigger `pytest tests/autoscrapper/ocr/`; edits to `scanner/` files trigger the full test suite.

## Repository Map

| Path | Purpose |
| --- | --- |
| `.github/copilot-instructions.md` | Repo-wide GitHub Copilot custom instructions; should stay concise and point back to `AGENTS.md` |
| `.github/instructions/` | Path-specific Copilot instruction files for language/tool-specific standards |
| `src/autoscrapper/__main__.py` | Entry point; dispatches to TUI (`autoscrapper`) or scan CLI (`autoscrapper scan [--dry-run]`) |
| `src/autoscrapper/tui/` | Textual screens; `app.py` is the root; `scan.py` starts the scan flow |
| `src/autoscrapper/scanner/engine.py` | Scan coordinator; builds `ScanContext`, calls `scan_pages()`, returns `ScanStats` |
| `src/autoscrapper/scanner/scan_loop.py` | Per-cell scan loop; OCR → rule lookup → action dispatch; calls `reset_ocr_caches()` at entry |
| `src/autoscrapper/scanner/actions.py` | Executes SELL/RECYCLE clicks; `resolve_action_taken` maps decisions to outcome codes |
| `src/autoscrapper/scanner/outcomes.py` | Action outcome labels: `KEEP`, `SELL`, `RECYCLE`, `SKIP_*`, `UNREADABLE_*`, `DRY_RUN_*` |
| `src/autoscrapper/interaction/ui_windows.py` | Window targeting (`pywinctl`), `mss` capture, screen-space coordinate translation, scroll calibration |
| `src/autoscrapper/interaction/inventory_grid.py` | 4×5 contour-based grid detection; window-normalized `GRID_ROI_NORM`; returns `Cell` objects |
| `src/autoscrapper/interaction/input_driver.py` | Platform-split input: `pydirectinput` + `GetAsyncKeyState` (Windows), `pynput` (Linux) |
| `src/autoscrapper/ocr/inventory_vision.py` | Infobox detection, 2×-upscale OCR pipeline, item-name fuzzy matching; most calibration-sensitive file |
| `src/autoscrapper/ocr/tesseract.py` | `initialize_ocr()`, `image_to_data()`, `image_to_string()`; Tesseract API lifecycle; main-thread only |
| `src/autoscrapper/ocr/failure_corpus.py` | Captures `SKIP_UNLISTED` samples to `artifacts/ocr/skip_unlisted/` for threshold tuning (TODO T001) |
| `src/autoscrapper/core/item_actions.py` | `load_item_actions()`, `choose_decision()`, `clean_ocr_text()`; action aliases; `Decision` literal type |
| `src/autoscrapper/items/rules_store.py` | Load/save custom and default rules; `active_rules_path()` returns custom if it exists, else default |
| `src/autoscrapper/progress/decision_engine.py` | `DecisionEngine`: per-item KEEP/SELL/RECYCLE driven by quest, crafting, and hideout state |
| `src/autoscrapper/progress/rules_generator.py` | Generates `items_rules.default.json` entries from game data and a progress snapshot |
| `src/autoscrapper/progress/data_update.py` | Fetches items/quests from Metaforge API (primary) with RaidTheory repo ZIP as fallback |
| `src/autoscrapper/progress/data/` | Bundled game snapshots (`items.json`, `quests.json`, `quests_by_trader.json`, `metadata.json`) — **generated** |
| `src/autoscrapper/config.py` | `ScanSettings`, `ProgressSettings`, `UiSettings` dataclasses; `CONFIG_VERSION = 5`; migrations v1→v5 |
| `src/autoscrapper/warmup.py` | Background import warmup; deliberately excludes `tesserocr`-dependent modules (main-thread constraint) |
| `scripts/update_snapshot_and_defaults.py` | Orchestrates data fetch + default-rules generation; used by daily CI workflow |
| `artifacts/` | Runtime outputs: `artifacts/ocr/` for failure corpus; `artifacts/update-report.*` for CI reporting |
| `tests/` | Pytest suite mirroring `src/autoscrapper/` structure |

## Critical Invariants

- Preserve custom-over-default rule precedence. `items_rules.custom.json` always overrides `items_rules.default.json`; merge order in `item_actions.py` must never invert this.
- Do **not** hand-edit `src/autoscrapper/progress/data/*` or `src/autoscrapper/items/items_rules.default.json`; regenerate via `scripts/update_snapshot_and_defaults.py`.
- Do **not** hand-edit `uv.lock`; use `uv add/remove/sync` instead. A PreToolUse hook in `.claude/settings.json` blocks edits to this file.
- Bump `CONFIG_VERSION` in `src/autoscrapper/config.py` and add a corresponding migration function to `_MIGRATIONS` when adding or removing persisted config fields. Current version: **5**.
- `initialize_ocr()` must run on the **main thread** before scan threads start. `cysignals` (a `tesserocr` transitive dependency) installs OS signal handlers and can only be called from the main thread. `warmup.py` excludes `inventory_vision`, `scan_loop`, and `engine` for this reason.
- Image-processing coordinates are capture-space pixels; screen-space translation belongs in `src/autoscrapper/interaction/ui_windows.py`. Inside `inventory_vision.py`, `preprocess_for_ocr()` upscales images 2×; any bbox returned from Tesseract over a 2× image must be halved before use in original-space operations. `find_action_bbox_by_ocr` handles this internally — callers receive original-space coords.
- The dark context menu opens to the **left** of the clicked cell; `_CONTEXT_MENU_*` constants in `inventory_vision.py` are normalized by 1920.
- Keep the fuzzy-match threshold consistent between OCR item-name matching (`inventory_vision.py`) and rule lookup (`core/item_actions.py`). Default: `DEFAULT_ITEM_NAME_MATCH_THRESHOLD = 75`. Changing this requires corpus replay against `artifacts/ocr/skip_unlisted/` before shipping (see `.claude/skills/corpus-replay/` and TODO T001).
- OCR preprocessing pipeline order is fixed: `BGR → grayscale → upscale 2× → Otsu binarization → morphological ops → Tesseract`. Binarization must precede morphological operations. Raw BGR must never reach Tesseract.
- `reset_ocr_caches()` must be called at the start of `scan_pages()`. The three module-level caches (`_last_roi_hash`, `_last_ocr_result`, `_ITEM_NAMES`) must not persist across scan sessions.
- `ocr_debug/` is disposable debug output and is safe to clear between sessions.
- Linux target window title is `Arc Raiders`; Windows target process is `PioneerGame.exe`. Override with `AUTOSCRAPPER_TARGET_APP` env var.

## Hotspots

- `src/autoscrapper/ocr/`, `src/autoscrapper/interaction/`, and `src/autoscrapper/scanner/` are tightly coupled.
- `src/autoscrapper/ocr/inventory_vision.py` is the hottest and most calibration-sensitive file (infobox detection, 2× coordinate math, fuzzy threshold, OCR pipeline order).
- `src/autoscrapper/core/item_actions.py` and `src/autoscrapper/items/rules_store.py` define action resolution behavior.
- `src/autoscrapper/progress/` changes often imply regenerating bundled data via the update script.
- `src/autoscrapper/config.py` requires a version bump whenever persisted fields change.

## Agent Inventory

Sub-agents defined in `.claude/agents/` — invoke by description match when editing the corresponding modules:

| Agent | Trigger |
| --- | --- |
| `ocr-reviewer` | Edits to `src/autoscrapper/ocr/` or `src/autoscrapper/scanner/` |
| `scan-validator` | Edits to `scanner/scan_loop.py` or `interaction/` |
| `rules-reviewer` | Edits to `core/item_actions.py` or `items/rules_store.py` |
| `interaction-reviewer` | Edits to `interaction/` or input-driver code |
| `config-reviewer` | Edits to `config.py` |
| `progress-reviewer` | Edits to `progress/rules_generator.py`, `quest_inference.py`, or `data_loader.py` |

Equivalent agents also exist in `.kilo/agents/` for Kilo Code sessions.

## Skills Inventory

Project skills in `.claude/skills/` — invoke by name when relevant:

| Skill | When to use |
| --- | --- |
| `ocr-debug` | Debugging OCR misreads: coordinate spaces, preprocessing pipeline, cache state |
| `scan-failed` | OCR correct but wrong action — rule precedence, fuzzy threshold, progress overrides |
| `update-data` | Regenerating `progress/data/*.json` and `items_rules.default.json` safely |
| `add-rule` | Adding or editing a custom item rule in the rules JSON file |
| `dry-run` | Running `scan --dry-run` and interpreting `ocr_debug/` output images |
| `corpus-replay` | Validating a fuzzy threshold change against the captured OCR corpus before shipping |
| `repo-janitor` | Repository cleanup and dead code removal |

Project skills in `.github/skills/` (for GitHub Copilot agents):

`ai-tuning`, `codebase-index`, `docs-writer`, `fix-issue`, `gh-cli`, `language-optimization`, `lint-and-validate`, `mcp-use`, `ocr-debug`, `repo-janitor`, `update-data`, `workflow-development`.

## Agent Workflow

- Make minimal, targeted edits.
- Prefer project skills in `.claude/skills/` and `.github/skills/` when relevant; especially `mcp-use`, `codebase-index`, `language-optimization`, `ai-tuning`, and `workflow-development`.
- Keep `.github/copilot-instructions.md` concise and repo-wide; move detailed or path-specific rules into `AGENTS.md` or `.github/instructions/*.instructions.md` instead of duplicating them.
- Invoke the appropriate sub-agent from `.claude/agents/` after any change to OCR, scanner, interaction, config, rules, or progress modules.
- Read the relevant module before editing; update adjacent docs only when the behavior or workflow changes.
- Use script-driven or tool-driven changes instead of manual rewrites for generated assets.
- Call out any unverified behavior clearly in summaries and PR text.
