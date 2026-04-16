<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-15 | Updated: 2026-04-15 -->

# tests/

## Purpose
Pytest test suite for the autoscrapper application. Mirrors the `src/autoscrapper/` module structure. All tests are run with `uv run pytest`.

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `autoscrapper/` | Tests for the main application modules (see `autoscrapper/AGENTS.md`) |
| `scripts/` | Tests for developer scripts in `scripts/` |

## For AI Agents

### Working In This Directory
- Test layout mirrors `src/autoscrapper/` exactly — when adding a new module, add a corresponding test file.
- Fixtures and parametrize decorators are preferred over code duplication.
- OCR tests (`autoscrapper/ocr/`) require Tesseract to be installed; they are skipped automatically on CI if Tesseract is absent.

### Testing Requirements
- Run the full suite: `uv run pytest`
- Run a specific subdirectory: `uv run pytest tests/autoscrapper/ocr/ -x -q`
- After OCR changes, also run corpus replay: `uv run python scripts/replay_ocr_failure_corpus.py`

### Common Patterns
- `conftest.py` (if present at root) provides shared fixtures.
- OCR fixture images live alongside test files in `autoscrapper/ocr/`.
- Use `pytest.mark.skip` with a reason when a test requires a live game window.

## Dependencies

### Internal
- All of `src/autoscrapper/` — tests import application code directly via the installed package.

### External
- `pytest` — test runner
- `pytest-cov` — coverage (optional)
