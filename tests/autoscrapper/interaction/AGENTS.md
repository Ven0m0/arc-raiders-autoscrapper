<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-15 | Updated: 2026-04-15 -->

# tests/autoscrapper/interaction/

## Purpose
Tests for `src/autoscrapper/interaction/` — coordinate translation, keybind parsing, and window detection logic.

## Key Files

| File | Description |
|------|-------------|
| `test_ui_windows.py` | Tests for `ui_windows.py` — screen-space ↔ capture-space conversion, window bounds. |
| `test_keybinds.py` | Tests for `keybinds.py` — keybind round-trip serialization and key name validation. |

## For AI Agents

### Working In This Directory
- Window/screen coordinate tests must not assume a specific monitor resolution — use parametrized fixtures.
- Input driver calls must be mocked — never send real mouse/keyboard events from tests.

### Testing Requirements
Run: `uv run pytest tests/autoscrapper/interaction/ -x -q`
