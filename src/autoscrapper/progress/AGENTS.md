<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-15 | Updated: 2026-04-15 -->

# progress/

## Purpose
Quest, hideout, and crafting data management plus default-rule generation. Fetches live game data from the MetaForge API, persists it as a snapshot, and generates the bundled `items_rules.default.json` based on what items are needed for active quests and hideout upgrades.

## Key Files

| File | Description |
|------|-------------|
| `data_update.py` | `update_data_snapshot()` — fetches fresh data from MetaForge API and writes `data/*.json`. Called by the updater script. |
| `rules_generator.py` | `generate_rules_from_active()` — generates default rules from quest/hideout state. Accepts `active_quests`, `hideout_levels`, `completed_projects`. |
| `decision_engine.py` | `DecisionEngine` — suppresses sell/recycle for items needed by incomplete quests or hideout modules. Called from the scanner. |
| `data_loader.py` | Loads and validates `data/*.json` files into typed structures. |
| `quest_inference.py` | Infers which quests are active/complete from progress state. |
| `quest_overrides.py` | Manual quest state overrides (user-defined exceptions). |
| `progress_config.py` | `ProgressSettings` dataclass — user-configured progress state (trader levels, etc.). |
| `update_report.py` | Generates the `artifacts/update-report.md` after a data refresh. |
| `recipe_utils.py` | Helpers for crafting recipe traversal. |
| `weapon_grouping.py` | Groups weapon variants for rule generation. |
| `__init__.py` | Package init — no side effects. |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `data/` | Generated JSON snapshots — **do not hand-edit** (see `tests/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- **Never hand-edit `data/*.json`** — regenerate via `scripts/update_snapshot_and_defaults.py`.
- `rules_generator.py` now accepts `completed_projects` parameter — do not call without it.
- `decision_engine.py` checks `ProgressSettings` to determine which items to protect. If an item is being kept unexpectedly, verify the quest/hideout state is current.
- Changes to `data_update.py` or `rules_generator.py` often require regenerating bundled data — run `scripts/update_snapshot_and_defaults.py --dry-run` first.

### Testing Requirements
- `tests/autoscrapper/progress/test_data_loader.py`
- `tests/autoscrapper/progress/test_data_update.py`
- `tests/autoscrapper/progress/test_rules_generator.py`
- `tests/autoscrapper/progress/test_progress_config.py`
- `tests/autoscrapper/progress/test_update_report.py`
- Run: `uv run pytest tests/autoscrapper/progress/ -x -q`

### Common Patterns
- `data_loader.py` returns empty defaults (not exceptions) on missing/malformed files.
- Quest inference uses a dependency graph from `src/autoscrapper/progress/data/quests_graph.json`.
- `update_data_snapshot()` overwrites files in place — always use `--dry-run` in a temp dir first.

## Dependencies

### Internal
- `src/autoscrapper/api/client.py` — MetaForge API for data refresh
- `src/autoscrapper/items/items_rules.default.json` — output target for rule generation
- `src/autoscrapper/scanner/scan_loop.py` — consumes `DecisionEngine` decisions

### External
- Standard library `json`, `pathlib`
