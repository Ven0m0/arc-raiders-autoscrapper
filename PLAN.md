# Arc Raiders AutoScrapper — Technical Debt & Feature Plan

Generated: 2026-04-14  
Source: TODO.md + inline `# type: ignore` / `# noqa` audit of `src/` + status review

---

## Completed Tasks (removed from active backlog)

| ID   | Title                                          | Completed  |
|------|------------------------------------------------|------------|
| T003 | Hybrid database updater (MetaForge + Wiki)     | 2026-04-14 |
| T005 | LiveWindow Protocol for `isAlive` access       | 2026-04-14 |
| T006 | Add `opencv-stubs` dev dependency              | 2026-04-14 |
| T007 | Fix `on_screen_resume` signature               | 2026-04-14 |
| T008 | Narrow bare-Exception in `MaintenanceScreen`   | 2026-04-14 |
| T009 | Add `__all__` to `rich_support.py`             | 2026-04-14 |
| T010 | Fix stale infobox rect on OCR retry            | 2026-04-14 |
| T011 | Remove dead code in `_extract_title_from_data` | 2026-04-14 |
| T016 | Integrate arctracker.io API for stash sync     | 2026-04-14 |

---

## Dependency Graph

```
T001 ──► T002

T004  (independent)
T012  (independent)
T013  (independent)
T014  (independent)
T015  (independent)
T017  (independent)
T018  (independent)
```

**Wave 1** (parallelisable): T001, T004, T012, T013, T014, T015, T017, T018  
**Wave 2** (unblocked after T001 lands): T002

---

## Tasks

---

### T001 — Calibrate DEFAULT_ITEM_NAME_MATCH_THRESHOLD from live SKIP_UNLISTED corpus

**Anchor:** `src/autoscrapper/ocr/inventory_vision.py:47`  
**Severity:** medium  
**Category:** performance · debt  
**Size:** M (20–100 LOC)  
**Blocks:** T002

**Context**

`DEFAULT_ITEM_NAME_MATCH_THRESHOLD = 75` is a hand-picked constant. The repo
already has capture and replay tooling for this calibration loop:
`autoscrapper/ocr/failure_corpus.py:capture_skip_unlisted_sample()` writes
samples to `artifacts/ocr/skip_unlisted/samples.jsonl`, and
`scripts/replay_ocr_failure_corpus.py` can sweep candidate thresholds and write
reports. The remaining gap is to use that existing corpus/replay path to validate
the default threshold, confirm the captured fields and reported metrics are
sufficient for decision-making, and extend the tooling only if the current output
is missing data needed to judge false positives versus `SKIP_UNLISTED` outcomes
(items ignored that should be actioned).

**Acceptance criteria**

- `capture_skip_unlisted_sample()` continues to persist the fields needed for
  replay-based calibration, including at minimum `raw_text`, `chosen_name`,
  `matched_name`, and the image path in the JSON-lines corpus.
- `scripts/replay_ocr_failure_corpus.py` is used as the primary replay harness;
  if it lacks any required metric or input option, T001 scopes the minimal
  extension instead of introducing a duplicate script.
- Replay output supports comparing integer candidate thresholds with enough
  accuracy data to identify false positives and unmatched cases.
- `DEFAULT_ITEM_NAME_MATCH_THRESHOLD` changes only after replay confirms every
  existing corpus sample either stays unmatched or resolves to the correct item
  name.
- The chosen value is documented with the corpus commit hash in a comment
  adjacent to the constant definition at `inventory_vision.py:47`.
- `match_item_name_result()` continues to accept an explicit `threshold`
  override; any caller that hard-codes a different value is updated to use the
  constant.

**Implementation hint**

Extend `scanner/actions.py` (`capture_skip_unlisted_sample()`) via the existing
corpus output at `artifacts/ocr/skip_unlisted/samples.jsonl` rather than
introducing a new `ocr_debug/` sink. Reuse `scripts/replay_ocr_failure_corpus.py`
as the replay harness (or evolve it in place) so it calls
`match_item_name_result(raw, threshold=t)` for each candidate `t` and computes
accuracy. Single source-of-truth constant: `ocr/inventory_vision.py:47`.

---

### T002 — Benchmark tessdata.best-eng accuracy and latency against failure corpus

**Anchor:** `src/autoscrapper/ocr/tesseract.py:1`  
**Severity:** low  
**Category:** performance  
**Size:** S (< 20 LOC)  
**Blocked by:** T001

**Context**

The project pins `tessdata.fast-eng` for speed. `tessdata.best-eng` may
recover OCR failures that produce `SKIP_UNLISTED` outcomes, but only a corpus
replay can confirm whether the accuracy gain justifies the latency cost.

**Acceptance criteria**

