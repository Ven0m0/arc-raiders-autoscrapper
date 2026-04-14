# TODO — arc-raiders-autoscrapper fork improvements

**Generated:** 2026-04-14  
**Source:** codebase audit against PLAN.md tasks  
**Reference issues:** Ven0m0/arc-raiders-autoscrapper#41 (TODO tracker), #22 (Renovate dashboard)

---

## Priority 1 — OCR Quality Bugs

### OCR-01: Roman numeral tier suffix correction
**File:** `src/autoscrapper/core/item_actions.py`  
**Plan ref:** T012  
**Issue:** Tesseract misreads Roman numeral suffixes on ALL-CAPS weapon names: `IV→1V`, `III→111`, `II→11`, `I→1`. This causes rule lookups to fail for tiered weapons.  
`normalize_item_name()` (line 50) currently only strips and lowercases.  
**Fix:** Add `OCR_ALIASES` dict and `_fix_roman_ocr_suffix()` function called from `normalize_item_name()`.

```python
OCR_ALIASES: dict[str, str] = {
    " 1v": " iv",
    " 111": " iii",
    " 11": " ii",
    " 1": " i",
}

def _fix_roman_ocr_suffix(name: str) -> str:
    _ROMAN_ONLY = re.compile(r"^[ivx]+$", re.ASCII)
    for bad, good in OCR_ALIASES.items():
        if name.endswith(bad):
            corrected_suffix = good.strip()
            if _ROMAN_ONLY.match(corrected_suffix):
                return name[: -len(bad)] + good
    return name
```

---

### OCR-02: Weapon swap UI text contaminates item name detection
**File:** `src/autoscrapper/ocr/inventory_vision.py`  
**Plan ref:** T013  
**Function:** `_extract_title_from_data`  
**Issue:** Weapon infoboxes contain a "Swap with Primary Slot" UI line near the top. OCR picks this up as the item name instead of the weapon name.  
**Fix:** Add `_EXCLUDED_UI_KEYWORDS = frozenset(["swap with", "swap"])`. Skip lines matching these keywords on first pass. On second pass (`_retry_with_larger=True`), widen `top_fraction` to `0.35`.

---

## Priority 2 — Data Pipeline

### DATA-01: Remove Supabase dependency from data_update.py
**File:** `src/autoscrapper/progress/data_update.py`  
**Plan ref:** T014  
**Issue:** Lines 738–749 call `_fetch_supabase_all()` for item components and recycle components. `SUPABASE_URL` (line 26) and `SUPABASE_ANON_KEY` (line 33) are still live. The MetaForge `/items?includeComponents=true` API is the intended replacement.  
**Fix:** Use `?includeComponents=true` on the MetaForge `/items` API. Extract components inline from the response via `_extract_component_dict()`. Remove `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `_fetch_supabase_all`, `_build_component_map`, and the two call sites at lines 738–749.

**Security note:** Remove the hardcoded Supabase endpoint URL regardless of whether the Supabase key is public/anon.

---

## Priority 3 — UX / Configuration

### UX-01: Change default stop key from Escape to F9
**File:** `src/autoscrapper/interaction/keybinds.py`  
**Plan ref:** T015  
**Issue:** `DEFAULT_STOP_KEY = "escape"` (line 5) conflicts with in-game Escape usage (opens game menu). F9 is unused by Arc Raiders.  
**Fix:**
```python
DEFAULT_STOP_KEY = "f9"
# Add to _CANONICAL_DISPLAY:
"f9": "F9",
```

---

## Priority 4 — Type Safety

### TYPE-01: ScanSettingsScreen missing ABC inheritance
**File:** `src/autoscrapper/tui/settings.py:92`  
**Plan ref:** T004  
**Issue:** `_compose_form` and `_load_into_fields` carry `@abstractmethod` but `ScanSettingsScreen` does not list `ABC` in its base classes. Basedpyright cannot enforce the abstract contract; a caller could instantiate the class directly and get a confusing runtime error.  
**Fix:** Change the class declaration:
```python
from abc import ABC
class ScanSettingsScreen(AppScreen, ABC): ...
```

---

## Priority 5 — Testing

### TEST-01: Add test suite for src/autoscrapper/api/
**Directory:** `tests/api/`  
**Plan ref:** T017  
**Issue:** The `api/` package (client.py, models.py, datasource.py) created in T016 has zero test coverage. `tests/api/` does not exist; it was listed in T016's acceptance criteria but not delivered.  
**Fix:** Create `tests/api/__init__.py` and `tests/api/test_client.py` covering:
- `RateLimitState` enforcement
- `ArcTrackerClient` retry logic (mocked responses)
- Graceful fallback when `HAS_REQUESTS = False` or on HTTP errors
- `datasource.py` sync functions against mock API payloads

---

## Priority 6 — Features

### FEAT-01: Quest-keyed sell/recycle guard (safe-recycle mode)
**Files:** `src/autoscrapper/core/item_actions.py`, `src/autoscrapper/progress/`  
**Plan ref:** T018  
**Description:** Items needed for active (incomplete) quests can be accidentally sold or recycled if the user hasn't set an explicit KEEP override. The progress data already tracks quest requirements and completion status.  
**Approach:**
- Add `quest_guard_enabled` setting (default `True`) in `config.py`.
- In `resolve_action()`, before returning SELL or RECYCLE, check active quest
  requirements; override to KEEP with reason `"quest_guard"` if a match is found.
- TUI scan report annotates guarded items.

### FEAT-02: OCR failure corpus calibration
**Files:** `scripts/replay_ocr_failure_corpus.py`, `src/autoscrapper/ocr/inventory_vision.py:47`  
**Plan ref:** T001 → T002  
**Description:** `DEFAULT_ITEM_NAME_MATCH_THRESHOLD = 75` is hand-picked. Replay tooling exists (`scripts/replay_ocr_failure_corpus.py`, `artifacts/ocr/skip_unlisted/samples.jsonl`) but the calibration loop has not been run against a live corpus. Needs real `SKIP_UNLISTED` captures to validate or adjust the constant.  
**Approach:** Accumulate samples via `capture_skip_unlisted_sample()`, run replay harness across candidate thresholds, document chosen value with corpus commit hash.

---

## Completed (removed from active backlog)

| Item     | Description                                       | Done       |
|----------|---------------------------------------------------|------------|
| BUG-01   | Stale infobox rect fix (`scan_loop.py`)           | 2026-04-14 |
| BUG-02   | Dead code removal (`inventory_vision.py`)         | 2026-04-14 |
| OCR-03   | Permissive `clean_ocr_text` regex                 | 2026-04-14 |
| DATA-02  | Hybrid wiki+MetaForge updater (`data_update.py`)  | 2026-04-14 |
| UX-02    | LiveWindow Protocol for `isAlive`                 | 2026-04-14 |
| UX-03    | `on_screen_resume` signature fix                  | 2026-04-14 |
| CI-01    | `pytest` in dev dependency group (`pyproject.toml`)| 2026-04-14 |
| FEAT-API | arctracker.io API integration (`src/api/`)        | 2026-04-14 |
