---
title: Implementation Plan
status: active
updated: 2026-04-24
---

<!-- AGENT GUIDE: Read AGENTS.md first. Never hand-edit data/ or items_rules.default.json -->

## Workflow

1. Read `AGENTS.md` before starting
2. Make minimal, targeted changes
3. Never hand-edit `src/autoscrapper/progress/data/` or `items_rules.default.json`
4. Regenerate data with `scripts/update_snapshot_and_defaults.py` when needed
5. Run validation: `uv run ruff check src/ tests/ && uv run ty check src/ && uv run basedpyright src/ && uv run pytest`

## Delivery Waves

| Wave | Goal | Tasks | Parallel |
|------|------|-------|----------|
| 1 | Data pipeline | T014, T034, T003 | T014∥T034 |
| 2 | OCR accuracy | T027, T012, T013, T028, T030, T032 | All parallel |
| 3 | Code quality | T036, T037 | Parallel |
| 4 | Test coverage | T039, T040, T041 | Parallel |
| 5 | Features | T019, T020 | Parallel |
| 6 | Performance | T042, T043 | Parallel |

## Priority Queue

| # | Task | Why |
|---|------|-----|
| 1 | T014 | Unblocks T003, removes security risk |
| 2 | T034 | High-value data pipeline |
| 3 | T027 | High OCR accuracy impact |
| 4 | T039 | Critical untested business logic |
| 5 | T012 | Quick win for weapon recognition |

---

## Tasks

### T003 - Hybrid MetaForge plus wiki pipeline
<blocked-on>T014</blocked-on>
| Attr | Value |
|------|-------|
| Priority | medium |
| Size | M |
| Status | blocked |

**Files:** `src/autoscrapper/progress/data_update.py`

**Done:**
- [ ] MetaForge primary + RaidTheory fallback intact
- [ ] Wiki enrichment for workshop/expedition/project data
- [ ] Dry-run reports coverage
- [ ] Metadata records field origins

---

### T012 - Roman numeral OCR alias correction
| Attr | Value |
|------|-------|
| Priority | medium |
| Size | S |
| Status | ready |

**File:** `src/autoscrapper/core/item_actions.py`

**Done:**
- [ ] Normalization corrects OCR suffix errors (1V, 111)
- [ ] Canonical matching uses existing fuzzy threshold
- [ ] Tests cover corrected and unchanged names

---

### T013 - Filter weapon swap UI text from item-name detection
| Attr | Value |
|------|-------|
| Priority | medium |
| Size | S |
| Status | ready |

**File:** `src/autoscrapper/ocr/inventory_vision.py`

**Done:**
- [ ] Swap UI strings ignored on first title pass
- [ ] Retry path reaches real item name below UI line
- [ ] No regression in unrelated title extraction

---

### T014 - Remove Supabase dependency
<critical-path/>
| Attr | Value |
|------|-------|
| Priority | high |
| Size | M |
| Status | ready |

**Files:** `src/autoscrapper/progress/data_update.py`, `scripts/update_snapshot_and_defaults.py`

**Done:**
- [ ] MetaForge uses `includeComponents` instead of Supabase
- [ ] All Supabase constants/helpers deleted
- [ ] Updater runs without Supabase calls

**Risk:** Breaking data pipeline. Mitigation: Test with `--dry-run` first.

---

### T019 - Per-session decision log
| Attr | Value |
|------|-------|
| Priority | medium |
| Size | S |
| Status | ready |

**File:** `src/autoscrapper/scanner/`

**Done:**
- [ ] JSONL decision records when logging enabled
- [ ] Log: timestamp, raw_text, decision, location, score, source
- [ ] Opt-in, no scan slowdown

---

### T020 - Safe recycle protection against quest requirements
| Attr | Value |
|------|-------|
| Priority | medium |
| Size | M |
| Status | ready |

**File:** `src/autoscrapper/progress/`

**Done:**
- [ ] Recycle decisions cross-checked against quest requirements
- [ ] Conflicts override to KEEP with quest reason
- [ ] Graceful degradation when progress data absent

---

### T027 - Feed item names to Tesseract as user_words
<critical-path/>
| Attr | Value |
|------|-------|
| Priority | high |
| Size | M |
| Status | ready |

**Files:** `src/autoscrapper/ocr/tesseract.py`, `src/autoscrapper/items/rules_store.py`

**Done:**
- [ ] `initialize_ocr` writes tokens to temp file, loads via `user_words_suffix`
- [ ] `load_system_dawg` set to 0
- [ ] Re-init on rules_store changes
- [ ] Corpus replay shows no regressions

**Risk:** Tesseract re-init is expensive. Mitigation: Pre-load at startup only.

---

### T028 - Pad all four sides of OCR title-strip ROIs
| Attr | Value |
|------|-------|
| Priority | medium |
| Size | S |
| Status | ready |

**File:** `src/autoscrapper/ocr/inventory_vision.py`

**Done:**
- [ ] Top/bottom/right get symmetric _TITLE_PAD pixels of median background
- [ ] Retry path keeps existing expansion
- [ ] Corpus replay shows no regressions

---

### T030 - Confidence-gated retry
| Attr | Value |
|------|-------|
| Priority | medium |
| Size | S |
| Status | ready |

**File:** `src/autoscrapper/ocr/inventory_vision.py`

**Done:**
- [ ] Primary read uses `image_to_data`, computes mean per-character confidence
- [ ] Retries fire when mean_conf < 60 even if fuzzy match exists
- [ ] Highest-confidence result wins

---

### T032 - Set user_defined_dpi=300 on Tesseract API
| Attr | Value |
|------|-------|
| Priority | low |
| Size | XS |
| Status | ready |

**File:** `src/autoscrapper/ocr/tesseract.py`

