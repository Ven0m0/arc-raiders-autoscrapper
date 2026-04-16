<!-- Parent: ../../AGENTS.md -->
<!-- Generated: 2026-04-15 | Updated: 2026-04-15 -->

# src/autoscrapper/

## Purpose
Root package for the Arc Raiders AutoScrapper application. Contains the entry point, top-level config, and application-level bootstrapping. All feature modules are subpackages of this package.

## Key Files

| File | Description |
|------|-------------|
| `__main__.py` | CLI entry point — dispatches `autoscrapper` and `autoscrapper scan` commands |
| `config.py` | Persisted config dataclasses (user settings, OCR params, progress settings). Includes version field — bump on schema changes. |
| `warmup.py` | Pre-scan warmup: initializes OCR and loads item names before the scan thread starts |
| `app_warnings.py` | Startup warning checks (Tesseract version, missing config, etc.) |
| `__init__.py` | Package init — minimal, no side effects |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `api/` | MetaForge/ArcTracker API client and data models (see `api/AGENTS.md`) |
| `core/` | Rule lookup and fuzzy item-action decision logic (see `core/AGENTS.md`) |
| `interaction/` | Screen capture, inventory grid detection, platform input (see `interaction/AGENTS.md`) |
| `items/` | Custom and default rule storage, rule diff (see `items/AGENTS.md`) |
| `ocr/` | Tesseract init, image preprocessing, infobox/item OCR (see `ocr/AGENTS.md`) |
| `progress/` | Quest/hideout/crafting data, decision engine, rule generation (see `progress/AGENTS.md`) |
| `scanner/` | Scan engine, page loop, action execution, reporting (see `scanner/AGENTS.md`) |
| `tui/` | Textual TUI screens and application shell (see `tui/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- `config.py` is the **only** place persisted settings live. Always bump `CONFIG_VERSION` when adding or removing fields.
- `warmup.py` enforces the invariant: `initialize_ocr()` must complete on the **main thread** before the scan thread starts.
- Do not add business logic to `__main__.py` — it is a thin dispatcher only.

### Testing Requirements
- Top-level tests: `tests/autoscrapper/test_config.py`, `tests/autoscrapper/test_warmup.py`
- Run: `uv run pytest tests/autoscrapper/ -x -q`

### Common Patterns
- Subpackages are imported lazily to keep startup fast.
- Config is loaded once at startup and passed down; avoid re-reading from disk in hot paths.

## Dependencies

### Internal
- All subpackages depend on `config.py` for shared settings.

### External
- `textual` — TUI framework
- `uv` — runtime environment management
