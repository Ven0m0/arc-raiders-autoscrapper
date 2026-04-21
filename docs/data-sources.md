---
title: Data Sources
description: Game data sources used by AutoScrapper — priority order, endpoints, and output files
---

AutoScrapper pulls game data from four sources, layered by priority. MetaForge is
authoritative; arctracker.io and RaidTheory fill gaps; the Arc Raiders Wiki adds
`wikiUses` enrichment.

## Priority Order

```
MetaForge (primary)
  └─ arctracker.io (supplemental — fills missing IDs)
       └─ RaidTheory (fallback — used when MetaForge is unavailable)
            └─ Arc Raiders Wiki (enrichment — adds wikiUses field)
```

The `metadata.json` `dataSources` block records which provider supplied each dataset
and how many records each supplemental source contributed.

## MetaForge

| Field | Value |
|---|---|
| Base URL | `https://metaforge.app/api/arc-raiders` |
| Docs | `https://metaforge.app/arc-raiders/api` |
| Data | Items (sell prices, stack sizes, recycle components), quests |
| Auth | None required for public endpoints |

Endpoints used during snapshot refresh:

| Endpoint | Parameters | Returns |
|---|---|---|
| `GET /items` | `page`, `limit` | Paginated item records |
| `GET /quests` | `page`, `limit` | Paginated quest records |

Pages are fetched concurrently (up to 10 workers). MetaForge can change or remove
endpoints without warning; cache results locally and attribute MetaForge when
republishing derived data.

Optional Supabase enrichment adds `recipe` and `recyclesInto` fields when
`METAFORGE_SUPABASE_ANON_KEY` is set.

## arctracker.io

| Field | Value |
|---|---|
| Base URL | `https://arctracker.io` |
| Docs | `https://arctracker.io/developers/docs` |
| Data | Items, quests, hideout modules, projects, user progress |
| Rate limit | 500 req/hour (client enforces 8 s minimum interval) |

### Public endpoints (no auth)

Used during snapshot refresh to supplement MetaForge and provide hideout/project context.

| Endpoint | Returns | Saved to |
|---|---|---|
| `GET /api/items` | All game items | (merged into items.json) |
| `GET /api/quests` | All quests | (merged into quests.json) |
| `GET /api/hideout` | All hideout modules | `static/arctracker_hideout.json` |
| `GET /api/projects` | All projects | `static/arctracker_projects.json` |

All responses use the `{"data": [...]}` envelope.

### Authenticated endpoints

The `ArcTrackerClient` in `src/autoscrapper/api/client.py` exposes the full
`/api/v2/user/*` surface for per-user data. See [arctracker-api.md](arctracker-api.md).

## RaidTheory

| Field | Value |
|---|---|
| Repository | `https://github.com/RaidTheory/arcraiders-data` |
| Archive URL | `https://github.com/RaidTheory/arcraiders-data/archive/refs/heads/main.zip` |
| Data | Items and quests as individual JSON files |
| Auth | None |

Downloaded as a zip archive during each snapshot refresh. Used in two ways:

1. **Supplemental**: appends item/quest records whose IDs are absent from MetaForge.
2. **Full fallback**: replaces MetaForge entirely when MetaForge fetch fails.

MetaForge wins on record ID conflicts. `metadata.json` records the `supplementalCount`
contributed by RaidTheory.

## Arc Raiders Wiki

| Field | Value |
|---|---|
| URL | `https://arcraiders.wiki/wiki/Loot` |
| Data | `wikiUses` (workshop upgrades, expedition requirements, project use) |
| Dependencies | `requests`, `beautifulsoup4` (both in default deps — always active) |

The wiki loot table is scraped during every snapshot refresh. Each item with a
matching row receives a `wikiUses` string. A failed fetch is logged as a warning;
the update continues without wiki data.

`metadata.json` records `dataSources.items.wikiEnrichment.enrichedCount` and any error.

## Output Files

| File | Contents |
|---|---|
| `progress/data/items.json` | Merged and enriched item records |
| `progress/data/quests.json` | Merged quest records |
| `progress/data/quests_by_trader.json` | Quests grouped by trader |
| `progress/data/metadata.json` | Source attribution, counts, timestamps, error log |
| `progress/data/static/arctracker_hideout.json` | Raw hideout modules from arctracker.io |
| `progress/data/static/arctracker_projects.json` | Raw projects from arctracker.io |
| `items/items_rules.default.json` | Generated default KEEP/SELL/RECYCLE rules |
