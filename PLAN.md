---
title: Implementation Plan
status: active
updated: 2026-04-24
---

<!--
AGENTIC EXECUTION GUIDE:
- This file contains machine-readable XML tags (<execution-hints>, <dependencies>, <risks>)
- Read this entire file before planning any implementation
- Respect all <blocked-on> tags - do not start blocked tasks
- Tasks within the same <parallel-wave> can execute concurrently
- Always run validation commands after each task
- When in doubt, prefer smaller, verifiable changes
-->

## Workflow

1. Read `AGENTS.md` and `.github/instructions/python.instructions.md` first
2. Make minimal, targeted changes
3. Never hand-edit `src/autoscrapper/progress/data/` or `items_rules.default.json`
4. Regenerate data with `scripts/update_snapshot_and_defaults.py` when needed
5. Run validation before marking done:
   - `uv run ruff check src/ tests/ scripts/`
   - `uv run ty check src/`
   - `uv run basedpyright src/`
   - `uv run pytest`

## Delivery Waves

<execution-hints>
Waves are ordered by dependency and priority. Start from Wave 1 and proceed sequentially.
Within each wave, tasks marked <parallel> can execute concurrently. Tasks marked <sequential>
must wait for earlier tasks in the same wave to complete.
</execution-hints>

| Wave | Goal | Tasks |
|------|------|-------|
| 1 | Data pipeline & integrations | T014, T034, T003, T001, T002 |
| 2 | OCR accuracy improvements | T027, T012, T013, T028, T029, T030, T031, T032 |
| 3 | Code quality & architecture | T036, T037, T038 |
| 4 | Test coverage | T039, T040, T041 |
| 5 | Feature completion | T017, T019, T020, T022 |
| 6 | Performance & optimization | T042, T043, T044 |
| 7 | Research | T021 |

## Next Picks

<execution-hints>
These are the highest ROI tasks to pick up next. Prioritized by:
1. Unblocking other tasks (T014 blocks T003)
2. High value/effort ratio (T034, T027)
3. Risk reduction (T039 tests critical logic)
</execution-hints>

| Rank | Task | Description | Rationale |
|------|------|-------------|-----------|
| 1 | T034 | Arc-Lens scraping integration - high-value data pipeline | High value, unblocks richer data |
| 2 | T014 | Security fix removing Supabase dependency | Unblocks T003, removes security risk |
| 3 | T027 | Feed item names to Tesseract as user_words | High OCR accuracy impact |
| 4 | T039 | Add tests for decision_engine.py - core business logic | Critical untested business logic |
| 5 | T012 | Roman numeral OCR alias correction | Quick win for weapon recognition |

---

## Tasks

<!-- TEMPLATE:
### T### - Task Title

<execution-hints>
<blocked-on></blocked-on>
<parallel-with></parallel-with>
<affects-critical-path>true|false</affects-critical-path>
<requires-live-game>false|true</requires-live-game>
<validation-required>
- ruff
- basedpyright
- ty
- pytest
</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | high/medium/low |
| Size | XS/S/M/L/XL |
| Status | ready/blocked/complete |

**Files:** `path/to/file.py`, `path/to/file2.py`

**Why:** One-line rationale

**Done when:**
- [ ] Checklist item

<risks>
- Risk description and mitigation
</risks>
-->

<parallel-wave id="1" name="Data Pipeline">

### T001 - Calibrate OCR threshold from failure corpus

<execution-hints>
<blocked-on></blocked-on>
<parallel-with>T014, T034</parallel-with>
<affects-critical-path>false</affects-critical-path>
<requires-live-game>false</requires-live-game>
<validation-required>ruff, basedpyright, pytest</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | medium |
| Size | M |
| Status | ready |

**Files:** `src/autoscrapper/ocr/failure_corpus.py`, `scripts/replay_ocr_failure_corpus.py`

**Why:** Replace hand-picked threshold with corpus-backed evidence

**Done when:**
- [ ] Corpus samples capture fields needed for accuracy scoring
- [ ] Replay script compares thresholds and reports accuracy
- [ ] Default changes only when replay shows no regression

