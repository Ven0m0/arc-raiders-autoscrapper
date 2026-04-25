---
title: Implementation Plan
status: active
updated: 2026-04-25
updated_by: kilo
---

<!-- AGENT GUIDE: Read AGENTS.md first. Never hand-edit data/ or items_rules.default.json -->

<!-- Last updated: 2026-04-25T04:56:00+00:00 -->
<!-- Plan review: Only remaining tasks shown. Completed tasks (T012, T013, T014, T019, T027, T028, T030, T032, T035, T039, T040, T041, T042, T043) removed to reduce context -->

## Active Tasks

### T003 - Hybrid MetaForge plus wiki pipeline
<blocked-on>T014</blocked-on>
| Attr | Value |
|------|-------|
| Priority | medium |
| Size | M |
| Status | blocked (Supabase removal complete) |

**Files:** `src/autoscrapper/progress/data_update.py`

**Todo:**
- [ ] Wiki enrichment for workshop/expedition/project data
- [ ] Dry-run reports coverage
- [ ] Metadata records field origins

---

### T020 - Safe recycle protection against quest requirements
| Attr | Value |
|------|-------|
| Priority | medium |
| Size | M |
| Status | 🔄 IN PROGRESS |

**File:** `src/autoscrapper/progress/`

**Todo:**
- [ ] Graceful degradation when progress data absent
- [ ] Review conflict resolution (recycle vs quest requirement)

**Note:** `decision_engine.py` has `is_used_in_active_quests()` returning KEEP for quest-needed items. Needs graceful degradation review.

---

### T034 - Integrate Arc-Lens data scraping pipeline
<critical-path/>
| Attr | Value |
|------|-------|
| Priority | high |
| Size | L |
| Status | ❌ TODO |

**Files:** `scripts/vendor/arc-lens/`, `scripts/update_snapshot_and_defaults.py`

**Refs:** https://github.com/eetusa/arc-lens/

**Todo:**
- [ ] Port JS scrapers to Python (`requests` + `BeautifulSoup`)
- [ ] Implement `WikiItemScraper`, `WikiQuestScraper`, `WikiProjectScraper`, `MetaforgeScraper`
- [ ] Wire into `update_snapshot_and_defaults.py`
- [ ] Add `--source arc-lens` CLI flag
- [ ] Graceful failure handling

**Note:** Only empty `__init__.py` in vendor/arc_lens/. No implementation.

---

### T036 - Refactor oversized modules
<critical-path/>
| Attr | Value |
|------|-------|
| Priority | medium |
| Size | L |
| Status | ❌ TODO |

**Files:** 
- `src/autoscrapper/ocr/inventory_vision.py` (1832 lines)
- `src/autoscrapper/progress/decision_engine.py` (434 lines)

**Todo:**
- [ ] `inventory_vision.py` → `preprocessing.py`, `detection.py`, `matching.py`
- [ ] `decision_engine.py` → `quest_logic.py`, `hideout_logic.py`, `crafting_logic.py`
- [ ] Update all imports
- [ ] No functional changes (pure refactor)

**Risk:** High regression risk. Mitigation: Pure moves only, test at each step.

---

### T037 - Replace broad exception handling
| Attr | Value |
|------|-------|
| Priority | medium |
| Size | M |
| Status | ❌ TODO |

**Files:** 
- `src/autoscrapper/api/client.py`
- `src/autoscrapper/progress/data_update.py`
- `src/autoscrapper/ocr/inventory_vision.py`
- `src/autoscrapper/ocr/tesseract.py`
- `src/autoscrapper/interaction/ui_windows.py`
- `src/autoscrapper/scanner/scan_loop.py`

**Todo:**
- [ ] Define specific exceptions (RateLimitError, AuthError, NotFoundError, etc.)
- [ ] Replace `except Exception:` with specific types
- [ ] Add contextual error messages
- [ ] Tests verify specific exception handling

**Current:** 15 instances of `except Exception:`

---

### T038 - Introduce async/await patterns
<critical-path/>
| Attr | Value |
|------|-------|
| Priority | medium |
| Size | L |
| Status | ❌ TODO |

**Files:** 
- `scanner/scan_loop.py`
- `api/client.py`
- `interaction/`

**Todo:**
- [ ] API client: `aiohttp` or `httpx` async
- [ ] Scanner: concurrent cell processing
- [ ] Async-aware rate limiting
- [ ] Benchmark showing improvement

**Constraint:** OCR and input remain synchronous

---

## Validation

```bash
uv run ruff check src/ tests/
uv run ty check src/
uv run basedpyright src/
uv run pytest
```

## Skills

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
| `patch-update` | Game patch updates |

## Critical Files

- `src/autoscrapper/ocr/inventory_vision.py` (1832L) - T036 refactor candidate
- `src/autoscrapper/scanner/scan_loop.py` (async - T038)
- `src/autoscrapper/progress/decision_engine.py` (434L) - T036 refactor candidate
- `src/autoscrapper/config.py`
- `src/autoscrapper/api/client.py` (T037 exception handling)

## Recently Completed (reference)

✅ T012 (roman numerals), T013 (swap filter), T014 (Supabase), T019 (JSONL), T027 (user_words), T028 (padding), T030 (confidence), T032 (DPI), T035 (normalization), T039-043 (tests), T042 (caching), T043 (optimization)

## Priority Order

1. **T034** - Arc-Lens scraper (blocks data pipeline)
2. **T036** - Module refactoring (maintainability)
3. **T037** - Exception handling (reliability)
4. **T020** - Quest recycle protection
5. **T038** - Async patterns (performance)