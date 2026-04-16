<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-15 | Updated: 2026-04-15 -->

# tests/autoscrapper/core/

## Purpose
Tests for `src/autoscrapper/core/item_actions.py` — rule lookup, fuzzy matching, action resolution, and threshold behavior.

## Key Files

| File | Description |
|------|-------------|
| `test_item_actions.py` | Tests for `resolve_action()`: exact matches, fuzzy matches, no-match fallback, casing/whitespace edge cases. |

## For AI Agents

### Working In This Directory
- When changing the fuzzy threshold in `src/autoscrapper/core/item_actions.py`, add a test that verifies the boundary behavior (score at threshold, score just below threshold).
- Test action strings as lowercase — casing bugs are a known failure mode.

### Testing Requirements
Run: `uv run pytest tests/autoscrapper/core/ -x -q`