- Use the corpus produced by T001 as benchmark input.
- Run the same corpus image set through both `fast-eng` and `best-eng`; record
  per-image recognition time and whether `match_item_name_result()` resolves to
  the expected item name.
- Accept `best-eng` only if it reduces unresolved items without increasing
  median per-image time above 150 ms on the reference hardware.
- If the model changes: update the `tessdata.fast-eng` pin in `pyproject.toml`
  and setup docs in `README.md`, `scripts/setup-linux.sh`,
  `scripts/setup-windows.ps1`.
- If the model stays: record the negative benchmark result in a comment in
  `pyproject.toml`.

**Implementation hint**

Start with `scripts/benchmark_tessdata_models.py`, which already benchmarks
`tessdata.fast-eng` vs `tessdata.best-eng` by switching `TESSDATA_PREFIX` and
writing a report. Use the corpus produced by T001 as input. Only add a
replay-script `--model` flag or change `ocr/tesseract.py` directly if the
existing benchmark script proves insufficient.

---

### T004 — Add ABC inheritance to ScanSettingsScreen

**Anchor:** `src/autoscrapper/tui/settings.py:92`  
**Severity:** low  
**Category:** refactor · debt  
**Size:** S (< 20 LOC)

**Context**

`ScanProgress` (`scanner/progress.py`) already correctly inherits `ABC` and all
ten methods carry `@abstractmethod`. The remaining gap is `ScanSettingsScreen`
itself: `_compose_form` and `_load_into_fields` carry `@abstractmethod`, but the
class declaration at line 92 does not list `ABC` as a base. Without it,
`basedpyright` and runtime `isinstance` checks cannot enforce the abstract
contract.

**Acceptance criteria**

- `ScanSettingsScreen` class declaration adds `ABC` to its base list alongside
  `AppScreen` (or `Screen`).
- `python3 -m uv run basedpyright src/` reports no new errors after the change.
- `python3 -m uv run pytest` passes.

**Implementation hint**

```python
from abc import ABC, abstractmethod
class ScanSettingsScreen(AppScreen, ABC): ...
```

Textual does not block ABC co-inheritance with `Screen`/`AppScreen`.

---

### T012 — Add Roman numeral tier suffix correction for OCR misreads

**Anchor:** `src/autoscrapper/core/item_actions.py`  
**Severity:** medium  
**Category:** ocr · bug  
**Size:** S (< 20 LOC)

**Context**

Tesseract misreads Roman numeral suffixes on ALL-CAPS weapon names: `IV→1V`,
`III→111`, `II→11`, `I→1`. This causes rule lookups to fail for tiered weapons.
`normalize_item_name()` at line 50 currently only strips and lowercases; it does
not correct OCR digit-for-letter substitutions.

**Acceptance criteria**

- Add `OCR_ALIASES` dict and `_fix_roman_ocr_suffix()` function called from
  `normalize_item_name()`.
- OCR-aliased names resolve correctly to the canonical item name.
- `python3 -m uv run pytest` passes (add a test case in
  `tests/autoscrapper/core/test_item_actions.py`).

**Implementation hint**

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

Call `_fix_roman_ocr_suffix(normalized)` at the end of `normalize_item_name()`.

---

### T013 — Filter weapon swap UI text from item name detection

**Anchor:** `src/autoscrapper/ocr/inventory_vision.py`  
**Severity:** medium  
**Category:** ocr · bug  
**Size:** S (< 20 LOC)

**Context**

Weapon infoboxes contain a "Swap with Primary Slot" UI line near the top. OCR
picks this up as the item name instead of the weapon name, producing
`SKIP_UNLISTED` outcomes for valid weapons.

**Acceptance criteria**

- Add `_EXCLUDED_UI_KEYWORDS = frozenset(["swap with", "swap"])` in
  `inventory_vision.py`.
- Skip lines matching these keywords on first pass in `_extract_title_from_data`.
- On retry (`_retry_with_larger=True`), widen `top_fraction` to `0.35` to
  capture the actual name below the UI element.
- Existing title extraction tests continue to pass.

---

### T014 — Remove Supabase dependency from data_update.py

**Anchor:** `src/autoscrapper/progress/data_update.py:26`  
**Severity:** medium  
**Category:** data · security  
**Size:** M (20–100 LOC)

**Context**

Lines 738–749 call `_fetch_supabase_all("arc_item_components")` and
`_fetch_supabase_all("arc_item_recycle_components")` at update time. The
`SUPABASE_URL` constant (line 26) and `SUPABASE_ANON_KEY` env var (line 33) are
still live. The MetaForge `/items?includeComponents=true` API is the intended
replacement, making the Supabase calls redundant. The hardcoded endpoint URL and
key pattern are a credential hygiene risk.

**Acceptance criteria**

- Add `?includeComponents=true` to the MetaForge `/items` API call; extract
  components inline via a new `_extract_component_dict()` helper.
