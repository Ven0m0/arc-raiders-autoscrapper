# Codebase Audit Plan

## Overview
Comprehensive audit of the Arc Raiders AutoScrapper Python codebase for quality, security, and correctness.

## Current Status Summary

### Tooling Results
| Tool | Result | Notes |
|------|--------|-------|
| ruff | PASS | All checks passed |
| basedpyright | 28 type errors | See Type Errors section |
| vulture | 5 issues (tests only) | Unused test variables |
| deadcode | 100+ findings | Mostly TUI framework methods (false positives) |
| pytest | 260 passed, 2 failed | 2 test failures need fixing |

### Test Failures
1. `tests/autoscrapper/ocr/test_failure_corpus.py::test_resolve_image_path_traversal`
   - Missing `schema_version` argument in `OcrFailureSample.__init__()`
   
2. `tests/scripts/test_replay_ocr_failure_corpus.py::test_evaluate_threshold_records_expected_status_and_correctness`
   - Extra `captured_cleaned_text` field in output

## Critical Issues (Fix First)

### 1. Type Safety Errors (basedpyright)

#### File: `src/autoscrapper/ocr/failure_corpus.py`
- Line 151: `normalized_label_status` type mismatch - `str` not assignable to `OcrFailureLabelStatus`
- Lines 160-166: Multiple `Unknown | None` arguments not assignable to required `str` parameters

#### File: `src/autoscrapper/items/rules_store.py`
- Line 80: Object of type "None" is not subscriptable

#### File: `src/autoscrapper/interaction/ui_windows.py`
- Line 108: Cannot access attribute "getTitle" for class "LinuxWindow"
- Line 196: Return type mismatch - `None` not assignable to tuple types
- Line 228: "base" is not a known attribute of module "mss"

#### File: `src/autoscrapper/ocr/inventory_vision.py`
- Line 409: `ndarray` not assignable to `Mat` in `inRange` call
- Line 809: `None` not assignable to `dsize` in `resize` call

#### File: `src/autoscrapper/ocr/tesseract.py`
- Line 82: `int` not assignable to `PSM` parameter

#### File: `src/autoscrapper/progress/decision_engine.py`
- Lines 235-258: Multiple `list[str] | bool` type errors in join() calls
- Line 366: `Unknown | None` not assignable to `str` in get()

#### File: `src/autoscrapper/progress/data_update.py`
- Line 34: Import "bs4" could not be resolved
- Lines 424-425: `Unknown | None` not assignable to `str`
- Lines 503, 513: Possibly unbound variables `_requests`, `_BeautifulSoup`

#### File: `src/autoscrapper/progress/update_report.py`
- Line 26: `object` not assignable to `ConvertibleToFloat`

#### File: `src/autoscrapper/progress/quest_overrides.py`
- Line 17: `Unknown | None` not assignable to `str`

### 2. Test Failures

#### Fix: `tests/autoscrapper/ocr/test_failure_corpus.py`
The `OcrFailureSample` dataclass requires `schema_version` but test doesn't provide it.

#### Fix: `tests/scripts/test_replay_ocr_failure_corpus.py`
Test expects specific dict keys but code adds extra `captured_cleaned_text` field.

## Medium Priority Issues

### 3. Dead Code (Legitimate Findings)

#### File: `src/autoscrapper/interaction/input_driver.py`
- Lines 14-24: Platform-specific attributes assigned but never read directly
  - `FAILSAFE`, `PAUSE`, `argtypes`, `restype` (Windows)
  
#### File: `src/autoscrapper/interaction/inventory_grid.py`
- Line 191: Method `center_by_index` is never used

#### File: `src/autoscrapper/ocr/inventory_vision.py`
- Line 139: Variable `candidate_count` is never used

#### File: `src/autoscrapper/scanner/__init__.py`
- Line 12: Function `__getattr__` is never used

### 4. Code Quality Issues

#### Print Statements (should use logging)
- `src/autoscrapper/warmup.py:52` - print for warning
- `src/autoscrapper/scanner/engine.py:256,351` - print for status/warning
- `src/autoscrapper/scanner/report.py` - multiple console.print (acceptable for TUI)
- `src/autoscrapper/core/item_actions.py:79-91` - print for warnings
- `src/autoscrapper/ocr/inventory_vision.py` - multiple debug prints

#### Magic Numbers
- Multiple calibration constants in `inventory_vision.py` need documentation
- Threshold values scattered across files

## Low Priority / Deferred

### 5. TUI Framework Methods (False Positives from deadcode)
The deadcode tool reports many unused methods in TUI files. These are framework callbacks used by Textual and should NOT be removed:
- `compose()` methods
- `on_key()` methods  
- `on_button_pressed()` methods
- `action_*()` methods

### 6. Dependency Security
- No CVE scanner (pip-audit) available in environment
- Recommend adding `pip-audit` or `safety` to dev dependencies

## Proposed Fixes

### Phase 1: Critical (Breaking)
1. Fix test failures in `test_failure_corpus.py` and `test_replay_ocr_failure_corpus.py`
2. Add type annotations to fix basedpyright errors
3. Fix `rules_store.py:80` None subscript issue

### Phase 2: Type Safety
1. Add proper type guards for Optional values
2. Fix numpy/opencv type stubs issues
3. Add `# type: ignore` comments for platform-specific imports with explanations

### Phase 3: Code Quality
1. Replace print statements with logging where appropriate
2. Remove genuinely dead code (non-TUI)
3. Document magic numbers

### Phase 4: Testing
1. Add bandit security scanner
2. Add pip-audit for dependency CVE checking
3. Achieve 100% test pass rate

## Risk Assessment

| Change | Risk Level | Breaking Potential |
|--------|------------|-------------------|
| Fix test failures | Low | None (tests only) |
| Add type annotations | Low | None |
| Fix None subscript | Medium | Low (runtime safety) |
| Replace print with logging | Low | None |
| Remove dead code | Medium | Medium (verify first) |

## Files Requiring Attention

### High Priority
- `src/autoscrapper/ocr/failure_corpus.py`
- `src/autoscrapper/items/rules_store.py`
- `src/autoscrapper/interaction/ui_windows.py`
- `tests/autoscrapper/ocr/test_failure_corpus.py`
- `tests/scripts/test_replay_ocr_failure_corpus.py`

### Medium Priority
- `src/autoscrapper/progress/decision_engine.py`
- `src/autoscrapper/progress/data_update.py`
- `src/autoscrapper/interaction/input_driver.py`
- `src/autoscrapper/ocr/inventory_vision.py`
- `src/autoscrapper/ocr/tesseract.py`

### Low Priority (Documentation/Style)
- `src/autoscrapper/warmup.py`
- `src/autoscrapper/scanner/engine.py`
- `src/autoscrapper/core/item_actions.py`

## Implementation Order

1. Fix test failures (immediate)
2. Fix type errors in core files
3. Add missing type annotations
4. Clean up dead code
5. Add security scanning tools
6. Document remaining technical debt
