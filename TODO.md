# TODO — arc-raiders-autoscrapper fork improvements

**Updated:** 2026-04-14  
**Source:** Codebase audit + diff against `zappybiby/ArcRaiders-AutoScrapper` base  
**Reference issues:** Ven0m0/arc-raiders-autoscrapper#41 (TODO tracker), #22 (Renovate dashboard)

---

## Priority 1 — Bug Fixes

### BUG-01: Stale infobox rect causes wrong OCR crops at session end
**Status:** Open  
**File:** `src/autoscrapper/scanner/scan_loop.py`  
**Function:** `_ScanRunner._ocr_infobox_with_retries` (retry loop, `ocr_attempt > 0`)  
**Symptom:** OCR retry passes reuse the previously-detected infobox rect without
re-detecting. When the context menu closes between attempts the scanner crops the
"TAB | CLOSE" button bar at screen bottom, producing empty or garbage item names.  
**Fix:** On retry, re-capture the full window and call `find_infobox()` for a fresh
rect. Break early if detection returns `None` (menu closed).

```python
# In the ocr_attempt > 0 branch:
window_bgr = capture_region((win_left, win_top, win_width, win_height))
new_rect = find_infobox(window_bgr)
if new_rect is None:
    break  # infobox closed; abort retry
x, y, w, h = new_rect
infobox_bgr = window_bgr[y : y + h, x : x + w]
```

See PLAN.md T010 for full acceptance criteria.

---

## Priority 2 — OCR Quality Improvements

### OCR-01: Roman numeral tier suffix correction
**Status:** Partial — OCR pipeline has `_ROMAN_NUMERAL_FIXES` in `inventory_vision.py:83–87`,
but `normalize_item_name()` in `item_actions.py:50` applies no alias correction.
Rule lookups remain vulnerable when the OCR-level fix misses a case.  
**File:** `src/autoscrapper/core/item_actions.py`  
**Fix:** Add `OCR_ALIASES` dict and `_fix_roman_ocr_suffix()` called from
`normalize_item_name()`. See PLAN.md T012.

```python
OCR_ALIASES: dict[str, str] = {
    " 1v": " iv",
    " 111": " iii",
    " 11": " ii",
    " 1": " i",
}
```

### OCR-02: Weapon swap UI text contaminates item name detection
**Status:** Open  
**File:** `src/autoscrapper/ocr/inventory_vision.py`  
**Function:** `_extract_title_from_data`  
**Fix:** Add `_EXCLUDED_UI_KEYWORDS = frozenset(["swap with", "swap"])`. Skip
matching lines on first pass. On retry (`_retry_with_larger=True`), widen
`top_fraction` to `0.35`. See PLAN.md T013.

### ~~OCR-03: `clean_ocr_text` too restrictive — drops valid punctuation~~
**Status:** Done — `item_actions.py:57` already uses the permissive character
class `[^-A-Za-z0-9 '(),.!?:&+]+`.

---

## Priority 3 — Data Pipeline Improvements

### DATA-01: Remove Supabase dependency from data_update.py
**Status:** Open  
**File:** `src/autoscrapper/progress/data_update.py`  
**Issue:** Active Supabase code at lines 26, 33, 284–313, 738–749. The
`SUPABASE_ANON_KEY` reads from env but the URL is hardcoded — committed
credential, external service risk.  
**Fix:** Use `?includeComponents=true` on the MetaForge `/items` API instead.
Extract components inline with `_extract_component_dict()`. Remove all Supabase
symbols. See PLAN.md T014.

### DATA-02: Refresh data snapshot
**Status:** Current — snapshot at `src/autoscrapper/progress/data/` was last
updated 2026-04-13T06:31:59Z (547 items, 94 quests). Re-run
`python3 -m uv run python scripts/update_snapshot_and_defaults.py` before each
release to keep default rules fresh.

---

## Priority 4 — UX / Configuration

### UX-01: Change default stop key from Escape to F9
**Status:** Open  
**File:** `src/autoscrapper/interaction/keybinds.py:5`  
**Fix:**
```python
DEFAULT_STOP_KEY = "f9"
# Add to _CANONICAL_DISPLAY:
"f9": "F9",
```
See PLAN.md T015.

---

## Priority 5 — Type Safety / Debt

### DEBT-01: ScanSettingsScreen missing ABC inheritance
**Status:** Open  
**File:** `src/autoscrapper/tui/settings.py:92`  
**Issue:** `@abstractmethod` is applied to `_compose_form` and `_load_into_fields`
but `ScanSettingsScreen` does not inherit `ABC`, so the decorator has no enforcement.  
**Fix:** `class ScanSettingsScreen(AppScreen, ABC):` and add `ABC` to the import.
See PLAN.md T017.

---

## Priority 6 — Features

### FEAT-01: Complete arctracker.io API integration
**Status:** In progress (~60%)  
**Files:** `src/autoscrapper/api/`, `src/autoscrapper/tui/api_settings.py`,
`src/autoscrapper/config.py`  
**Done:** API package created, `ApiSettings` dataclass, `ApiSettingsScreen`.  
**Remaining:** Wire API scan mode into `scan.py` / `engine.py`, graceful OCR
fallback, rate-limit handling, `tests/api/test_client.py`. See PLAN.md T016.

### FEAT-02: Headless scan mode with structured output
**Status:** Not started  
**Description:** `autoscrapper scan --headless --output json` for automation and
external tool integration. See PLAN.md T018.

### FEAT-03: Per-session decision log
**Status:** Not started  
**Description:** Append-only JSONL at `artifacts/sessions/` capturing per-item
decisions with match score and source. Feeds rule refinement workflow. See
PLAN.md T019.

### FEAT-04: Integrate ARC Safe Recycle logic
**Reference:** https://github.com/thanhn062/ARC-Safe-Recycle  
**Issue:** Ven0m0/arc-raiders-autoscrapper#41  
**Description:** Cross-reference items against active quest requirements before
recycling to prevent accidental destruction of needed items.

### FEAT-05: Integrate Raider Lens overlay features
**Reference:** https://github.com/eli1776/raider-lens  
**Issue:** Ven0m0/arc-raiders-autoscrapper#41  
**Description:** Review raider-lens for overlay/display features that could
complement the scanner's TUI output.

---

## Priority 7 — CI / Dev Tooling

### CI-01: Verify pytest is accessible in all install paths
**File:** `pyproject.toml`  
**Status:** `pytest>=9.0.3` is in both `[project.optional-dependencies.dev]` and
`[dependency-groups.dev]`. Ensure setup docs (`README.md`,
`scripts/setup-linux.sh`) reference `uv sync --group dev` so pytest is
available without extra flags.

---

## Upstream sync checklist

When merging from `zappybiby/ArcRaiders-AutoScrapper` apply in order:

- [ ] BUG-01: Stale infobox rect fix (`scan_loop.py`)
- [x] ~~BUG-02: Dead code removal~~ (`inventory_vision.py`) — already removed
- [ ] OCR-01: Roman numeral alias correction (`item_actions.py`) — partial
- [ ] OCR-02: Weapon swap UI keyword filter (`inventory_vision.py`)
- [x] ~~OCR-03: Permissive `clean_ocr_text` regex~~ — already in fork
- [ ] DATA-01: Remove Supabase, use `includeComponents=true` (`data_update.py`)
- [ ] DATA-02: Commit fresh data snapshot + regenerated default rules
- [ ] UX-01: F9 as default stop key (`keybinds.py`)
- [ ] CI-01: Verify pytest install path in setup docs