<risks>
- OCR threshold changes can cause widespread item misclassification
- Mitigation: Always run corpus replay before changing default threshold
- See skill: `threshold-corpus-replay`
</risks>

---

### T002 - Benchmark tessdata.best-eng vs tessdata.fast-eng

<execution-hints>
<blocked-on>T001</blocked-on>
<parallel-with></parallel-with>
<affects-critical-path>false</affects-critical-path>
<requires-live-game>false</requires-live-game>
<validation-required>pytest</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | low |
| Size | S |
| Status | blocked on T001 |

**Files:** `src/autoscrapper/ocr/tesseract.py`, `scripts/benchmark_tessdata_models.py`

**Why:** Only worth doing after threshold corpus is stable

**Done when:**
- [ ] Benchmark uses same corpus from T001
- [ ] Compare accuracy and latency for both models
- [ ] Change models only if latency trade-off is acceptable

---

### T003 - Hybrid MetaForge plus wiki pipeline

<execution-hints>
<blocked-on>T014</blocked-on>
<parallel-with></parallel-with>
<affects-critical-path>false</affects-critical-path>
<requires-live-game>false</requires-live-game>
<validation-required>ruff, basedpyright, pytest</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | medium |
| Size | M |
| Status | blocked on T014 |

**Why:** Extend updater after unsupported Supabase dependency is removed

**Done when:**
- [ ] MetaForge primary and RaidTheory fallback remain intact
- [ ] Wiki enrichment fills gaps for workshop, expedition, project-use data
- [ ] Dry-run output reports coverage without writing tracked files
- [ ] Metadata records origin of enriched fields

<dependencies>
T014 must be complete before starting - this task builds on the post-Supabase
architecture.
</dependencies>

---

### T014 - Remove Supabase dependency

<execution-hints>
<blocked-on></blocked-on>
<parallel-with>T001, T034</parallel-with>
<affects-critical-path>true</affects-critical-path>
<requires-live-game>false</requires-live-game>
<validation-required>ruff, basedpyright, ty, pytest</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | high |
| Size | M |
| Status | ready |

**Files:** `src/autoscrapper/progress/data_update.py`, `scripts/update_snapshot_and_defaults.py`

**Why:** Remove committed credential, keep updater on supported sources

**Done when:**
- [ ] MetaForge item fetching uses `includeComponents` instead of Supabase
- [ ] All Supabase constants and helpers deleted
- [ ] Snapshot updater runs without any Supabase call path

<risks>
- Breaking data update pipeline
- Mitigation: Test with --dry-run flag first, verify all data sources still work
- Ensure RaidTheory fallback is functional before removing Supabase
</risks>

---

### T034 - Integrate Arc-Lens data scraping pipeline

<execution-hints>
<blocked-on></blocked-on>
<parallel-with>T001, T014</parallel-with>
<affects-critical-path>false</affects-critical-path>
<requires-live-game>false</requires-live-game>
<validation-required>ruff, basedpyright, pytest</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | high |
| Size | L |
| Status | ready |

**Files:** New `scripts/vendor/arc-lens/`, `scripts/update_snapshot_and_defaults.py`

**Why:** Integrate Arc-Lens community scrapers for fresh MetaForge/raidtheory data and edge-case sources (trophies, wiki content)

**References:**
- https://github.com/eetusa/arc-lens/blob/master/scripts/metaforge-scraper.js
- https://github.com/eetusa/arc-lens/blob/master/scripts/quest-scraper.js
- https://github.com/eetusa/arc-lens/blob/master/scripts/wiki-scraper.js

**Done when:**
- [ ] Vendor arc-lens scrapers under `scripts/vendor/arc-lens/` with attribution
- [ ] Port JS scrapers to Python using `requests` + `BeautifulSoup`
- [ ] Wire into `update_snapshot_and_defaults.py` as optional data source
- [ ] Add `--source arc-lens` flag to run only Arc-Lens pipeline
- [ ] Document what each scraper contributes
- [ ] Pipeline fails gracefully if Arc-Lens data unavailable

