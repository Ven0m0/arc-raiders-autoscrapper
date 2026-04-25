

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

**Todo:**
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
| Status | ✅ COMPLETE |

**File:** `src/autoscrapper/core/item_actions.py`

**Done:**
- [x] Normalization corrects OCR suffix errors (1V, 111)
- [x] Canonical matching uses existing fuzzy threshold
- [x] Tests cover corrected and unchanged names

---

### T013 - Filter weapon swap UI text from item-name detection
| Attr | Value |
|------|-------|
| Priority | medium |
| Size | S |
| Status | ✅ COMPLETE |

**File:** `src/autoscrapper/ocr/inventory_vision.py`

**Done:**
- [x] Swap UI strings ignored on first title pass
- [x] Retry path reaches real item name below UI line
- [x] No regression in unrelated title extraction

---

### T014 - Remove Supabase dependency
<critical-path/>
| Attr | Value |
|------|-------|
| Priority | high |
| Size | M |
| Status | ✅ COMPLETE |

**Files:** `src/autoscrapper/progress/data_update.py`, `scripts/update_snapshot_and_defaults.py`

**Done:**
- [x] MetaForge uses `includeComponents` instead of Supabase
- [x] All Supabase constants/helpers deleted
- [x] Updater runs without Supabase calls

**Risk:** Breaking data pipeline. Mitigation: Test with `--dry-run` first.

---

### T019 - Per-session decision log
| Attr | Value |
|------|-------|
| Priority | medium |
| Size | S |
| Status | ✅ COMPLETE |

**File:** `src/autoscrapper/scanner/`

**Done:**
- [x] JSONL decision records when logging enabled
- [x] Log: timestamp, raw_text, decision, location, score, source
- [x] Opt-in, no scan slowdown

---

### T020 - Safe recycle protection against quest requirements
| Attr | Value |
|------|-------|
| Priority | medium |
| Size | M |
| Status | 🔄 IN PROGRESS |

**File:** `src/autoscrapper/progress/`

**Todo:**
- [ ] Recycle decisions cross-checked against quest requirements
- [ ] Conflicts override to KEEP with quest reason
- [ ] Graceful degradation when progress data absent

**Note:** `decision_engine.py` has partial implementation (quest requirement checking in `get_decision()`). Needs review for graceful degradation.

---

### T027 - Feed item names to Tesseract as user_words
<critical-path/>
| Attr | Value |
|------|-------|
| Priority | high |
| Size | M |
| Status | ✅ COMPLETE |

**Files:** `src/autoscrapper/ocr/tesseract.py`, `src/autoscrapper/items/rules_store.py`

**Done:**
- [x] `initialize_ocr` writes tokens to temp file, loads via `user_words_suffix`
- [x] `load_system_dawg` set to 0
- [x] Re-init on rules_store changes
- [x] Corpus replay shows no regressions

**Risk:** Tesseract re-init is expensive. Mitigation: Pre-load at startup only.

---

### T028 - Pad all four sides of OCR title-strip ROIs
| Attr | Value |
|------|-------|
| Priority | medium |
| Size | S |
| Status | ✅ COMPLETE |

**File:** `src/autoscrapper/ocr/inventory_vision.py`

**Done:**
- [x] Top/bottom/right get symmetric _TITLE_PAD pixels of median background
- [x] Retry path keeps existing expansion
- [x] Corpus replay shows no regressions

---

### T030 - Confidence-gated retry
| Attr | Value |
|------|-------|
| Priority | medium |
| Size | S |
| Status | ✅ COMPLETE |

**File:** `src/autoscrapper/ocr/inventory_vision.py`

**Done:**
- [x] Primary read uses `image_to_data`, computes mean per-character confidence
- [x] Retries fire when mean_conf < 60 even if fuzzy match exists
- [x] Highest-confidence result wins

---

### T032 - Set user_defined_dpi=300 on Tesseract API
| Attr | Value |
|------|-------|
| Priority | low |
| Size | XS |
| Status | ✅ COMPLETE |

**File:** `src/autoscrapper/ocr/tesseract.py`

**Done:**
- [x] `initialize_ocr` sets `user_defined_dpi` to 300
- [x] No corpus regression

---

### T034 - Integrate Arc-Lens data scraping pipeline
| Attr | Value |
|------|-------|
| Priority | high |
| Size | L |
| Status | ❌ TODO |

**Files:** New `scripts/vendor/arc-lens/`, `scripts/update_snapshot_and_defaults.py`

**Refs:** https://github.com/eetusa/arc-lens/

