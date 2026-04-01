# Fix Plan: Item Name Detection Failures

**Date:** 2026-04-01  
**Branch:** main  

---

## Root Cause Analysis

Item name detection fails via three compounding failure modes:

### 1. No Fuzzy Matching (Highest Impact)
**Files:** `core/item_actions.py:137-152`, `TODO.md:12`

Matching is a raw dictionary lookup after `normalize_item_name()` (strip + lowercase). A single OCR character error — one misread letter, an extra space, a split word — produces `SKIP_UNLISTED`. The TODO already calls for `rapidfuzz`, but it hasn't been implemented.

Examples of OCR outputs that would silently fail:
- `"ARC-Powercell"` (hyphen instead of space) → no match for `"arc powercell"`
- `"Arc Power cell"` (word split by Tesseract) → no match for `"arc powercell"`
- `"Anqled Grip II Blueprint"` (q/g OCR confusion) → no match

### 2. Wrong Tesseract PSM Mode
**Files:** `ocr/tesseract.py:82`

`PSM.SINGLE_BLOCK` tells Tesseract the ROI is a **multi-line paragraph block**. Item names are a single line of text in a narrow strip (18% of infobox height). The correct mode is `PSM.SINGLE_LINE`, which avoids Tesseract wasting time on layout analysis and reduces hallucinated word breaks.

### 3. No Image Upscaling Before OCR
**Files:** `ocr/inventory_vision.py:593-596`

Preprocessing is only grayscale + OTSU binary threshold. The title ROI is a small pixel area (≈18% of a ~200px-tall infobox = ~36px height). Tesseract performs significantly better on text that is at least 30-40px tall per character. Without 2–4× upscaling before the OCR call, small or compressed UI text produces garbled output.

### 4. Fragile Infobox Detection (Secondary)
**Files:** `ocr/inventory_vision.py:295-466`

Detection relies on a hardcoded BGR target color `(236, 246, 253)` with tolerance 5–30. This fails with non-standard monitor gamma, HDR, or custom in-game color filters. If `find_infobox_with_debug()` returns `failure_reason != None`, the scan silently produces `UNREADABLE_NO_INFOBOX` instead of retrying with relaxed parameters.

---

## Fix Plan

### Phase 1 — Quick Wins (High impact, no architecture change)

#### 1.1 Switch PSM to SINGLE_LINE
**File:** `src/autoscrapper/ocr/tesseract.py:82`  
Change `psm=PSM.SINGLE_BLOCK` → `psm=PSM.SINGLE_LINE`.

```python
# Before
api = PyTessBaseAPI(path=str(candidate), lang="eng", psm=PSM.SINGLE_BLOCK)
# After
api = PyTessBaseAPI(path=str(candidate), lang="eng", psm=PSM.SINGLE_LINE)
```

Note: `ocr_infobox()` also calls `image_to_data()` which uses the same API instance. Verify this doesn't break button text extraction — if needed, create a second API instance with `SINGLE_BLOCK` for full infobox scanning and use `SINGLE_LINE` only for the title ROI call.

#### 1.2 Upscale Title ROI Before OCR
**File:** `src/autoscrapper/ocr/inventory_vision.py` — inside `preprocess_for_ocr()` or at the `ocr_item_name()` call site

Add 2× upscaling with `cv2.INTER_CUBIC` before thresholding:

```python
def preprocess_for_ocr(roi_bgr: np.ndarray) -> np.ndarray:
    scale = 2
    roi_bgr = cv2.resize(roi_bgr, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary
```

Test at 2× first; 3× may help for 1080p users but increases CPU time.

#### 1.3 Add Tesseract Character Whitelist
**File:** `src/autoscrapper/ocr/tesseract.py` — in `_create_api()`

Constrain Tesseract to characters that can appear in item names:

```python
api.SetVariable("tessedit_char_whitelist", "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 '-")
```

This eliminates false positives from Tesseract reading `|` as `I`, `0` as `O`, etc.

---

### Phase 2 — Fuzzy Matching (Resolves residual OCR noise)

#### 2.1 Add rapidfuzz Dependency
**File:** `pyproject.toml`

```toml
[project]
dependencies = [
    ...
    "rapidfuzz>=3.0",
]
```

#### 2.2 Implement `match_item_name()`
**File:** `src/autoscrapper/core/item_actions.py`

Add after the existing exact-match in `choose_decision()`:

```python
from rapidfuzz import process, fuzz

FUZZY_THRESHOLD = 85  # WRatio score, tunable

def match_item_name(raw: str, actions: ActionMap) -> Optional[str]:
    """Return best-matching key from actions, or None if below threshold."""
    normalized = normalize_item_name(raw)
    if not normalized:
        return None
    result = process.extractOne(normalized, actions.keys(), scorer=fuzz.WRatio)
    if result and result[1] >= FUZZY_THRESHOLD:
        return result[0]
    return None
```

Modify `choose_decision()` to fall through to fuzzy if exact match misses:

```python
def choose_decision(item_name: str, actions: ActionMap):
    normalized = normalize_item_name(item_name)
    if not normalized:
        return None, None
    decision_list = actions.get(normalized)         # exact match first
    if decision_list is None:
        matched_key = match_item_name(normalized, actions)  # fuzzy fallback
        if matched_key:
            decision_list = actions.get(matched_key)
    if decision_list is None:
        return None, None
    ...
```

**Threshold guidance:** Start at 85. Log matched pairs at first; review fuzzy matches that score 85–92 to confirm they're correct before trusting them silently.