<risks>
- External dependency on Arc-Lens repository structure
- Mitigation: Vendor the scripts, don't submodule; gracefully degrade if unavailable
</risks>

</parallel-wave>

<parallel-wave id="2" name="OCR Accuracy">

### T012 - Roman numeral OCR alias correction

<execution-hints>
<blocked-on></blocked-on>
<parallel-with>T013, T027, T028, T029, T030, T032</parallel-with>
<affects-critical-path>false</affects-critical-path>
<requires-live-game>false</requires-live-game>
<validation-required>ruff, basedpyright, pytest</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | medium |
| Size | S |
| Status | ready |

**File:** `src/autoscrapper/core/item_actions.py`

**Why:** Close OCR-to-rule mismatch for tiered weapon names

**Done when:**
- [ ] Normalization corrects common OCR suffix errors (1V, 111)
- [ ] Canonical matching uses existing fuzzy threshold
- [ ] Tests cover corrected and unchanged names

<implementation-hints>
Related code already exists in inventory_vision.py as `_ROMAN_NUMERAL_FIXES`.
Consider extracting to shared utility if both OCR and rule matching need it.
</implementation-hints>

---

### T013 - Filter weapon swap UI text from item-name detection

<execution-hints>
<blocked-on></blocked-on>
<parallel-with>T012, T027, T028, T029, T030, T032</parallel-with>
<affects-critical-path>false</affects-critical-path>
<requires-live-game>false</requires-live-game>
<validation-required>ruff, basedpyright, pytest</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | medium |
| Size | S |
| Status | ready |

**File:** `src/autoscrapper/ocr/inventory_vision.py`

**Why:** Prevent overlay text from being mistaken for item title

**Done when:**
- [ ] Known swap-related UI strings ignored on first title pass
- [ ] Retry path expands to reach real item name below UI line
- [ ] Change does not weaken unrelated title extraction

<risks>
- May filter legitimate item names that happen to match UI strings
- Mitigation: Only filter in the initial pass, retry without filter if no match found
</risks>

---

### T027 - Feed item names to Tesseract as user_words

<execution-hints>
<blocked-on></blocked-on>
<parallel-with>T012, T013, T028, T029, T030, T032</parallel-with>
<affects-critical-path>true</affects-critical-path>
<requires-live-game>false</requires-live-game>
<validation-required>ruff, basedpyright, ty, pytest, ocr-corpus-replay</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | high |
| Size | M |
| Status | ready |

**Files:** `src/autoscrapper/ocr/tesseract.py`, `src/autoscrapper/items/rules_store.py`

**Why:** Tesseract LSTM has no domain prior; user_words recommended for non-prose vocabulary

**Done when:**
- [ ] `initialize_ocr` writes item-name tokens to temp file, loads via `user_words_suffix`
- [ ] `load_system_dawg` set to 0 to remove English-dictionary noise
- [ ] Re-init after rules_store custom-overrides change, with integration test
- [ ] Corpus replay shows no regressions

<risks>
- Tesseract re-initialization is expensive; avoid doing it mid-scan
- Mitigation: Pre-load all item names at startup, re-init only when custom rules change
- Thread-safety: ensure API initialization happens on main thread
</risks>

<implementation-hints>
Use `tesserocr` API variables:
- `user_words_suffix` for the word list file path
- `load_system_dawg` set to "0" to disable system dictionary
See: https://github.com/tesseract-ocr/tesseract/blob/main/doc/tesseract.1.asc
</implementation-hints>

---

### T028 - Pad all four sides of OCR title-strip ROIs

<execution-hints>
<blocked-on></blocked-on>
<parallel-with>T012, T013, T027, T029, T030, T032</parallel-with>
<affects-critical-path>false</affects-critical-path>
<requires-live-game>false</requires-live-game>
<validation-required>ruff, basedpyright, pytest, ocr-corpus-replay</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | medium |
| Size | S |
| Status | ready |

