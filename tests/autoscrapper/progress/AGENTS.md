<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-15 | Updated: 2026-04-15 -->

# tests/autoscrapper/progress/

## Purpose
Tests for `src/autoscrapper/progress/` — data loading, snapshot update, rule generation, quest inference, and update report formatting.

## Key Files

| File | Description |
|------|-------------|
| `test_data_loader.py` | Tests for `data_loader.py`: missing file defaults, malformed JSON handling, typed output. |
| `test_data_update.py` | Tests for `data_update.py`: snapshot update logic, API mock responses. |
| `test_rules_generator.py` | Tests for `rules_generator.py`: rule output for given quest/hideout state, `completed_projects` parameter. |
| `test_progress_config.py` | Tests for `progress_config.py`: `ProgressSettings` serialization and defaults. |
| `test_update_report.py` | Tests for `update_report.py`: report formatting and diff output. |

## For AI Agents

### Working In This Directory
- `test_rules_generator.py` must pass `completed_projects` to `generate_rules_from_active()`.
- Mock MetaForge API calls with fixture data — do not make live API calls in tests.
- Use `tmp_path` for snapshot write tests.

### Testing Requirements
Run: `uv run pytest tests/autoscrapper/progress/ -x -q`
