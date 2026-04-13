# TODO — arc-raiders-autoscrapper fork improvements

**Generated:** 2026-04-13  
**Source:** diff between local (`zappybiby/ArcRaiders-AutoScrapper` base + session patches) and `Ven0m0/arc-raiders-autoscrapper` fork  
**Reference issues:** Ven0m0/arc-raiders-autoscrapper#41 (TODO tracker), #22 (Renovate dashboard)

---

## Priority 1 — Bug Fixes (port to fork immediately)

### BUG-01: Stale infobox rect causes wrong OCR crops at session end
**File:** `src/autoscrapper/scanner/scan_loop.py`  
**Function:** `_ScanRunner._ocr_infobox_with_retries` (retry loop, `ocr_attempt > 0`)  
**Symptom:** OCR retry passes reused the previously-detected infobox rect without re-detecting. When the context menu closed between attempts, the scanner cropped the "TAB | CLOSE" button bar at screen bottom, producing empty or garbage item names.  
**Fix:** On retry, re-capture the full window and call `find_infobox()` to get a fresh rect. Break early if detection returns `None` (menu closed).  
**Evidence:** `ocr_debug/20260413_062406_*_infobox_processed.png` crops contain "TAB CLOSE" text.

```python
# In the ocr_attempt > 0 branch, replace stale capture_region(old_rect) with:
window_bgr = capture_region((win_left, win_top, win_width, win_height))
new_rect = find_infobox(window_bgr)
if new_rect is None:
    break  # infobox closed; abort retry
x, y, w, h = new_rect
infobox_bgr = window_bgr[y : y + h, x : x + w]
```

---

### BUG-02: Dead code block in `_extract_title_from_data`
**File:** `src/autoscrapper/ocr/inventory_vision.py`  
**Lines (upstream):** 720–740  
**Issue:** Duplicate function body (including a `_group_score` re-definition) after a `return` statement — unreachable and misleading.  
**Fix:** Delete lines 720–740 entirely.

---

## Priority 2 — OCR Quality Improvements

### OCR-01: Roman numeral tier suffix correction
**File:** `src/autoscrapper/core/item_actions.py`  
**Issue:** Tesseract misreads Roman numeral suffixes on ALL-CAPS weapon names: `IV→1V`, `III→111`, `II→11`, `I→1`. This causes rule lookups to fail for tiered weapons.  
**Fix:** Add `OCR_ALIASES` dict and `_fix_roman_ocr_suffix()` function called from `normalize_item_name()`.

```python
OCR_ALIASES: Dict[str, str] = {
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

def normalize_item_name(name: str) -> str:
    normalized = name.strip().lower()
    return _fix_roman_ocr_suffix(normalized)
```

---

### OCR-02: Weapon swap UI text contaminates item name detection
**File:** `src/autoscrapper/ocr/inventory_vision.py`  
**Function:** `_extract_title_from_data`  
**Issue:** Weapon infoboxes contain a "Swap with Primary Slot" UI line near the top. OCR picks this up as the item name instead of the weapon name.  
**Fix:** Add `_EXCLUDED_UI_KEYWORDS = frozenset(["swap with", "swap"])`. Skip lines matching these keywords on first pass. On second pass (`_retry_with_larger=True`), widen `top_fraction` to `0.35` to capture the actual name below the UI element.

---

### OCR-03: `clean_ocr_text` too restrictive — drops valid punctuation
**File:** `src/autoscrapper/core/item_actions.py`  
**Upstream regex:** `[^-A-Za-z0-9 '()\\]+`  
**Fork regex:** `[^-A-Za-z0-9 '(),.!?:&+]+`  
**Issue:** The upstream regex strips `.`, `,`, `!`, `?`, `:`, `&`, `+` which can appear in real item names.  
**Fix:** Use the fork's more permissive character class.

---

## Priority 3 — Data Pipeline Improvements

### DATA-01: Remove Supabase dependency from data_update.py
**File:** `src/autoscrapper/progress/data_update.py`  
**Issue:** Upstream fetches item components and recycle components from a Supabase endpoint using a hardcoded anon JWT. This creates a dependency on an external service that may change.  
**Fix:** Use `?includeComponents=true` on the MetaForge `/items` API instead. Extract components inline from the response using `_extract_component_dict()`. Remove all Supabase code (`SUPABASE_URL`, `SUPABASE_ANON_KEY`, `_fetch_supabase_all`, `_build_component_map`).

**Note:** The hardcoded Supabase JWT in the upstream repo is a credential that should never be committed — remove it as a security improvement even if the endpoint is public/anon.

---

### DATA-02: Refresh data snapshot
**Files:** `src/autoscrapper/progress/data/`  
**Current upstream snapshot:** stale  
**Current local snapshot:** 547 items, 94 quests — `lastUpdated: 2026-04-13T06:31:59Z`  
**Action:** Run `scripts/update_snapshot_and_defaults.py` and commit the updated JSON files + regenerated `items_rules.default.json` (5681 lines).

---

## Priority 4 — UX / Configuration

### UX-01: Change default stop key from Escape to F9
**File:** `src/autoscrapper/interaction/keybinds.py`  
**Issue:** `DEFAULT_STOP_KEY = "escape"` conflicts with in-game Escape usage (opens game menu). F9 is unused by Arc Raiders.  
**Fix:**
```python
DEFAULT_STOP_KEY = "f9"
# Add to _CANONICAL_DISPLAY:
"f9": "F9",
```