**File:** `src/autoscrapper/ocr/inventory_vision.py`

**Why:** Tightly-cropped text reduces accuracy per tessdoc

**Done when:**
- [ ] Top, bottom, right edges receive symmetric _TITLE_PAD pixels of median background
- [ ] Retry path keeps existing extra expansion behaviour
- [ ] Corpus replay shows no regressions

---

### T029 - Sauvola binarisation for uneven illumination

<execution-hints>
<blocked-on></blocked-on>
<parallel-with>T012, T013, T027, T028, T030, T032</parallel-with>
<affects-critical-path>false</affects-critical-path>
<requires-live-game>false</requires-live-game>
<validation-required>ruff, basedpyright, pytest, ocr-corpus-replay</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | medium |
| Size | M |
| Status | ready |

**File:** `src/autoscrapper/ocr/inventory_vision.py`

**Why:** Otsu fails on title-band glow and rarity gradients; Sauvola is locally adaptive

**Done when:**
- [ ] `preprocess_for_ocr_sauvola` implemented via numpy or Tesseract `thresholding_method=2`
- [ ] When Otsu yields no fuzzy match, Sauvola runs and higher-WRatio result wins
- [ ] No new mandatory dependency added

<implementation-hints>
Sauvola can be implemented two ways:
1. OpenCV + numpy: `cv2.ximgproc.niBlackThreshold` with `binarizationMethod=cv2.ximgproc.BINARIZATION_SAUVOLA`
2. Tesseract config: `tessedit_thresholding_method=2` (Sauvola)

Option 2 is simpler but less controllable. Option 1 adds dependency on opencv-contrib.
</implementation-hints>

---

### T030 - Confidence-gated retry

<execution-hints>
<blocked-on></blocked-on>
<parallel-with>T012, T013, T027, T028, T029, T032</parallel-with>
<affects-critical-path>false</affects-critical-path>
<requires-live-game>false</requires-live-game>
<validation-required>ruff, basedpyright, pytest, ocr-corpus-replay</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | medium |
| Size | S |
| Status | ready |

**File:** `src/autoscrapper/ocr/inventory_vision.py`

**Why:** Current retry misses high-fuzzy/low-confidence cases producing wrong item names

**Done when:**
- [ ] Primary read uses `image_to_data`, computes mean per-character confidence
- [ ] Retries fire when mean_conf below 60 even if fuzzy match exists
- [ ] Highest-confidence result wins

---

### T031 - Glyph-aware fuzzy distance

<execution-hints>
<blocked-on>T001</blocked-on>
<parallel-with></parallel-with>
<affects-critical-path>false</affects-critical-path>
<requires-live-game>false</requires-live-game>
<validation-required>ruff, basedpyright, pytest, ocr-corpus-replay</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | medium |
| Size | S |
| Status | blocked on T001 |

**File:** `src/autoscrapper/ocr/inventory_vision.py`

**Why:** WRatio penalises O/0, I/1, 5/S equally, forcing loose threshold

**Done when:**
- [ ] `match_item_name_result` canonicalises 0-O, 1-I, 5-S, 8-B on query and choices
- [ ] Default threshold tightens ~5 points without losing recall
- [ ] OCR and rule-lookup thresholds remain shared

<dependencies>
Blocked on T001 because threshold changes require corpus-backed evidence.
Don't start until T001 corpus replay infrastructure is ready.
</dependencies>

---

### T032 - Set user_defined_dpi=300 on Tesseract API

<execution-hints>
<blocked-on></blocked-on>
<parallel-with>T012, T013, T027, T028, T029, T030</parallel-with>
<affects-critical-path>false</affects-critical-path>
<requires-live-game>false</requires-live-game>
<validation-required>ruff, basedpyright, pytest, ocr-corpus-replay</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | low |
| Size | XS |
| Status | ready |

**File:** `src/autoscrapper/ocr/tesseract.py`

**Why:** Numpy arrays carry no DPI header; explicit 300 DPI hint correct with 2x upscale

**Done when:**
- [ ] `initialize_ocr` sets `user_defined_dpi` to 300
- [ ] No corpus regression

