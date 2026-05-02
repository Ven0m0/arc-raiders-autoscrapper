---
title: Implementation Plan
status: active
updated: 2026-04-26
updated_by: kilo
---

<!-- AGENT GUIDE: Read AGENTS.md first. Never hand-edit data/ or items_rules.default.json -->

<!-- Last updated: 2026-04-26T07:59:00+00:00 -->
<!-- Plan review: T034 and T020 verified complete. Remaining: T003 (blocked), T036, T037, T038 -->

## Active Tasks

### T003 - Hybrid MetaForge plus wiki pipeline
<blocked-on>T014</blocked-on>
| Attr | Value |
|------|-------|
| Priority | medium |
| Size | M |
| Status | blocked |

**Files:** `src/autoscrapper/progress/data_update.py`

**Todo:**
- [ ] Wiki enrichment for workshop/expedition/project data
- [ ] Dry-run reports coverage
- [ ] Metadata records field origins

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
- [ ] Replace `except Exception:` with specific types (currently 15 instances)
- [ ] Add contextual error messages
- [ ] Tests verify specific exception handling

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


### T039 Replace httpx with "httpx[http2]

use http2 for httpx via "httpx[http2]

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

## Completed Tasks

| Task | Status | Notes |
|------|--------|-------|
| T012-T014, T019 | ✅ | Core infrastructure |
| T020 | ✅ Verified | `is_used_in_active_quests()` handles empty progress gracefully |
| T027-T028, T030, T032 | ✅ | UI/OCR improvements |
| T034 | ✅ Verified | Full Arc-Lens implementation (516 lines in scrapers.py) |
| T035, T039-T043 | ✅ | Normalization, tests, caching, optimization |

## Priority Order

1. **T036** - Module refactoring (maintainability)
2. **T037** - Exception handling (reliability)
3. **T038** - Async patterns (performance)
4. **T003** - Wiki enrichment (blocked on T014)
