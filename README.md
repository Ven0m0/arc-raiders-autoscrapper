# Arc Raiders Inventory Auto Scrapper

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff) [![Maintainability](https://qlty.sh/gh/Ven0m0/projects/arc-raiders-autoscrapper/maintainability.svg)](https://qlty.sh/gh/Ven0m0/projects/arc-raiders-autoscrapper)

<p align="center">
  <img src="https://github.com/user-attachments/assets/c1de27b2-4dd9-4d04-855a-b4faa4e9dd1a" alt="autoscrapper_logo4">
</p>

Automates Arc Raiders inventory actions (Sell/Recycle) using screen capture and Tesseract (OCR).

> This program does not hook into the game process, but there is no guarantee it will not be flagged by anti-cheat systems or violate the game's Terms of Service. **Use at your own risk.**

---

## Setup

This repo uses [uv](https://docs.astral.sh/uv/) to manage Python and dependencies.

- `uv sync` is enough for cloud/CI tasks that only need the project plus dev tooling.
- Linux desktop automation also needs the optional `linux-input` extra, which the setup script installs for you.
- The repo is pinned to Python 3.13 via `.python-version`.

### Clone

```bash
git clone https://github.com/Ven0m0/arc-raiders-autoscrapper.git
cd arc-raiders-autoscrapper
```

### Windows 10/11 (64-bit)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\setup-windows.ps1
# Specify a Python version explicitly:
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\setup-windows.ps1 -PythonVersion 3.13
```

### Linux

```bash
bash scripts/setup-linux.sh
# Or with an explicit Python version:
PYTHON_VERSION=3.13 bash scripts/setup-linux.sh
# Manual full install:
uv sync --extra linux-input
```

---

## Usage

```bash
# Open the Textual UI (default):
uv run autoscrapper

# Start a scan directly (safe dry-run — no clicks):
uv run autoscrapper scan --dry-run

# Live scan:
uv run autoscrapper scan
```

`scan` supports the optional `--dry-run` flag. All other workflows are in the Textual UI.

**How it works:**

1. Open your inventory and scroll to the top.
2. Start the scan, then alt-tab back into the game. Scanning begins after a short delay.
3. Press the configured stop key (default: `Esc`) to abort. Multiple presses may be needed.

**Linux:** Default target window title is `Arc Raiders`. Override with `AUTOSCRAPPER_TARGET_APP` if needed.

---

## Automated Data Updates

A scheduled GitHub Actions workflow refreshes game data and default rules daily.

| Field | Value |
|---|---|
| Workflow | `.github/workflows/daily-data-update.yml` |
| Schedule | Daily at `14:00 UTC` |
| Output | Updates snapshot data + `items_rules.default.json`, then opens/updates a PR on `bot/daily-data-update` |
| Report | Attaches `artifacts/update-report.json`; uses `artifacts/update-report.md` as the PR body |

Default rules are regenerated with this baseline:

- All quests completed
- Workshop profile at level 2 for: `scrappy`, `weapon_bench`, `equipment_bench`, `med_station`, `explosives_bench`, `utility_bench`, and `refiner`

### Data sources

The updater uses a layered source strategy. MetaForge is preferred; arctracker.io and RaidTheory supplement or fill gaps; the Arc Raiders Wiki adds optional enrichment.

| Source | Purpose | Behaviour |
|---|---|---|
| [MetaForge ARC Raiders API](https://metaforge.app/arc-raiders/api) | Primary item and quest source | Reads paginated `/items` and `/quests` from `https://metaforge.app/api/arc-raiders` |
| MetaForge Supabase (optional) | Crafting and recycle relationships | Adds recipe and `recyclesInto` data when `METAFORGE_SUPABASE_ANON_KEY` is set |
| [arctracker.io](https://arctracker.io) | Secondary item, quest, hideout, and project source | Public API at `https://arctracker.io/api/*`; supplements MetaForge and activates as fallback |
| [fgrzesiak/arcraiders-data](https://github.com/fgrzesiak/arcraiders-data) | Fallback item and quest source | Downloaded as a zip archive; fills missing records when MetaForge or arctracker are unavailable |
| [Arc Raiders Wiki loot table](https://arcraiders.wiki/wiki/Loot) | Optional workshop/expedition/project-use enrichment | Adds a `wikiUses` field when the `scraper` extra is installed |

### MetaForge API reference

[API documentation](https://metaforge.app/arc-raiders/api) · Base URL: `https://metaforge.app/api/arc-raiders`

AutoScrapper uses two paginated endpoints during snapshot refresh:

| Endpoint | Parameters | Purpose |
|---|---|---|
| `GET /items` | `page`, `limit` | Item records, sell prices, stack sizes, recycle components, and pagination metadata |
| `GET /quests` | `page`, `limit` | Quest records, reward items, and requirement payloads |

MetaForge can change or break these endpoints without warning and asks consumers to cache results locally. AutoScrapper follows that guidance by querying MetaForge only during snapshot refreshes, then reading the generated JSON files at runtime instead of calling the API while scanning.

If you reuse this updater or publish derived data, keep MetaForge attribution and link back to `https://metaforge.app/arc-raiders` as required by the API terms.

### arctracker.io API reference

[API documentation](https://arctracker.io/developers/docs) · Base URL: `https://arctracker.io`

arctracker.io provides two tiers of endpoints: public game-data endpoints used during snapshot refreshes, and authenticated user-progress endpoints used by the `ArcTrackerClient` in `src/autoscrapper/api/client.py`.

All responses use a `{"data": [...]}` envelope. Rate limit is 500 requests/hour; the client enforces a conservative 8-second minimum interval between requests.

**Public endpoints (no authentication required)**

| Endpoint | Purpose | Item fields |
|---|---|---|
| `GET /api/items` | All game items | `id`, `name`, `type`, `rarity`, `value`, `weightKg`, `stackSize`, `craftBench`, `updatedAt` |
| `GET /api/quests` | All quests | quest metadata and requirements |
| `GET /api/hideout` | All hideout modules | module metadata |
| `GET /api/projects` | All projects | project metadata |

**Authenticated endpoints (requires `X-App-Key` + `Authorization: Bearer <user_key>`)**

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/v2/user/profile` | GET | User profile |
| `/api/v2/user/quests` | GET | User quest progress (params: `locale`, `filter`) |
| `/api/v2/user/rounds` | GET | Raid history (params: `locale`, `limit`, `offset`, `outcome`, `map`, `season`) |
| `/api/v2/user/stash` | GET | Stash contents, paginated (`totalSlots`, `usedSlots`, `items`) |
| `/api/v2/user/hideout` | GET | Hideout upgrade progress |
| `/api/v2/user/projects` | GET | Project completion progress (params: `locale`, `season`) |
| `/api/v2/user/loadout` | GET | Current loadout |
| `/api/v2/user/blueprints` | GET | Unlocked blueprints (params: `locale`, `filter`) |

Configure API keys in the app settings or via environment:

```bash
# App identifier (registers your integration with arctracker)
export ARCTRACKER_APP_KEY=...
# Per-user bearer token (grants access to /api/v2/user/* endpoints)
export ARCTRACKER_USER_KEY=...
```

### RaidTheory fallback

The updater downloads the [`fgrzesiak/arcraiders-data`](https://github.com/fgrzesiak/arcraiders-data) repository archive and uses it in two cases:

1. Appends item or quest records that are missing from MetaForge and arctracker.io.
2. Falls back to the RaidTheory dataset when both upstream sources fail.

MetaForge remains the preferred source when multiple providers return the same record ID.
`metadata.json` records which provider supplied each final item and quest dataset.

### Arc Raiders Wiki enrichment

When the optional `scraper` extra is installed (`uv sync --extra scraper`), the updater also fetches the [Arc Raiders Wiki loot table](https://arcraiders.wiki/wiki/Loot) and adds a `wikiUses` field to each item containing workshop upgrade requirements, expedition requirements, and project-use data from the loot table.

Wiki enrichment is supplemental — it does not replace any MetaForge field. A failed wiki fetch is logged as a warning and the update continues without wiki data. The `metadata.json` `dataSources.items.wikiEnrichment` block records the URL, availability, match count, and any error.

### Run the updater locally

```bash
# Optional: enable crafting/recycle enrichment from MetaForge Supabase
export METAFORGE_SUPABASE_ANON_KEY=...

# Optional: enable Arc Raiders Wiki enrichment (wikiUses field)
uv sync --extra scraper

# Real update (writes tracked files):
uv run python scripts/update_snapshot_and_defaults.py

# Dry run (no tracked file writes):
uv run python scripts/update_snapshot_and_defaults.py --dry-run
```