<implementation-hints>
Set via Tesseract API variable: `user_defined_dpi` = "300"
This should be done during API initialization in `_create_api()` or `initialize_ocr()`
</implementation-hints>

</parallel-wave>

<parallel-wave id="3" name="Code Quality">

### T035 - Consolidate duplicated normalization functions

<execution-hints>
<blocked-on></blocked-on>
<parallel-with></parallel-with>
<affects-critical-path>false</affects-critical-path>
<requires-live-game>false</requires-live-game>
<validation-required>ruff, basedpyright, ty, pytest</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | high |
| Size | S |
| Status | complete |

**Files:** `src/autoscrapper/progress/progress_config.py`, `src/autoscrapper/progress/quest_inference.py`, `src/autoscrapper/progress/update_report.py`

**Why:** Same `_normalize_quest_name` function duplicated across 3 files; violates DRY principle

**Done when:**
- [x] Create shared normalization utility in `src/autoscrapper/utils/normalization.py`
- [x] All 3 files import from shared location
- [x] Tests verify identical behavior after consolidation
- [x] No performance regression

<implementation-notes>
COMPLETED: The function is now centralized in `src/autoscrapper/utils/normalization.py`
and imported by all three target files. All validation passes.
</implementation-notes>

---

### T036 - Refactor oversized modules

<execution-hints>
<blocked-on></blocked-on>
<parallel-with>T037, T038</parallel-with>
<affects-critical-path>true</affects-critical-path>
<requires-live-game>false</requires-live-game>
<validation-required>ruff, basedpyright, ty, pytest</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | medium |
| Size | L |
| Status | ready |

**Files:** `src/autoscrapper/ocr/inventory_vision.py` (1781 lines), `src/autoscrapper/progress/decision_engine.py` (434 lines)

**Why:** inventory_vision.py mixes infobox detection, OCR preprocessing, item matching, debug saving; decision_engine.py mixes quest/hideout/crafting logic

**Done when:**
- [ ] `inventory_vision.py` split into: preprocessing.py, detection.py, matching.py
- [ ] `decision_engine.py` split into: quest_logic.py, hideout_logic.py, crafting_logic.py
- [ ] All imports updated, tests pass
- [ ] No functional changes

<risks>
- High regression risk due to module size and complexity
- Mitigation: Make pure moves first (no logic changes), verify with tests at each step
- Consider doing one module at a time, not both simultaneously
</risks>

---

### T037 - Replace broad exception handling

<execution-hints>
<blocked-on></blocked-on>
<parallel-with>T036, T038</parallel-with>
<affects-critical-path>false</affects-critical-path>
<requires-live-game>false</requires-live-game>
<validation-required>ruff, basedpyright, pytest</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | medium |
| Size | M |
| Status | ready |

**Files:** `src/autoscrapper/api/client.py`, `src/autoscrapper/progress/data_update.py`

**Why:** Heavy use of `except Exception` masks real bugs and makes debugging difficult

**Done when:**
- [ ] API client raises specific exceptions (RateLimitError, AuthError, NotFoundError)
- [ ] Data update catches specific exceptions per operation
- [ ] Each exception type includes contextual error message
- [ ] Tests verify proper exception handling

<implementation-hints>
Create custom exception hierarchy in `src/autoscrapper/api/exceptions.py`:
- `ArcTrackerError(Exception)` - base
  - `RateLimitError(ArcTrackerError)`
  - `AuthError(ArcTrackerError)`
  - `NotFoundError(ArcTrackerError)`
  - `DownloadError(ArcTrackerError)` (already exists)
</implementation-hints>

---

### T038 - Introduce async/await patterns

<execution-hints>
<blocked-on></blocked-on>
<parallel-with>T036, T037</parallel-with>
<affects-critical-path>true</affects-critical-path>
<requires-live-game>false</requires-live-game>
<validation-required>ruff, basedpyright, ty, pytest</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | medium |
| Size | L |
| Status | ready |