#### 2.3 Log Fuzzy Match Decisions
When a fuzzy match is used, log `(raw_ocr → matched_key, score)` so the user can review edge cases. Add to `ItemActionResult` or the scan report's per-item notes field.

---

### Phase 3 — Infobox Detection Robustness

#### 3.1 Relax Color Tolerance on Retry
**File:** `src/autoscrapper/ocr/inventory_vision.py:295-466`

After a failed infobox detection, retry with `tolerance_max=50` (vs current 30) before returning `UNREADABLE_NO_INFOBOX`. This handles monitors with shifted gamma or saturation.

#### 3.2 Add OCR Debug Output for SKIP_UNLISTED
**File:** `src/autoscrapper/scanner/scan_loop.py` — in `_process_cell()`

When outcome is `SKIP_UNLISTED`, log the raw OCR text alongside the result. Currently this information is discarded, making it impossible to diagnose real-world failure rates. Save to a debug log file or include in the scan report.

---

## Implementation Order

| # | Change | File | Effort | Impact |
|---|--------|------|--------|--------|
| 1 | PSM → SINGLE_LINE | `ocr/tesseract.py:82` | 1 line | High |
| 2 | 2× upscale in preprocess | `ocr/inventory_vision.py:593` | 2 lines | High |
| 3 | Tesseract char whitelist | `ocr/tesseract.py` | 2 lines | Medium |
| 4 | Add rapidfuzz dep | `pyproject.toml` | 1 line | — |
| 5 | `match_item_name()` + fallback | `core/item_actions.py` | ~25 lines | High |
| 6 | Log fuzzy matches | `scanner/scan_loop.py` | ~5 lines | Medium |
| 7 | Retry infobox with wider tolerance | `ocr/inventory_vision.py` | ~10 lines | Medium |
| 8 | Log SKIP_UNLISTED raw OCR | `scanner/scan_loop.py` | ~5 lines | Medium |

Start with 1→2→3 (no new dependencies, minimal risk), then 4→5→6, then 7→8.

---

## Verification

- Enable `--dry-run` and scan a full inventory page; compare SKIP_UNLISTED count before and after.
- Check `ocr_debug/` directory (already present in repo root) — it likely contains captured frames useful for offline testing.
- For fuzzy threshold tuning: collect SKIP_UNLISTED raw OCR texts from a few runs, run them through `rapidfuzz` offline against the known item name list, and pick the lowest threshold that produces zero false positives.

---

## Additional Improvements

### Dependency Changes

| Dependency | Action | Reason |
|---|---|---|
| `opencv-python` | Replace with `opencv-python-headless` | No `cv2.imshow`/GUI used anywhere; saves ~100MB, removes Qt/GTK deps |
| `rapidfuzz>=3.0` | **Add** | Planned in TODO.md; needed for fuzzy matching (Phase 2 above) |
| `tessdata.fast-eng` | Keep; benchmark `tessdata.best-eng` | Best-eng (~10MB vs 4MB) may improve accuracy for unusual item name abbreviations |

All other deps (`tesserocr`, `mss`, `pydirectinput-rgx`, `pywinctl`, `Pillow`) are correctly chosen and should stay. Pillow is a hard requirement — `tesserocr`'s `SetImage()` requires a `PIL.Image`, not a numpy array.

---

### Error Handling (High Priority)

The codebase has a pattern of bare `except Exception: pass/continue` that silently swallows failures. These make bugs nearly impossible to diagnose:

| Location | Issue | Fix |
|---|---|---|
| `interaction/ui_windows.py:107` | `except Exception: title = ""` — swallows window API errors | Log exception before fallback |
| `interaction/ui_windows.py:260` | `except Exception: pass` on MSS `close()` | Log exception; resource leak possible |
| `ocr/tesseract.py:45` | `except Exception: pass` on init candidates | Log which path failed and why |
| `ocr/inventory_vision.py:671` | `except Exception: continue` in `_group_score()` | Log; drops confidence values silently |
| `ocr/inventory_vision.py:719` | `except Exception:` in OCR string extraction | Log with item context (slot index/coords) |
| `ocr/inventory_vision.py:747` | Broad `except Exception` treats all OCR failures identically | Differentiate timeout vs API failure vs OOM |
| `config.py:87-88` | Catches `OSError` and `JSONDecodeError` identically | Distinguish "file missing" vs "corrupted JSON" |
| `scanner/engine.py:120` | `except Exception: return None` — silent Rich display failure | Log so user knows why progress bar is absent |

### Config Validation

| Location | Issue | Fix |
|---|---|---|
| `config.py:19-26` | No upper bounds on delay fields — user can set `infobox_retry_interval_ms=1000000` | Add max bounds (e.g. delays ≤ 5000ms, retries ≤ 10) |
| `config.py:11` (`CONFIG_VERSION = 5`) | Version tracked but never checked on load | Implement `_migrate_vN_to_vN+1()` functions; warn on schema mismatch |
| `config.py:53-66` | `_coerce_positive_int()` silently returns `None` on invalid input | Log "ignoring invalid X value, using default Y" |

### Code Quality

| Location | Issue | Fix |
|---|---|---|
| `scanner/actions.py:23-27` | `INPUT_ACTION_DELAY` etc. duplicate `ScanSettings` defaults | Remove hardcoded copies; derive from `ScanSettings()` |
| `ocr/inventory_vision.py:608-625` | Two identical `except Exception` blocks for debug image save | Unify into `_save_debug_image_safe()` helper |
| `interaction/ui_windows.py:100-115` | Returns `None` silently if window not found after all fallbacks | Raise `RuntimeError("game window not found")` instead |
