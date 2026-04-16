<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-15 | Updated: 2026-04-15 -->

# tests/autoscrapper/

## Purpose
Tests for all `src/autoscrapper/` modules. Directory structure mirrors the source tree exactly. Top-level files test the package root; subdirectories test the corresponding source subpackage.

## Key Files

| File | Description |
|------|-------------|
| `test_config.py` | Tests for `config.py` — serialization, versioning, migration |
| `test_warmup.py` | Tests for `warmup.py` — OCR init ordering and warmup behavior |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `core/` | Tests for `src/autoscrapper/core/` |
| `interaction/` | Tests for `src/autoscrapper/interaction/` |
| `items/` | Tests for `src/autoscrapper/items/` |
| `ocr/` | Tests for `src/autoscrapper/ocr/` — includes failure corpus and fixture tests |
| `progress/` | Tests for `src/autoscrapper/progress/` |
| `scanner/` | Tests for `src/autoscrapper/scanner/` |

## For AI Agents

### Working In This Directory
- When adding a new source file, add a corresponding test file in the matching subdirectory.
- OCR tests may require Tesseract — tests that cannot run without a live game window must use `pytest.mark.skip`.
- Avoid importing application modules at module level if they trigger side effects (e.g. Tesseract init).

### Testing Requirements
- Run all: `uv run pytest tests/autoscrapper/ -x -q`
- Run one module: `uv run pytest tests/autoscrapper/ocr/ -x -q`

### Common Patterns
- Use `tmp_path` (pytest built-in) for any test that writes files.
- Parametrize over multiple item names / rule combinations rather than duplicating test functions.