**Files:** `src/autoscrapper/scanner/scan_loop.py`, `src/autoscrapper/api/client.py`, `src/autoscrapper/interaction/`

**Why:** Blocking sleep operations and sequential cell scanning limit throughput

**Done when:**
- [ ] API client uses `aiohttp` or `httpx` for async requests
- [ ] Scanner supports concurrent cell processing (configurable parallelism)
- [ ] Rate limiting uses async-aware throttling
- [ ] Benchmark shows measurable throughput improvement

<risks>
- OCR and desktop input are inherently synchronous; don't force async where it adds no value
- Mitigation: Keep OCR on main thread, use async only for I/O (API calls, file writes)
- Thread-safety: Tesseract APIs must be initialized on main thread
</risks>

</parallel-wave>

<parallel-wave id="4" name="Test Coverage">

### T039 - Add tests for decision_engine.py

<execution-hints>
<blocked-on></blocked-on>
<parallel-with>T040, T041</parallel-with>
<affects-critical-path>false</affects-critical-path>
<requires-live-game>false</requires-live-game>
<validation-required>pytest</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | high |
| Size | M |
| Status | ready |

**Files:** New `tests/progress/test_decision_engine.py`

**Why:** Core business logic completely untested (434 lines of decision-making)

**Done when:**
- [ ] Unit tests for all decision paths (KEEP, SELL, RECYCLE)
- [ ] Tests for quest requirement conflicts
- [ ] Tests for hideout upgrade priority logic
- [ ] Tests for crafting value evaluation
- [ ] >80% coverage of decision_engine.py

---

### T040 - Add tests for inventory_grid.py

<execution-hints>
<blocked-on></blocked-on>
<parallel-with>T039, T041</parallel-with>
<affects-critical-path>false</affects-critical-path>
<requires-live-game>false</requires-live-game>
<validation-required>pytest</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | high |
| Size | M |
| Status | ready |

**Files:** New `tests/interaction/test_inventory_grid.py`

**Why:** Grid coordinate calculations are critical and currently untested

**Done when:**
- [ ] Tests for cell coordinate calculations
- [ ] Tests for grid detection edge cases
- [ ] Tests for row/column boundary detection
- [ ] Tests for different screen resolutions

---

### T041 - Add integration tests for OCR pipeline

<execution-hints>
<blocked-on></blocked-on>
<parallel-with>T039, T040</parallel-with>
<affects-critical-path>false</affects-critical-path>
<requires-live-game>false</requires-live-game>
<validation-required>pytest</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | medium |
| Size | L |
| Status | ready |

**Files:** New `tests/ocr/test_ocr_pipeline_integration.py`

**Why:** No end-to-end test from image input to item decision

**Done when:**
- [ ] Fixture with sample inventory images
- [ ] Test full flow: image -> OCR -> fuzzy match -> decision
- [ ] Test polarity detection, retry logic, confidence gating
- [ ] Mock Tesseract for deterministic tests

<implementation-hints>
Create test fixtures in `tests/fixtures/ocr/`:
- Sample infobox images (various rarities)
- Sample context menu images
- Expected OCR outputs for each

Mock Tesseract API to return predetermined strings for each fixture.
</implementation-hints>

</parallel-wave>

<parallel-wave id="5" name="Features">

### T017 - Make ScanSettingsScreen a real ABC

<execution-hints>
<blocked-on></blocked-on>
<parallel-with>T019, T020, T022</parallel-with>
<affects-critical-path>false</affects-critical-path>
<requires-live-game>false</requires-live-game>
<validation-required>ruff, basedpyright, ty, pytest</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | low |
| Size | S |
| Status | ready |

**File:** `src/autoscrapper/tui/settings.py`

**Why:** Turn silent design bug into enforced contract

**Done when:**
- [ ] Class inherits from `ABC`
- [ ] Abstract methods enforced at instantiation
- [ ] No new type-checking regressions

---

### T019 - Per-session decision log

