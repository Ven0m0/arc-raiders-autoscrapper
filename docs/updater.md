---
title: Data Updater
description: How to run scripts/update_snapshot_and_defaults.py — CLI flags, data flow, output artifacts
---

`scripts/update_snapshot_and_defaults.py` refreshes the bundled game data snapshot and
regenerates the default item rules. It is run by the daily GitHub Actions workflow and
can be run locally on demand.

## Quick Start

```bash
# Dry run — fetches and diffs without writing tracked files
uv run python scripts/update_snapshot_and_defaults.py --dry-run

# Real update — writes tracked files
uv run python scripts/update_snapshot_and_defaults.py

# Real update (writes tracked files)
uv run python scripts/update_snapshot_and_defaults.py
```

Wiki enrichment runs by default — no extra install step required.

## CLI Flags

| Flag | Default | Purpose |
|---|---|---|
| `--dry-run` | off | Fetch and diff in a temp dir; do not write tracked files |
| `--data-dir PATH` | `src/autoscrapper/progress/data` | Override the data directory |
| `--rules-path PATH` | `src/autoscrapper/items/items_rules.default.json` | Override the rules output path |
| `--report-json PATH` | `artifacts/update-report.json` | Machine-readable report output |
| `--report-md PATH` | `artifacts/update-report.md` | Markdown summary report output |
| `--sample-limit N` | `10` | Max entries in markdown diff samples |

## Data Flow

```
1. update_data_snapshot(data_dir)
   ├─ Fetch MetaForge items + quests (parallel pages)
   ├─ Fetch arctracker.io items + quests + hideout + projects
   ├─ Download RaidTheory archive (fallback / supplemental)
   ├─ Scrape Arc Raiders Wiki loot table (wikiUses enrichment)
   └─ Write items.json, quests.json, quests_by_trader.json, metadata.json,
      static/arctracker_hideout.json, static/arctracker_projects.json

2. _fetch_default_user_context(data_dir)
   ├─ Read static/arctracker_hideout.json → hideout_levels (max level 2 per module)
   └─ Read static/arctracker_projects.json → completed_projects (all IDs)

3. generate_rules_from_active(...)
   └─ All quests completed + derived hideout/project context → default rules

4. write_rules(rules_payload, rules_path)
   └─ Writes items_rules.default.json
```

## Tracked Files

These are the files a real (non-dry-run) update can modify:

```
src/autoscrapper/progress/data/items.json
src/autoscrapper/progress/data/quests.json
src/autoscrapper/progress/data/quests_by_trader.json
src/autoscrapper/progress/data/metadata.json
src/autoscrapper/items/items_rules.default.json
```

Timestamp-only changes are filtered out of the diff — a run that only updates
`lastUpdated` does not count as a real change.

## Output Artifacts

### `artifacts/update-report.json`

Machine-readable report used as the GitHub Actions PR body source.

Key fields:

| Field | Description |
|---|---|
| `mode` | `"dry-run"` or `"write"` |
| `snapshot.beforeItemCount` / `afterItemCount` | Item counts before and after |
| `snapshot.changedFiles` | List of tracked files that changed |
| `quests` | Added/removed/changed quest diff |
| `rules` | Added/removed/changed rules diff |
| `assumptions.workshopIds` | Hideout module IDs used for level-2 defaults |

### `artifacts/update-report.md`

Human-readable markdown summary used as the PR body in the daily CI workflow.

## Default Rules Assumptions

The generated `items_rules.default.json` assumes:

- All quests are completed (`all_quests_completed=True`, `active_quests=[]`)
- All hideout modules fetched from arctracker.io are set to level 2 (or `maxLevel` if lower)
- Excluded module IDs: `stash`, `workbench` (never raised to level 2)
- All projects from arctracker.io are marked completed

## Timestamps and Idempotency

The diff logic strips volatile keys (`generatedAt`, `lastUpdated`, `lastupdated`) before
comparing before/after JSON. A run that produces semantically identical data with only
updated timestamps reports zero changed files and does not open a new PR in CI.

## Related Files

| File | Purpose |
|---|---|
| `src/autoscrapper/progress/data_update.py` | Core fetch, normalize, and merge logic |
| `src/autoscrapper/progress/rules_generator.py` | Default rules generation |
| `src/autoscrapper/progress/update_report.py` | Report building and diff helpers |
| `.github/workflows/daily-data-update.yml` | CI workflow that runs this script daily |
| `docs/data-sources.md` | Data source reference |