- Remove all Supabase code: `SUPABASE_URL`, `SUPABASE_ANON_KEY`,
  `_fetch_supabase_all`, `_build_component_map`, and the two call sites at
  lines 738–749.
- `python3 -m uv run ruff check src/` passes.
- `python3 -m uv run pytest tests/autoscrapper/progress/test_data_update.py`
  passes.

---

### T015 — Change default stop key from Escape to F9

**Anchor:** `src/autoscrapper/interaction/keybinds.py:5`  
**Severity:** low  
**Category:** ux  
**Size:** S (< 20 LOC)

**Context**

`DEFAULT_STOP_KEY = "escape"` (line 5) conflicts with in-game Escape usage
(opens game menu). F9 is unused by Arc Raiders. `_CANONICAL_DISPLAY` handles
function keys via `_FUNCTION_KEY_PATTERN`, so adding an explicit entry is
optional but improves label display.

**Acceptance criteria**

- Change `DEFAULT_STOP_KEY = "f9"`.
- Add `"f9": "F9"` to `_CANONICAL_DISPLAY` for consistent label rendering.
- `python3 -m uv run pytest tests/autoscrapper/interaction/test_keybinds.py`
  passes.

---

### T017 — Add test suite for src/autoscrapper/api/

**Anchor:** `src/autoscrapper/api/client.py`  
**Severity:** medium  
**Category:** testing  
**Size:** M (20–100 LOC)

**Context**

The `api/` package introduced in T016 has no test coverage. The `ArcTrackerClient`
handles rate limiting, retries, and error fallback — all paths that need unit
tests. The `tests/api/` directory does not yet exist; it was listed in T016's
acceptance criteria but was not delivered.

**Acceptance criteria**

- Create `tests/api/__init__.py` and `tests/api/test_client.py`.
- Test `RateLimitState` tracks and enforces request limits.
- Test `ArcTrackerClient` retry logic with mocked responses (use
  `unittest.mock.patch` or `pytest-httpx`).
- Test graceful fallback when `HAS_REQUESTS = False` or on HTTP errors.
- Test `datasource.py` sync functions against mock API payloads.
- `python3 -m uv run pytest tests/api/` passes.

---

### T018 — Quest-keyed sell/recycle guard (safe-recycle mode)

**Anchor:** `src/autoscrapper/core/item_actions.py`, `src/autoscrapper/progress/`  
**Severity:** medium  
**Category:** feature  
**Size:** M (20–100 LOC)

**Context**

Rule lookup currently uses static per-item KEEP/SELL/RECYCLE rules without
cross-referencing active quest requirements. Items needed for in-progress quests
can be accidentally sold or recycled if the user hasn't set an explicit KEEP
override. The progress data already tracks quest requirements and active/completed
status; the decision layer needs to consult it.

**Acceptance criteria**

- Add a `quest_guard_enabled` setting (default `True`) to the config.
- In `resolve_action()` (or equivalent entry point in `item_actions.py`), before
  returning SELL or RECYCLE, check if any active (non-completed) quest requires
  the item; if so, override to KEEP and tag the reason as `"quest_guard"`.
- Quest guard applies only to items with a `SELL` or `RECYCLE` rule; explicit
  user KEEP overrides are unaffected.
- TUI scan report includes a `"quest_guard"` column or annotation when the guard
  fires.
- `python3 -m uv run pytest` passes with new test cases covering guarded and
  unguarded scenarios.

---

## Status Legend

| Status | Meaning |
|--------|---------|
| `[ ]`  | Not started |
| `[~]`  | In progress |
| `[x]`  | Complete |
| `[!]`  | Blocked |

## Task Summary

| ID   | Title (short)                              | Sev    | Size | Blocked by |
|------|--------------------------------------------|--------|------|------------|
| T001 | Calibrate OCR fuzzy threshold from corpus  | medium | M    | —          |
| T002 | Benchmark tessdata.best-eng vs fast-eng    | low    | S    | T001       |
| T004 | ScanSettingsScreen ABC inheritance (fix)   | low    | S    | —          |
| T012 | Roman numeral OCR alias correction         | medium | S    | —          |
| T013 | Filter weapon swap UI text from OCR        | medium | S    | —          |
| T014 | Remove Supabase dependency from data_update| medium | M    | —          |
| T015 | Change default stop key to F9              | low    | S    | —          |
| T017 | Add tests/api/ test suite                  | medium | M    | —          |
| T018 | Quest-keyed sell/recycle guard             | medium | M    | —          |

**Recommended starting points:**
- T004 — one-line ABC fix, zero dependencies, fully validatable with `basedpyright + pytest`.
- T015 — one-line change with immediate UX impact.
- T012 + T013 — OCR quality bugs, no external dependencies.