---

## Priority 5 — Code Quality (fork already has some of these)

### QUAL-01: Switch JSON parser to `orjson`
**File:** `src/autoscrapper/core/item_actions.py` (and potentially others)  
**Status:** ✅ Already done in Ven0m0 fork  
**Note:** `orjson` is significantly faster for large rule files (5681 lines). Ensure `orjson` is in `pyproject.toml` dependencies.

### QUAL-02: Use Python 3.12+ `type` alias syntax
**File:** `src/autoscrapper/core/item_actions.py`  
**Status:** ✅ Already done in Ven0m0 fork  
```python
type Decision = Literal["KEEP", "RECYCLE", "SELL"]
type DecisionList = list[Decision]
type ActionMap = dict[str, DecisionList]
```

### QUAL-03: `@dataclass(slots=True)` for `ItemActionResult`
**File:** `src/autoscrapper/core/item_actions.py`  
**Status:** ✅ Already done in Ven0m0 fork  
Reduces memory overhead; each scan creates many `ItemActionResult` instances.

### QUAL-04: Split `load_item_actions` error handling into two `except` clauses
**File:** `src/autoscrapper/core/item_actions.py`  
**Status:** ✅ Already done in Ven0m0 fork  
Separate `FileNotFoundError` from `JSONDecodeError` for clearer error messages.

### QUAL-05: Expand `ACTION_ALIASES` with additional entries
**File:** `src/autoscrapper/core/item_actions.py`  
**Status:** ✅ Already done in Ven0m0 fork  
Fork adds `"sell_or_recycle": "SELL"`, `"sell or recycle": "SELL"`, `"crafting material": "KEEP"`.

### QUAL-06: `load_item_actions` — check `isinstance(name, str)` before `normalize_item_name`
**File:** `src/autoscrapper/core/item_actions.py`  
**Issue (upstream):** `normalize_item_name(name)` is called before the `isinstance(name, str)` guard, causing a potential AttributeError if `name` is `None`.  
**Fix:** Move `isinstance` check first.  
**Status:** ✅ Already fixed in both local diff and Ven0m0 fork.

---

## Priority 6 — Features (from issue #41 + related projects)

### FEAT-01: Integrate ARC Safe Recycle logic
**Reference:** https://github.com/thanhn062/ARC-Safe-Recycle  
**Issue:** Ven0m0/arc-raiders-autoscrapper#41  
**Description:** Study the safe-recycle approach from the referenced project. Consider adding a "safe recycle" mode that cross-references items against active quest requirements before recycling, to prevent accidental destruction of needed items.

### FEAT-02: Integrate Raider Lens overlay features
**Reference:** https://github.com/eli1776/raider-lens  
**Issue:** Ven0m0/arc-raiders-autoscrapper#41  
**Description:** Review raider-lens for overlay/display features that could complement the scanner's TUI output.

### FEAT-03: Add CHANGELOG.md
**Status:** ✅ Created locally (`CHANGELOG.md`)  
**Action:** Commit and push `CHANGELOG.md` to the fork. It covers 9 versions from Nov 2025 to Apr 2026 with the full upstream history.

---

## Priority 7 — CI / Dev Tooling (fork already ahead)

### CI-01: Add pre-commit hooks
**Status:** ✅ Already in Ven0m0 fork (`.pre-commit-config.yaml`)  
Fork has: `ruff`, `gitleaks` (secret scanning), `zizmor` (GitHub Actions security), `tombi` (TOML linter), `shellcheck`  
**Action:** Ensure local dev setup runs `pre-commit install`.

### CI-02: Add Renovate for automated dependency updates
**Status:** ✅ Already active in Ven0m0 fork (issue #22)  
Pending: Python `>=3.13.13` update (PR #156 closed/blocked — recreate if needed).

### CI-03: Add GitHub Copilot setup steps workflow
**Status:** ✅ Already in Ven0m0 fork (`.github/workflows/copilot-setup-steps.yml`)

### CI-04: Add `pytest` to dev dependencies
**File:** `pyproject.toml`  
**Issue:** `pytest` is listed in `pyproject.toml` but not installed in the default venv — `uv run python -m pytest` fails with "No module named pytest".  
**Fix:** Ensure `uv sync --extra dev` is documented in setup instructions, or add pytest to the base `[project.dependencies]`.

---

## Upstream sync checklist

When syncing from `zappybiby/ArcRaiders-AutoScrapper` to `Ven0m0/arc-raiders-autoscrapper`, apply in order:

- [ ] BUG-01: Stale infobox rect fix (`scan_loop.py`)
- [ ] BUG-02: Dead code removal (`inventory_vision.py`)
- [ ] OCR-01: Roman numeral alias correction (`item_actions.py`)
- [ ] OCR-02: Weapon swap UI keyword filter (`inventory_vision.py`)
- [ ] OCR-03: Permissive `clean_ocr_text` regex (already in fork — verify not regressed)
- [ ] DATA-01: Remove Supabase, use `includeComponents=true` (`data_update.py`)
- [ ] DATA-02: Commit fresh data snapshot + regenerated default rules
- [ ] UX-01: F9 as default stop key (`keybinds.py`)
- [ ] FEAT-03: Commit `CHANGELOG.md`
- [ ] CI-04: Fix `pytest` dev dependency setup
