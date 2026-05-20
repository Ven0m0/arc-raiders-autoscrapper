---
title: arctracker.io API Reference
description: Public and authenticated endpoints used by AutoScrapper from the arctracker.io API
---

AutoScrapper uses [arctracker.io](https://arctracker.io) for two purposes:

- **Snapshot refresh** — public game-data endpoints supply items, quests, hideout modules,
  and projects during `update_snapshot_and_defaults.py` runs.
- **User-progress API** — the `ArcTrackerClient` in `src/autoscrapper/api/client.py`
  provides per-user stash, quest progress, and raid history for live integration.

Full API documentation: `https://arctracker.io/developers/docs`

## Connection Details

| Field | Value |
|---|---|
| Base URL | `https://arctracker.io` |
| Response envelope | `{"data": [...]}` for list endpoints |
| Rate limit | 500 req/hour |
| Client interval | 8 s minimum between requests (conservative margin) |
| User-Agent | `ArcRaiders-AutoScrapper/0.2.0` |

## Public Endpoints

No authentication required. Used during snapshot refresh via `urllib` (no `requests` needed).

| Endpoint | Method | Returns |
|---|---|---|
| `/api/items` | GET | All game items |
| `/api/quests` | GET | All quests |
| `/api/hideout` | GET | All hideout modules |
| `/api/projects` | GET | All projects |

### Item fields

```json
{
  "id": "string",
  "name": "string",
  "type": "string",
  "rarity": "string (lowercased)",
  "value": 0,
  "weightKg": 0.0,
  "stackSize": 1,
  "craftBench": "string | null",
  "updatedAt": "ISO-8601 timestamp"
}
```

## Authenticated Endpoints

Requires `X-App-Key` and `Authorization: Bearer <user_key>` headers.
The `ArcTrackerClient` handles auth, rate limiting, and retries automatically.

```python
from autoscrapper.api.client import create_client_from_config

client = create_client_from_config()   # reads from saved ApiSettings
if client.is_configured():
    stash = client.get_all_stash_items()
```

### Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/v2/user/profile` | GET | User profile |
| `/api/v2/user/quests` | GET | Quest progress (params: `locale`, `filter`) |
| `/api/v2/user/stash` | GET | Stash contents, paginated |
| `/api/v2/user/hideout` | GET | Hideout upgrade progress |
| `/api/v2/user/projects` | GET | Project completion (params: `locale`, `season`) |
| `/api/v2/user/rounds` | GET | Raid history (params: `locale`, `limit`, `offset`, `outcome`, `map`, `season`) |
| `/api/v2/user/loadout` | GET | Current loadout |
| `/api/v2/user/blueprints` | GET | Unlocked blueprints (params: `locale`, `filter`) |

### Stash response shape

```json
{
  "data": {
    "totalSlots": 100,
    "usedSlots": 42,
    "items": [
      { "id": "string", "name": "string", "slot": 1, "quantity": 1 }
    ]
  }
}
```

## Configuration

API keys are stored in `ApiSettings` (persisted via `config.py`). Set them through
the TUI settings screen or via environment variables:

```bash
ARCTRACKER_APP_KEY=<your-app-key>   # registers your integration
ARCTRACKER_USER_KEY=<bearer-token>  # grants /api/v2/user/* access
```

`create_client_from_config()` reads from saved settings automatically.
`client.is_configured()` returns `True` only when both keys are present.
