<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-15 | Updated: 2026-04-15 -->

# api/

## Purpose
MetaForge/ArcTracker API client and data models. Fetches game data (items, quests, hideout modules, projects) from the community API to populate the progress snapshot and default rules.

## Key Files

| File | Description |
|------|-------------|
| `client.py` | `ArcTrackerClient` — HTTP client for the MetaForge public API. Methods: `get_public_hideout()`, `get_public_projects()`, etc. |
| `datasource.py` | `ApiDatasource` — translates API item stash responses into `ItemActionResult` objects for the scanner. Uses `item.slot` if available, falls back to iteration index for cell mapping. |
| `models.py` | Pydantic/dataclass models for API response shapes (items, quests, hideout modules). |
| `__init__.py` | Package init — no side effects. |

## For AI Agents

### Working In This Directory
- `client.py` is the **only** place that makes outbound HTTP calls. Do not add direct `requests`/`httpx` calls elsewhere.
- `datasource.py` maps `slot_idx // 20` for page and `slot_idx % 20` for cell — the 4×5 grid assumption (20 items/page) is hardcoded; change here if grid size changes.
- API responses may be `None` — always guard with `(response or {}).get(...)` before indexing.

### Testing Requirements
- No dedicated test file currently exists. New client methods should be tested with mocked HTTP responses.

### Common Patterns
- `ArcTrackerClient` is instantiated fresh per call in scripts; it is not a singleton.
- `datasource.py` produces `Cell` objects with `(page, row, col)` coordinates for the scanner.

## Dependencies

### Internal
- `src/autoscrapper/scanner/types.py` — `Cell`, `ItemActionResult`
- `src/autoscrapper/progress/decision_engine.py` — decision resolution for stash items

### External
- HTTP library (check `pyproject.toml` for `httpx` or `requests`)
