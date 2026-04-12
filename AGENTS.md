# AGENTS.md

Canonical repo-wide agent guide.
Keep `/home/runner/work/arc-raiders-autoscrapper/arc-raiders-autoscrapper/CLAUDE.md` as a symlink to this file; do not maintain separate content.

## Guidance Hierarchy

- `AGENTS.md` → canonical repo-wide guidance.
- `.github/copilot-instructions.md` → short Copilot bootstrap only.
- `.github/instructions/*.instructions.md` → path- or topic-specific rules.
- `.github/skills/` → reusable workflows and specialized guidance.

## Project

Arc Raiders AutoScrapper is a desktop automation app for Arc Raiders inventory management.
It uses a Textual TUI, screen capture + OCR for item detection, fuzzy rule lookup for `KEEP | SELL | RECYCLE`, and optional desktop input automation.
It does **not** hook into the game process.

## Stack

| Area | Details |
| --- | --- |
| Runtime | Python `3.13.x`–`3.14.x` only, `uv` |
| UI | `textual` |
| OCR | `tesserocr`, `tessdata.fast-eng` |
| Vision | `opencv-python-headless`, `Pillow`, `mss` |
| Matching | `rapidfuzz` |
| Input | `pydirectinput-rgx` (Windows), `pynput` via `linux-input` extra (Linux) |
| Serialization | `orjson` |

## Python Version Guardrails

- Keep Python support bounded to `>=3.13, <=3.14`; do **not** move to Python `3.15+` until the dependency/tooling breakage is resolved.
- Treat Python-version changes as coordinated changes across `.python-version`, `pyproject.toml`, lockfiles, setup scripts, and workflows.
- The repo currently mixes `3.13` runtime metadata with some `3.14`-targeted tooling and Windows wheel constraints; verify all affected files before changing version policy.

## Commands

Prefer `python3 -m uv ...` in automation because `uv` may not be on `PATH`.

| Task | Command |
| --- | --- |
| Setup | `python3 -m uv sync` |
| Setup with Linux input | `python3 -m uv sync --extra linux-input` |
| Run TUI | `python3 -m uv run autoscrapper` |
| Scan | `python3 -m uv run autoscrapper scan` |
| Safe scan | `python3 -m uv run autoscrapper scan --dry-run` |
| Lint | `python3 -m uv run ruff check src/ tests/` |
| Format | `python3 -m uv run ruff format src/ tests/ scripts/` |
| Tests | `python3 -m uv run pytest` |
| Types | `python3 -m uv run basedpyright src/` |
| Broad checks | `python3 -m uv run prek run --all-files` |
| Refresh generated data/rules | `python3 -m uv run python scripts/update_snapshot_and_defaults.py` |
| Preview generated data/rules | `python3 -m uv run python scripts/update_snapshot_and_defaults.py --dry-run` |
| Qlty check | `qlty check -a` |
| Qlty metrics | `qlty metrics -a` |
| Qlty smells | `qlty smells -a` |

## Tooling Notes

| Tool | Purpose | Source |
| --- | --- | --- |
| `basedpyright` | Type checking | `[tool.basedpyright]` in `pyproject.toml` |
| `ruff` | Lint + format | `[tool.ruff]` in `pyproject.toml` |
| `prek` | Broad repo hooks | `.pre-commit-config.yaml` |

- `basedpyright` runs automatically on `.py` edits via `.claude/settings.json` hooks.
- `ruff` auto-formats and reports lint issues via the same hook chain.
- Do not reintroduce `mypy` guidance unless the project config changes.

## Validation

| Change type | Minimum validation |
| --- | --- |
| Python source | `python3 -m uv run ruff check src/ tests/` + `python3 -m uv run pytest` |
| OCR / scanner / interaction / input | Standard validation + `python3 -m uv run autoscrapper scan --dry-run` against a live Arc Raiders window |
| Generated data / default rules | Use the updater script; usually run `--dry-run` first |
| Workflow changes | `python3 -m uv run prek run --files .github/workflows/<name>.yml` |
| Docs / agent guidance only | Verify file accuracy, links, hierarchy, and referenced commands |

Notes:
- Local pytest still matters even though GitHub Actions currently emphasizes Ruff.
- Do not claim end-to-end validation unless a live Arc Raiders window was used.
- Prefer `--dry-run` before anything that could click in-game.

## Repository Map

| Path | Purpose |
| --- | --- |
| `src/autoscrapper/tui/` | Textual screens; `scan.py` starts the scan flow |
| `src/autoscrapper/scanner/` | Scan engine, page loop, reporting, action execution |
| `src/autoscrapper/interaction/` | Screen capture, grid detection, platform input |
| `src/autoscrapper/ocr/` | Tesseract init, preprocessing, infobox/item extraction |
| `src/autoscrapper/core/item_actions.py` | Rule lookup and fuzzy decision logic |
| `src/autoscrapper/items/rules_store.py` | Load/save custom rules; custom overrides bundled defaults |
| `src/autoscrapper/progress/` | Quest/hideout/crafting data and default-rule generation |
| `scripts/update_snapshot_and_defaults.py` | Regenerates progress snapshots and bundled default rules |
| `src/autoscrapper/config.py` | Persisted config dataclasses, migrations, versioning |
| `tests/` | Pytest suite |

## Critical Invariants

- Preserve custom-over-default rule precedence.
- Do **not** hand-edit `src/autoscrapper/progress/data/*` or `src/autoscrapper/items/items_rules.default.json`; regenerate via `scripts/update_snapshot_and_defaults.py`.
- Do **not** hand-edit `uv.lock`; use `uv add/remove/sync` instead.
- Bump `CONFIG_VERSION` and add a migration when changing persisted config fields.
- `initialize_ocr()` must run on the main thread before the scan thread starts.
- Capture-space image coordinates and screen-space input coordinates must stay separate.
- `inventory_vision.py` upscales OCR images 2×; convert OCR boxes back to original-space coords before reuse. `find_action_bbox_by_ocr()` already returns original-space coords.
- Keep the fuzzy-match threshold shared between OCR matching and rule lookup.
- `ocr_debug/` is disposable debug output and is safe to clear between sessions.

## Hotspots

- `src/autoscrapper/ocr/`, `src/autoscrapper/interaction/`, and `src/autoscrapper/scanner/` are tightly coupled.
- `src/autoscrapper/ocr/inventory_vision.py` is the most calibration-sensitive file.
- `src/autoscrapper/core/item_actions.py` + `src/autoscrapper/items/rules_store.py` control action resolution behavior.
- `src/autoscrapper/progress/` changes often imply regenerating bundled data.

## Remotes

- `upstream` → `https://github.com/zappybiby/ArcRaiders-AutoScrapper.git` (canonical source)
- `origin` → your fork

## Agent Workflow

- Make minimal, targeted edits.
- Prefer MCP-first workflows and relevant project skills, especially `mcp-use`, `language-optimization`, `codebase-index`, `ai-tuning`, and `workflow-development`.
- Read the relevant module before editing; update adjacent docs only when behavior or workflow changes.
- Use script-driven or tool-driven updates for generated assets.
- Surface unverified behavior clearly in summaries and PR text.
