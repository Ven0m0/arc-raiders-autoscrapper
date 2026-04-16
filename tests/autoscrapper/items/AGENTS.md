<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-15 | Updated: 2026-04-15 -->

# tests/autoscrapper/items/

## Purpose
Tests for `src/autoscrapper/items/` — rule store loading, merging, custom-over-default precedence, and rule file I/O.

## Key Files

| File | Description |
|------|-------------|
| `test_rules_store.py` | Tests for `RulesStore`: load from custom path, fall back to defaults, custom-over-default precedence, missing file handling. |

## For AI Agents

### Working In This Directory
- Always test that a custom rule for an item beats the default rule for the same item.
- Use `tmp_path` for any test that writes rule files.

### Testing Requirements
Run: `uv run pytest tests/autoscrapper/items/ -x -q`
