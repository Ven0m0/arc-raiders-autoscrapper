<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-15 | Updated: 2026-04-15 -->

# progress/data/

## Purpose
Generated JSON snapshots of game data: items, quests, quest dependency graph, and trader-grouped quests. All files here are **machine-generated** — do not hand-edit.

## Key Files

| File | Description |
|------|-------------|
| `items.json` | All game items with metadata (names, categories, trader values). |
| `quests.json` | All quests with objectives and item requirements. |
| `quests_by_trader.json` | Quests grouped by trader for the progress review UI. |
| `quests_graph.json` | Quest dependency graph used by `quest_inference.py`. |
| `metadata.json` | Snapshot metadata: API version, `generatedAt` timestamp, data hash. |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `static/` | Static reference data that changes rarely (hideout modules, projects) |

## For AI Agents

### Working In This Directory
- **Never hand-edit any file here.** Regenerate via `scripts/update_snapshot_and_defaults.py`.
- Volatile timestamp keys (`generatedAt`, `lastUpdated`, `lastupdated`) are excluded from diff comparisons in the updater script — do not add logic that depends on these being stable.
- After regeneration, commit all changed files in `data/` together with the corresponding `items_rules.default.json`.