**Todo:**
- [ ] Vendor arc-lens scrapers under `scripts/vendor/arc-lens/`
- [ ] Port JS to Python using `requests` + `BeautifulSoup`
- [ ] Wire into `update_snapshot_and_defaults.py`
- [ ] Add `--source arc-lens` flag
- [ ] Document scraper contributions
- [ ] Graceful failure if Arc-Lens unavailable

**Note:** Only empty `__init__.py` exists in vendor/arc_lens/. No scraper implementation.

---

### T035 - Consolidate duplicated normalization functions
| Attr | Value |
|------|-------|
| Priority | high |
| Size | S |
| Status | ✅ COMPLETE |

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
| Status | ❌ TODO |

**Files:** `src/autoscrapper/ocr/inventory_vision.py` (1832L), `progress/decision_engine.py` (434L)

**Todo:**
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
| Status | ❌ TODO |

**Files:** `src/autoscrapper/api/client.py`, `progress/data_update.py`, `ocr/inventory_vision.py`, `ocr/tesseract.py`, `interaction/ui_windows.py`, `scanner/scan_loop.py`

**Todo:**
- [ ] API client raises specific exceptions (RateLimitError, AuthError, NotFoundError)
- [ ] Data update catches specific exceptions per operation
- [ ] Contextual error messages
- [ ] Tests verify handling
- [ ] Replace `except Exception:` with specific exception types across codebase

---

### T038 - Introduce async/await patterns
<critical-path/>
| Attr | Value |
|------|-------|
| Priority | medium |
| Size | L |
| Status | ❌ TODO |

**Files:** `scanner/scan_loop.py`, `api/client.py`, `interaction/`

**Todo:**
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
| Status | ✅ COMPLETE |

**File:** New `tests/progress/test_decision_engine.py`

**Done:**
- [x] Unit tests for KEEP/SELL/RECYCLE paths
- [x] Quest requirement conflict tests
- [x] Hideout upgrade priority tests
- [x] Crafting value evaluation tests
- [x] >80% coverage

---

### T040 - Add tests for inventory_grid.py
| Attr | Value |
|------|-------|
| Priority | high |
| Size | M |
| Status | ✅ COMPLETE |

**File:** New `tests/interaction/test_inventory_grid.py`

**Done:**
- [x] Cell coordinate calculation tests
- [x] Grid detection edge case tests
- [x] Row/column boundary tests
- [x] Multi-resolution tests

---

### T041 - Add integration tests for OCR pipeline
| Attr | Value |
|------|-------|
| Priority | medium |
| Size | L |
| Status | ✅ COMPLETE |

**File:** New `tests/ocr/test_ocr_pipeline_integration.py`

**Done:**
- [x] Fixtures with sample inventory images
- [x] Full flow: image → OCR → fuzzy match → decision
- [x] Polarity detection, retry logic, confidence gating tests
- [x] Mock Tesseract for determinism

---

### T042 - Implement rule caching
| Attr | Value |
|------|-------|
| Priority | medium |
| Size | S |
| Status | ✅ COMPLETE |

**Files:** `core/item_actions.py`, `items/rules_store.py`

**Done:**
- [x] In-memory rule cache with TTL
- [x] Cache invalidation on file modification
- [x] Cache stats (hit rate, size)
- [x] Benchmark shows improvement

---

### T043 - Optimize OCR image processing
| Attr | Value |
|------|-------|
| Priority | high |
| Size | M |
| Status | ✅ COMPLETE |

**File:** `src/autoscrapper/ocr/inventory_vision.py`

**Done:**
- [x] Cache preprocessed images between passes
- [x] Remove duplicate connectedComponentsWithStats
- [x] Lazy upscaling when needed
- [x] Benchmark shows <20% latency reduction

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
| `scan-report` | Analyze scan failures |
| `failure-to-fix` | End-to-end failure pipeline |
| `config-bump` | Persisted config changes |

### Critical Files (Extra Caution)
- `src/autoscrapper/ocr/inventory_vision.py` (1832 lines - candidate for T036 refactor)
- `src/autoscrapper/scanner/scan_loop.py` (async candidate - T038)
- `src/autoscrapper/progress/decision_engine.py` (434 lines - candidate for T036 refactor)
- `src/autoscrapper/config.py`
- `src/autoscrapper/api/client.py` (T037 exception handling)

### Completed Tasks (Auto-generated from status)
✅ T012, T013, T014, T019, T027, T028, T030, T032, T035, T039, T040, T041, T042, T043

### Incomplete Tasks (Require Work)
❌ T034 (Arc-Lens scraper), T036 (module refactor), T037 (exception handling), T038 (async)
🔄 T020 (quest recycle protection - partial)
