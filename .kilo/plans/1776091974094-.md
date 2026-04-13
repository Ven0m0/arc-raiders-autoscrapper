# Plan: Integrate arctracker.io API for Direct Stash Sync

## Goal
Implement arctracker.io API integration to fetch user stash, hideout, and projects data directly from their API, bypassing OCR and guaranteeing accurate data.

## API Overview

**Authentication**: Dual-key system
- App Key (`arc_k1_...`): Registered via Developer Dashboard
- User Key (`arc_u1_...`): Created by users in Settings > Developer Access

**Endpoints to Implement**:
- `GET /api/v2/user/stash` - User inventory with enriched item data
- `GET /api/v2/user/hideout` - Hideout module upgrade progress  
- `GET /api/v2/user/projects` - Project phase completion progress

**Rate Limits**: 500 requests/hour per app

---

## Implementation Phases

### Phase 1: Configuration & Data Models

**Files to modify/create:**
1. `src/autoscrapper/config.py` - Add API settings dataclass
2. `src/autoscrapper/api/` - New package for arctracker integration

**Details:**
- Add `ArctrackerSettings` dataclass with:
  - `app_key: str | None` - Developer app key
  - `user_key: str | None` - User personal key
  - `enable_sync: bool` - Enable API sync feature
  - `auto_fetch_on_scan: bool` - Automatically fetch from API before scan
- Bump `CONFIG_VERSION` to 6 with migration
- Create `src/autoscrapper/api/__init__.py` and `src/autoscrapper/api/client.py`

**Data Models for API Responses:**
```python
# Stash API response structure
class StashItem:
    item_id: str
    name: str
    quantity: int
    slot: int | None
    type: str
    rarity: str
    value: int

class StashResponse:
    items: list[StashItem]
    total_slots: int
    used_slots: int

# Hideout API response structure  
class HideoutModule:
    module_id: str
    name: str
    current_level: int
    max_level: int

# Projects API response structure
class ProjectProgress:
    project_id: str
    name: str
    current_phase: int
    max_phases: int
    completed: bool
```

### Phase 2: API Client Implementation

**New file: `src/autoscrapper/api/client.py`**

**Features:**
- `ArctrackerClient` class with:
  - `__init__(app_key: str | None, user_key: str | None)`
  - `get_stash(locale="en", page=1, per_page=500) -> StashResponse`
  - `get_hideout(locale="en") -> list[HideoutModule]`
  - `get_projects(locale="en", season=None) -> list[ProjectProgress]`
  - Rate limit tracking via response headers
  - Error handling for 401/403/404/429/500
  - Retry logic with exponential backoff

**Rate Limit Handling:**
- Parse `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` headers
- Pre-emptive throttling when near limit
- User-friendly error messages for 429 (rate limited)

### Phase 3: TUI Settings Screen

**Files to modify:**
1. `src/autoscrapper/tui/settings.py` - Add new settings screen
2. `src/autoscrapper/tui/app.py` - Add menu item

**New Screen: `ArctrackerSettingsScreen`**
- Input field for App Key (with masking/show toggle)
- Input field for User Key (with masking/show toggle)
- Checkbox for "Enable API sync"
- Checkbox for "Auto-fetch on scan"
- "Test Connection" button to validate keys
- Help text explaining how to get keys from arctracker.io

**Menu Integration:**
- Add "API Sync (arctracker.io)" option in Settings menu

### Phase 4: API-Based Data Source

**New file: `src/autoscrapper/api/datasource.py`**

**Purpose:**
- Alternative to OCR-based stash detection
- Implements same interface as OCR scanner for drop-in replacement

**Key Functions:**
- `fetch_stash_as_scan_results() -> list[ItemActionResult]`
  - Fetches from API
  - Converts to `ItemActionResult` format
  - Applies same decision rules as OCR scan
- `sync_hideout_to_progress_settings() -> ProgressSettings`
  - Fetches hideout from API
  - Updates local progress settings
- `sync_projects_to_progress_settings()`
  - Fetches projects from API
  - Updates local progress settings

### Phase 5: Scan Mode Selection

**Files to modify:**
1. `src/autoscrapper/tui/scan.py` - Add API sync option
2. `src/autoscrapper/scanner/engine.py` - Support API data source

**UI Changes:**
- In Scan menu, when API keys are configured:
  - "Scan via API (arctracker.io)" option
  - "Traditional OCR Scan" option
  - Show last sync time if available

**Engine Changes:**
- `scan_inventory()` parameter: `data_source: Literal["ocr", "api"] = "ocr"`
- When `data_source="api"`:
  - Skip window detection
  - Skip grid detection
  - Skip OCR entirely
  - Fetch from API and convert to same result format
  - Still apply actions/decisions
  - Still support dry-run mode

### Phase 6: Progress Auto-Sync

**Files to modify:**
1. `src/autoscrapper/progress/progress_config.py` - Add API sync methods

**Features:**
- Auto-populate hideout levels from API
- Auto-populate project progress from API
- Option to use API as "source of truth" for progress settings
- Manual "Sync from arctracker.io" button in Progress screens

### Phase 7: Testing & Validation

**Tests to add:**
1. Unit tests for API client (mock responses)
2. Unit tests for data conversion
3. Integration test with test API keys
4. Rate limit handling tests

**Validation checklist:**
- [ ] API client handles all error codes correctly
- [ ] Rate limiting works without crashing
- [ ] Data conversion produces same format as OCR scan
- [ ] Decision rules apply correctly to API data
- [ ] UI screens work with and without API keys configured
- [ ] Config migration works correctly

---

## Clarifications (User Input)

1. **App Key**: Each user registers their own app at arctracker.io Developer Dashboard (not a shared app key).

2. **Public Endpoints**: The public endpoints (`/api/items`, `/api/quests`, `/api/hideout`, `/api/projects`) require **no authentication** and can always be used.

3. **User Endpoints**: User-specific endpoints (`/api/v2/user/*`) require **both** app key AND user key.

4. **Fallback Behavior**: Auto-fallback to OCR if API fails (rate limited, invalid keys, network error).

---

## Open Questions

1. **Data Freshness**: How should we handle the fact that API data might be stale (synced from game at unknown time)?
   - **Recommendation**: Show "Last synced: X minutes ago" warning if data is >1 hour old

2. **Item Name Mapping**: The API returns item IDs (e.g., "advanced-arc-powercell") but the OCR returns display names (e.g., "Advanced ARC Powercell"). How to reconcile?
   - **Recommendation**: Use the existing `items.json` data which already has both `id` and `name` fields to map between them

---

## Files to Create/Modify

### New Files:
- `src/autoscrapper/api/__init__.py`
- `src/autoscrapper/api/client.py`
- `src/autoscrapper/api/models.py`
- `src/autoscrapper/api/datasource.py`
- `tests/api/test_client.py`

### Modified Files:
- `src/autoscrapper/config.py` - Add API settings, bump version
- `src/autoscrapper/tui/settings.py` - Add API settings screen
- `src/autoscrapper/tui/app.py` - Add menu integration
- `src/autoscrapper/tui/scan.py` - Add API scan option
- `src/autoscrapper/scanner/engine.py` - Support API data source
- `src/autoscrapper/progress/progress_config.py` - Add sync methods
- `pyproject.toml` - Add `requests` dependency (if not already present)

---

## Success Criteria

1. User can configure arctracker.io API keys in settings
2. User can fetch stash data directly from API without OCR
3. API-fetched data produces the same decision results as OCR
4. Hideout and project progress can be auto-synced from API
5. Rate limits are handled gracefully
6. All existing OCR functionality continues to work unchanged