<execution-hints>
<blocked-on></blocked-on>
<parallel-with>T017, T020, T022</parallel-with>
<affects-critical-path>false</affects-critical-path>
<requires-live-game>false</requires-live-game>
<validation-required>ruff, basedpyright, pytest</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | medium |
| Size | S |
| Status | ready |

**File:** `src/autoscrapper/scanner/`

**Why:** Create durable record without replacing OCR failure corpus

**Done when:**
- [ ] Session appends JSONL decision records when logging enabled
- [ ] Log includes timestamp, raw text, decision, location, score, source
- [ ] Feature is opt-in, does not slow normal scans

<implementation-hints>
Add to `src/autoscrapper/scanner/engine.py` or create `src/autoscrapper/scanner/decision_logger.py`
Log format (JSONL):
```json
{"timestamp": "2026-01-15T10:30:00Z", "page": 1, "cell": 5, "raw_text": "Assault Rifl", "decision": "KEEP", "score": 82, "source": "fuzzy_match"}
```
</implementation-hints>

---

### T020 - Safe recycle protection against quest requirements

<execution-hints>
<blocked-on></blocked-on>
<parallel-with>T017, T019, T022</parallel-with>
<affects-critical-path>false</affects-critical-path>
<requires-live-game>false</requires-live-game>
<validation-required>ruff, basedpyright, pytest</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | medium |
| Size | M |
| Status | ready |

**File:** `src/autoscrapper/progress/`

**Why:** Prevent recycling items that active quests still need

**Done when:**
- [ ] Recycle decisions cross-checked against active quest requirements
- [ ] Conflicts override decision to KEEP and record quest reason
- [ ] Feature degrades gracefully when progress data absent

---

### T022 - Pytest in documented install paths

<execution-hints>
<blocked-on></blocked-on>
<parallel-with>T017, T019, T020</parallel-with>
<affects-critical-path>false</affects-critical-path>
<requires-live-game>false</requires-live-game>
<validation-required>pytest</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | low |
| Size | S |
| Status | ready |

**Files:** `pyproject.toml`, `scripts/setup-linux.sh`, `scripts/setup-windows.ps1`

**Why:** Remove setup drift for contributors and CI environments

**Done when:**
- [ ] Docs point contributors to install path including pytest
- [ ] Fresh setup aligns with dependency groups in pyproject.toml

</parallel-wave>

<parallel-wave id="6" name="Performance">

### T042 - Implement rule caching

<execution-hints>
<blocked-on></blocked-on>
<parallel-with>T043, T044</parallel-with>
<affects-critical-path>false</affects-critical-path>
<requires-live-game>false</requires-live-game>
<validation-required>ruff, basedpyright, pytest</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | medium |
| Size | S |
| Status | ready |

**Files:** `src/autoscrapper/core/item_actions.py`, `src/autoscrapper/items/rules_store.py`

**Why:** Rules reloaded from disk on every call; significant overhead during scans

**Done when:**
- [ ] Rules cached in memory with TTL
- [ ] Cache invalidated on file modification
- [ ] Cache statistics available (hit rate, size)
- [ ] Benchmark shows scan speed improvement

---

### T043 - Optimize OCR image processing

<execution-hints>
<blocked-on></blocked-on>
<parallel-with>T042, T044</parallel-with>
<affects-critical-path>false</affects-critical-path>
<requires-live-game>false</requires-live-game>
<validation-required>ruff, basedpyright, pytest, ocr-corpus-replay</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | high |
| Size | M |
| Status | ready |

**Files:** `src/autoscrapper/ocr/inventory_vision.py`

**Why:** 2x upscaling every ROI and duplicate connectedComponents calls are expensive

**Done when:**
- [ ] Cache preprocessed images between infobox and context menu passes
- [ ] Remove duplicate connectedComponentsWithStats calls
- [ ] Consider lazy upscaling only when needed
- [ ] Benchmark shows <20% OCR latency reduction

---

### T044 - Add game data caching

<execution-hints>
<blocked-on></blocked-on>
<parallel-with>T042, T043</parallel-with>
<affects-critical-path>false</affects-critical-path>
<requires-live-game>false</requires-live-game>
<validation-required>ruff, basedpyright, pytest</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | low |
| Size | S |
| Status | ready |