**Done:**
- [ ] `initialize_ocr` sets `user_defined_dpi` to 300
- [ ] No corpus regression

---

### T034 - Integrate Arc-Lens data scraping pipeline
| Attr | Value |
|------|-------|
| Priority | high |
| Size | L |
| Status | ready |

**Files:** New `scripts/vendor/arc-lens/`, `scripts/update_snapshot_and_defaults.py`

**Refs:** https://github.com/eetusa/arc-lens/

**Done:**
- [ ] Vendor arc-lens scrapers under `scripts/vendor/arc-lens/`
- [ ] Port JS to Python using `requests` + `BeautifulSoup`
- [ ] Wire into `update_snapshot_and_defaults.py`
- [ ] Add `--source arc-lens` flag
- [ ] Document scraper contributions
- [ ] Graceful failure if Arc-Lens unavailable

---

### T035 - Consolidate duplicated normalization functions
| Attr | Value |
|------|-------|
| Priority | high |
| Size | S |
| Status | **COMPLETE** |

**Files:** `src/autoscrapper/progress/progress_config.py`, `quest_inference.py`, `update_report.py`

**Done:**
- [x] Shared utility in `src/autoscrapper/utils/normalization.py`
- [x] All 3 files import from shared location
- [x] Tests pass, no regression

---

### T036 - Refactor oversized modules
<critical-path/>
| Attr | Value |
|------|-------|
| Priority | medium |
| Size | L |
| Status | ready |

**Files:** `src/autoscrapper/ocr/inventory_vision.py` (1781L), `progress/decision_engine.py` (434L)

**Done:**
- [ ] `inventory_vision.py` → preprocessing.py, detection.py, matching.py
- [ ] `decision_engine.py` → quest_logic.py, hideout_logic.py, crafting_logic.py
- [ ] All imports updated, tests pass
- [ ] No functional changes

**Risk:** High regression risk. Mitigation: Pure moves only, test at each step.

---

### T037 - Replace broad exception handling
| Attr | Value |
|------|-------|
| Priority | medium |
| Size | M |
| Status | ready |

**Files:** `src/autoscrapper/api/client.py`, `progress/data_update.py`

**Done:**
- [ ] API client raises specific exceptions (RateLimitError, AuthError, NotFoundError)
- [ ] Data update catches specific exceptions per operation
- [ ] Contextual error messages
- [ ] Tests verify handling

---

### T038 - Introduce async/await patterns
<critical-path/>
| Attr | Value |
|------|-------|
| Priority | medium |
| Size | L |
| Status | ready |

**Files:** `scanner/scan_loop.py`, `api/client.py`, `interaction/`

**Done:**
- [ ] API client uses `aiohttp` or `httpx`
- [ ] Scanner supports concurrent cell processing
- [ ] Async-aware rate limiting
- [ ] Benchmark shows improvement

**Risk:** OCR and input are synchronous. Mitigation: Async only for I/O, keep OCR on main thread.

---

### T039 - Add tests for decision_engine.py
| Attr | Value |
|------|-------|
| Priority | high |
| Size | M |
| Status | ready |

**File:** New `tests/progress/test_decision_engine.py`

**Done:**
- [ ] Unit tests for KEEP/SELL/RECYCLE paths
- [ ] Quest requirement conflict tests
- [ ] Hideout upgrade priority tests
- [ ] Crafting value evaluation tests
- [ ] >80% coverage

---

### T040 - Add tests for inventory_grid.py
| Attr | Value |
|------|-------|
| Priority | high |
| Size | M |
| Status | ready |

**File:** New `tests/interaction/test_inventory_grid.py`

**Done:**
- [ ] Cell coordinate calculation tests
- [ ] Grid detection edge case tests
- [ ] Row/column boundary tests
- [ ] Multi-resolution tests

---

### T041 - Add integration tests for OCR pipeline
| Attr | Value |
|------|-------|
| Priority | medium |
| Size | L |
| Status | ready |

**File:** New `tests/ocr/test_ocr_pipeline_integration.py`

**Done:**
- [ ] Fixtures with sample inventory images
- [ ] Full flow: image → OCR → fuzzy match → decision
- [ ] Polarity detection, retry logic, confidence gating tests
- [ ] Mock Tesseract for determinism

---

### T042 - Implement rule caching
| Attr | Value |
|------|-------|
| Priority | medium |
| Size | S |
| Status | ready |

**Files:** `core/item_actions.py`, `items/rules_store.py`

**Done:**
- [ ] In-memory rule cache with TTL
- [ ] Cache invalidation on file modification
- [ ] Cache stats (hit rate, size)
- [ ] Benchmark shows improvement

---

### T043 - Optimize OCR image processing
| Attr | Value |
|------|-------|
| Priority | high |
| Size | M |
| Status | ready |

**File:** `src/autoscrapper/ocr/inventory_vision.py`

**Done:**
- [ ] Cache preprocessed images between passes
- [ ] Remove duplicate connectedComponentsWithStats
- [ ] Lazy upscaling when needed
- [ ] Benchmark shows <20% latency reduction

---

## Quick Reference

### Validation
```bash
uv run ruff check src/ tests/
uv run ty check src/
uv run basedpyright src/
uv run pytest
```

### Skills
| Skill | Use When |
|-------|----------|
| `verify` | Pre-commit validation |
| `ocr-corpus-replay` | OCR changes |
| `threshold-corpus-replay` | Threshold changes |
| `add-fixture` | New OCR regression test |
| `dead-code-sweep` | Cleanup |

### Critical Files (Extra Caution)
- `src/autoscrapper/ocr/inventory_vision.py`
- `src/autoscrapper/scanner/`
- `src/autoscrapper/core/item_actions.py`
- `src/autoscrapper/config.py`