**Files:** `src/autoscrapper/progress/data_loader.py`

**Why:** Game data re-parsed on every access; JSON files rarely change

**Done when:**
- [ ] Parsed data cached with file mtime invalidation
- [ ] Cache shared across scan sessions
- [ ] Memory usage monitored (no unbounded growth)

</parallel-wave>

<parallel-wave id="7" name="Research">

### T021 - Assess Raider Lens overlay ideas

<execution-hints>
<blocked-on></blocked-on>
<parallel-with></parallel-with>
<affects-critical-path>false</affects-critical-path>
<requires-live-game>false</requires-live-game>
<validation-required>none</validation-required>
</execution-hints>

| Attribute | Value |
|-----------|-------|
| Priority | low |
| Size | M |
| Status | research |

**File:** `src/autoscrapper/tui/`

**Why:** Optional exploratory work, do not start until higher-value tasks land

**Done when:**
- [ ] Written assessment identifies what can be reused safely
- [ ] Prototype stays isolated from OCR and scan performance risk

<execution-hints>
Do NOT start this task until all Wave 1-6 tasks are complete.
This is research-only and should not impact production code.
</execution-hints>

</parallel-wave>

---

## Analysis Findings

### Code Quality Issues

| Issue | Location | Impact |
|-------|----------|--------|
| Duplicated `_normalize_quest_name` | 4 files in `progress/` | Medium - violates DRY |
| Broad `except Exception` handling | `api/client.py`, `data_update.py` | Medium - masks bugs |
| 1781-line `inventory_vision.py` | OCR module | High - maintainability |
| 434-line `decision_engine.py` | Progress module | Medium - separation of concerns |

### Missing Test Coverage (Critical)

| Module | Lines | Risk |
|--------|-------|------|
| `progress/decision_engine.py` | 434 | Core business logic |
| `interaction/inventory_grid.py` | 360 | Coordinate calculations |
| `scanner/actions.py` | 217 | Action execution |
| `progress/recipe_utils.py` | 14 | Recipe utilities |

### Performance Opportunities

| Opportunity | Current State | Target |
|-------------|---------------|--------|
| OCR image caching | None | Share between passes |
| Rule loading | Disk read every call | In-memory cache |
| Cell scanning | Sequential | Parallel (configurable) |
| API requests | Blocking sync | Async with `httpx` |

### Architecture Improvements

| Improvement | Current | Proposed |
|-------------|---------|----------|
| OCR backend | Locked to Tesseract | Protocol-based |
| Input drivers | Conditional imports | Strategy pattern |
| Module size | 1781 lines | <500 lines each |
| Error handling | Broad exceptions | Specific types |

---

## Quick Reference

### Skills Available

<execution-hints>
Use these skills via the `skill` tool for common workflows:
</execution-hints>

| Skill | When to Use |
|-------|-------------|
| `verify` | Run full validation suite (lint + types + tests) |
| `ocr-corpus-replay` | Validate OCR changes against failure corpus |
| `threshold-corpus-replay` | Validate threshold changes specifically |
| `add-fixture` | Add OCR regression test from debug image |
| `calibrate-vision` | Recalibrate context menu crop constants |
| `dead-code-sweep` | Find and remove dead code |
| `config-bump` | Safely add/remove config fields |

### Validation Commands

```bash
# Quick check
uv run ruff check src/ tests/

# Full validation (run before marking any task done)
uv run ruff check src/ tests/ scripts/
uv run ty check src/
uv run basedpyright src/
uv run pytest
```

### Critical Files (High-Risk Changes)

<risks>
These files require extra caution. Always run dry-run scans after changes:
- `src/autoscrapper/ocr/inventory_vision.py` - OCR accuracy
- `src/autoscrapper/scanner/` - Scan engine
- `src/autoscrapper/core/item_actions.py` - Decision logic
- `src/autoscrapper/config.py` - Config persistence
</risks>
