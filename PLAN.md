# Arc Raiders AutoScrapper — Technical Debt & Feature Plan

Generated: 2026-04-14  
Source: Inline `# type: ignore` / `# noqa` audit of `src/` + codebase status review

---

## Completed (removed from active tracking)

| ID   | Title                                          | Notes                                                    |
|------|------------------------------------------------|----------------------------------------------------------|
| T004 | Promote ScanProgress to ABC                    | Complete; ScanSettingsScreen partial → T017              |
| T005 | LiveWindow Protocol for isAlive access         | `ui_windows.py:19` implemented                           |
| T006 | Add cv2 type stubs                             | `opencv-stubs` in dev deps                               |
| T007 | Fix on_screen_resume signature                 | `scan.py:203` correct, no type: ignore                   |
| T008 | Narrow bare-Exception in MaintenanceScreen     | `DownloadError | OSError` explicit catches               |
| T009 | Add `__all__` to rich_support.py               | Full `__all__` list at top of file                       |
| T011 | Remove dead code in `_extract_title_from_data` | Dead block already deleted                               |
| —    | Permissive `clean_ocr_text` regex (OCR-03)     | `item_actions.py:57` already uses permissive char class  |
| —    | Dead code in `inventory_vision.py` (BUG-02)    | Already removed from fork                                |

---

## Dependency Graph

```
T001 ──► T002
T014 ──► T003  (Supabase removal must land before hybrid updater)

T010 (independent)
T012 (independent)
T013 (independent)
T015 (independent)
T016 (independent)
T017 (independent)
T018 (independent)
T019 (independent)
T020 (independent)
T021 (independent)
T022 (independent)
```

> **Arrow convention:** `A ──► B` means A must complete before B starts (A unblocks B).

**Wave 1** (parallelisable): T010, T012, T013, T014, T015, T016, T017, T018, T019, T020, T021, T022, T001  
**Wave 2**: T003 (after T014), T002 (after T001)

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
already has `autoscrapper/ocr/failure_corpus.py:capture_skip_unlisted_sample()`
writing samples to `artifacts/ocr/skip_unlisted/samples.jsonl`, and
`scripts/replay_ocr_failure_corpus.py` can sweep candidate thresholds and write
reports. The remaining gap is to use that existing corpus/replay path to validate
the default threshold.

**Acceptance criteria**

- `capture_skip_unlisted_sample()` persists at minimum `raw_text`, `chosen_name`,
  `matched_name`, and the image path.
- `scripts/replay_ocr_failure_corpus.py` is the primary replay harness; extend it
  in place rather than introducing a duplicate script.
- Replay output compares integer candidate thresholds with per-threshold accuracy.
- `DEFAULT_ITEM_NAME_MATCH_THRESHOLD` changes only after replay confirms no
  regression on the corpus.
- The chosen value is documented with the corpus commit hash adjacent to the
  constant at `inventory_vision.py:47`.

**Implementation hint**

Reuse `scripts/replay_ocr_failure_corpus.py` — call
`match_item_name_result(raw, threshold=t)` per candidate and compute accuracy.
Single source-of-truth constant: `src/autoscrapper/ocr/inventory_vision.py:47`.

---

### T002 — Benchmark tessdata.best-eng accuracy and latency against failure corpus

**Anchor:** `src/autoscrapper/ocr/tesseract.py:1`  
**Severity:** low  
**Category:** performance  
**Size:** S (< 20 LOC)  
**Blocked by:** T001

**Context**

The project pins `tessdata.fast-eng` for speed. `tessdata.best-eng` may recover
OCR failures that produce `SKIP_UNLISTED` outcomes. Only a corpus replay can
confirm whether the accuracy gain justifies the latency cost.

**Acceptance criteria**

- Use the corpus produced by T001.
- Run both `fast-eng` and `best-eng`; record per-image recognition time and
  whether `match_item_name_result()` resolves correctly.
- Accept `best-eng` only if it reduces unresolved items without raising median
  per-image time above 150 ms.
- If model changes: update the pin in `pyproject.toml` and setup docs.
- If model stays: record the negative result in a comment in `pyproject.toml`.

**Implementation hint**

Start with `scripts/benchmark_tessdata_models.py`.

---

### T003 — Implement hybrid database updater from MetaForge API + Arc Raiders Wiki

**Anchor:** `src/autoscrapper/progress/data_update.py`  
**Severity:** medium  
**Category:** feature  
**Size:** M (20–100 LOC)  
**Blocked by:** T014

**Context**

The repo already has `scripts/update_snapshot_and_defaults.py` and optional
`scraper` dependencies (`requests`, `beautifulsoup4`) in `pyproject.toml`. The
missing piece is an optional wiki-enrichment phase for workshop upgrades,
expedition requirements, and project-use data. T014 (Supabase removal) must
land first to avoid conflicts in `data_update.py`.

**Acceptance criteria**

- MetaForge remains the primary source; RaidTheory fallback remains intact.
- Wiki scraping enriches workshop upgrades, expedition requirements, project-use
  data keyed by canonical item names.
- A dry-run entrypoint exits 0 and reports item/source coverage without writing
  tracked files.
- `metadata.json` records which fields came from MetaForge, RaidTheory, and wiki.
- `README.md` documents the new extra and dry-run workflow.

---

### T010 — Fix stale infobox rect causing wrong OCR crops at session end

**Anchor:** `src/autoscrapper/scanner/scan_loop.py`  
**Severity:** high  
**Category:** bug  
**Size:** S (< 20 LOC)

**Context**

OCR retry passes in `_ScanRunner._ocr_infobox_with_retries` reuse the
previously-detected infobox rect without re-detecting. When the context menu
closes between attempts the scanner crops the "TAB | CLOSE" button bar at screen
bottom, producing empty or garbage item names.

**Acceptance criteria**

- On retry (`ocr_attempt > 0`), re-capture the full window and call
  `find_infobox()` for a fresh rect.
- Break early if detection returns `None` (menu closed).
- `ocr_debug/` crops no longer contain "TAB CLOSE" text on retry attempts.

**Implementation hint**

```python
# In the ocr_attempt > 0 branch:
window_bgr = capture_region((self.context.win_left, self.context.win_top, self.context.win_width, self.context.win_height))
new_rect = find_infobox(window_bgr)
if new_rect is None:
    break  # infobox closed; abort retry
x, y, w, h = new_rect
infobox_bgr = window_bgr[y : y + h, x : x + w]
```

---

### T012 — Add Roman numeral tier suffix correction in item_actions.py

**Anchor:** `src/autoscrapper/core/item_actions.py:50`  
**Severity:** medium  
**Category:** ocr · bug  
**Size:** S (< 20 LOC)

**Context**

Tesseract misreads Roman numeral suffixes on ALL-CAPS weapon names: `IV→1V`,
`III→111`, `II→11`, `I→1`, causing rule lookups to fail for tiered weapons.
Regex-based fixes already exist in the OCR pipeline (`inventory_vision.py:83–87`
via `_ROMAN_NUMERAL_FIXES`), but `normalize_item_name()` in `item_actions.py`
does not apply any alias correction, leaving rule lookup vulnerable when the OCR
fixes miss a case.

**Acceptance criteria**

- Add `OCR_ALIASES` dict and `_fix_roman_ocr_suffix()` in `item_actions.py`.
- Call `_fix_roman_ocr_suffix()` from `normalize_item_name()`.
- OCR-aliased names resolve correctly to the canonical item name via rule lookup.
- `pytest` passes.

**Implementation hint**

```python
OCR_ALIASES: dict[str, str] = {
    " 1v": " iv",
    " 111": " iii",
    " 11": " ii",
    " 1": " i",
}

def _fix_roman_ocr_suffix(name: str) -> str:
_ROMAN_ONLY = re.compile(r"^[ivx]+$")
    for bad, good in OCR_ALIASES.items():
        if name.endswith(bad):
            if _ROMAN_ONLY.match(good.strip()):
                return name[: -len(bad)] + good
    return name

def normalize_item_name(name: str) -> str:
    return _fix_roman_ocr_suffix(name.strip().lower())
```

---

### T013 — Filter weapon swap UI text from item name detection

**Anchor:** `src/autoscrapper/ocr/inventory_vision.py`  
**Severity:** medium  
**Category:** ocr · bug  
**Size:** S (< 20 LOC)

**Context**

Weapon infoboxes contain a "Swap with Primary Slot" UI line near the top. OCR
picks this up as the item name instead of the weapon name.

**Acceptance criteria**

- Add `_EXCLUDED_UI_KEYWORDS = frozenset(["swap with", "swap"])` in
  `inventory_vision.py`.
- Skip lines matching these keywords on the first extraction pass in
  `_extract_title_from_data`.
- On retry (`_retry_with_larger=True`), widen `top_fraction` to `0.35` to
  capture the actual name below the UI element.

---

### T014 — Remove Supabase dependency from data_update.py

**Anchor:** `src/autoscrapper/progress/data_update.py:26`  
**Severity:** medium  
**Category:** data · security  
**Size:** M (20–100 LOC)

**Context**

`data_update.py` fetches item components and recycle components from a Supabase
endpoint (`SUPABASE_URL` at line 26, `SUPABASE_ANON_KEY` at line 33,
`_fetch_supabase_all()` at lines 284–313, active usage at lines 738–749). The
hardcoded anon JWT is a committed credential and the endpoint is an external
service that may change at any time.

**Acceptance criteria**

- Use `?includeComponents=true` on the MetaForge `/items` API instead.
- Extract components inline with `_extract_component_dict()`.
- Remove `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `_fetch_supabase_all`,
  `_build_component_map` entirely.
- `python3 -m uv run ruff check src/` passes.
- Existing data snapshot can be regenerated via
  `scripts/update_snapshot_and_defaults.py` without any Supabase calls.

---

### T015 — Change default stop key from Escape to F9

**Anchor:** `src/autoscrapper/interaction/keybinds.py:5`  
**Severity:** low  
**Category:** ux  
**Size:** S (< 20 LOC)

**Context**

`DEFAULT_STOP_KEY = "escape"` conflicts with in-game Escape usage (opens game
menu). F9 is unused by Arc Raiders.

**Acceptance criteria**

- Change `DEFAULT_STOP_KEY = "f9"`.
- Add `"f9": "F9"` to `_CANONICAL_DISPLAY`.

---

### T016 — Integrate arctracker.io API for Direct Stash Sync

**Anchor:** `src/autoscrapper/api/`  
**Status:** In progress (~60% complete)  
**Severity:** medium  
**Category:** feature  
**Size:** L (100–500 LOC)

**Context**

The `src/autoscrapper/api/` package exists with `client.py`, `models.py`,
`datasource.py`, and `__init__.py`. `ApiSettings` dataclass is in `config.py`
(CONFIG_VERSION = 6). `ApiSettingsScreen` is implemented in
`tui/api_settings.py`. Remaining work is wiring the API data source into the
scan flow and adding graceful OCR fallback.

**Acceptance criteria**

1. `ArctrackerClient` has rate-limit tracking (500 req/hr), retry logic, and
   error handling.
2. TUI settings screen for API key configuration with "Test Connection" button.
3. API-based scan mode as alternative to OCR; same decision rule application.
4. Auto-sync hideout and project progress from API.
5. Graceful fallback to OCR when API fails or is rate-limited.
6. All existing OCR functionality continues to work unchanged.
7. `tests/api/test_client.py` covers rate-limit and error paths.

**Remaining files to modify**

- `src/autoscrapper/tui/scan.py` — wire API scan mode
- `src/autoscrapper/scanner/engine.py` — dispatch to API or OCR
- `src/autoscrapper/progress/progress_config.py` — auto-sync from API

---

### T017 — Fix ScanSettingsScreen missing ABC inheritance

**Anchor:** `src/autoscrapper/tui/settings.py:92`  
**Severity:** low  
**Category:** debt · refactor  
**Size:** S (< 20 LOC)

**Context**

`ScanProgress` was correctly promoted to ABC (T004 complete), but
`ScanSettingsScreen` in `tui/settings.py:92` still declares `@abstractmethod`
on `_compose_form` and `_load_into_fields` without inheriting `ABC`. The
`abstractmethod` decorator has no enforcement effect without `ABC` in the MRO,
so a caller can instantiate a concrete subclass that skips the implementation
and receive a silent runtime failure instead of a `TypeError` at class
definition time.

**Acceptance criteria**

- `ScanSettingsScreen` inherits `ABC`: `class ScanSettingsScreen(AppScreen, ABC)`.
- `from abc import ABC, abstractmethod` (already imports `abstractmethod`; add
  `ABC`).
- `basedpyright src/` reports no new errors.
- `pytest` passes.

---

### T018 — Add headless scan mode with structured JSON output

**Anchor:** `src/autoscrapper/scanner/cli.py`  
**Severity:** low  
**Category:** feature · workflow  
**Size:** M (20–100 LOC)

**Context**

The scan subcommand currently requires the TUI and writes human-readable output
only. A `--headless --output json` mode would let power users pipe results to
external tools (spreadsheets, Discord bots, overlays) without the Textual
dependency on the output path.

**Acceptance criteria**

- `autoscrapper scan --headless` runs without the Textual TUI, logging to stdout.
- `--output json` emits a JSONL stream (one object per item decision) with at
  minimum `item_name`, `decision`, `page`, `cell`, `timestamp`.
- `--output csv` writes the same fields to a file specified by `--out-file`.
- All existing `autoscrapper scan` behavior unchanged when flags are absent.
- `pytest` covers the output serialization helpers.

---

### T019 — Write per-session decision log for rule refinement

**Anchor:** `src/autoscrapper/scanner/`  
**Severity:** low  
**Category:** feature · observability  
**Size:** S (< 20 LOC)

**Context**

Currently there is no durable record of what decisions were made per session.
Users who want to tune rules after a run have no data to work from other than
memory. A lightweight append-only session log would feed the manual rule-review
workflow and complement the OCR failure corpus.

**Acceptance criteria**

- Each scan session appends a JSONL record to
  `artifacts/sessions/YYYYMMDD_HHMMSS.jsonl` (one line per item decision).
- Fields: `ts`, `item_name`, `raw_text`, `decision`, `page`, `cell`,
  `match_score`, `source` (`ocr` | `api`).
- Log path is configurable via `AppConfig`; default is opt-in (empty path →
  disabled).
- Existing scan performance is unaffected (async write or fire-and-forget).
- `README.md` documents the log format and how to enable it.

---

### T020 — Integrate ARC Safe Recycle cross-check logic

**Anchor:** `src/autoscrapper/core/item_actions.py`  
**Severity:** medium  
**Category:** feature · safety  
**Size:** M (20–100 LOC)  
**Reference:** https://github.com/thanhn062/ARC-Safe-Recycle · Ven0m0/arc-raiders-autoscrapper#41

**Context**

The scanner can recycle items needed for active quests. Integrating the
logic from ARC Safe Recycle would cross-reference each RECYCLE decision against
active quest requirements and override to KEEP when a conflict is detected.

**Acceptance criteria**

- Before emitting a RECYCLE decision, query active quest item requirements from
  the progress snapshot.
- If the item is needed, override decision to KEEP and annotate the reason
  (`quest: <quest_name>`).
- The check is skipped when the progress snapshot is absent (graceful degradation).
- `pytest` covers the override path and the graceful-degradation path.

---

### T021 — Review Raider Lens for overlay/display integration

**Anchor:** `src/autoscrapper/tui/`  
**Severity:** low  
**Category:** feature · ux  
**Size:** M (20–100 LOC)  
**Reference:** https://github.com/eli1776/raider-lens · Ven0m0/arc-raiders-autoscrapper#41

**Context**

Raider Lens provides overlay and display features that could complement the
scanner's TUI output. This task covers a review of the raider-lens codebase
followed by a lightweight prototype or design document.

**Acceptance criteria**

- Produce a written assessment of which raider-lens features are reusable
  without coupling to its OCR/capture stack.
- Prototype at least one overlay feature (e.g., item decision badge) that
  integrates with the existing Textual TUI.
- No changes to existing scan performance or OCR correctness.

---

### T022 — Verify pytest is accessible in all install paths

**Anchor:** `pyproject.toml`  
**Severity:** low  
**Category:** ci · tooling  
**Size:** S (< 20 LOC)

**Context**

`pytest>=9.0.3` is in both `[project.optional-dependencies.dev]` and
`[dependency-groups.dev]`. Setup docs (`README.md`, `scripts/setup-linux.sh`)
should reference `uv sync --group dev` so pytest is available without extra
flags.

**Acceptance criteria**

- `README.md` and both setup scripts reference `uv sync --group dev`.
- `uv run pytest` succeeds from a clean environment after following the docs.

---

## Upstream Sync Checklist

When merging from `zappybiby/ArcRaiders-AutoScrapper`, apply in order:

- [ ] **T010 / BUG-01** — Fix stale infobox rect (`scan_loop.py`)
- [x] ~~**BUG-02** — Dead code removal (`inventory_vision.py`)~~ — already removed
- [ ] **T012 / OCR-01** — Roman numeral alias correction (`item_actions.py`) — partial
- [ ] **T013 / OCR-02** — Weapon swap UI keyword filter (`inventory_vision.py`)
- [x] ~~**OCR-03** — Permissive `clean_ocr_text` regex~~ — already in fork
- [ ] **T014 / DATA-01** — Remove Supabase, use `includeComponents=true` (`data_update.py`)
- [ ] **DATA-02** — Commit fresh data snapshot + regenerated default rules
- [ ] **T015 / UX-01** — F9 as default stop key (`keybinds.py`)
- [ ] **T022 / CI-01** — Verify pytest install path in setup docs

---

## Maintenance Notes

### Data snapshot refresh

The bundled snapshot at `src/autoscrapper/progress/data/` should be regenerated
before each release:

```bash
python3 -m uv run python scripts/update_snapshot_and_defaults.py
```

Do not hand-edit snapshot files directly; see AGENTS.md for the invariant.
Current snapshot: last updated 2026-04-13T06:31:59Z (547 items, 94 quests).

---

## Status Legend

| Status | Meaning |
|--------|---------|
| `[ ]`  | Not started |
| `[~]`  | In progress |
| `[x]`  | Complete |
| `[!]`  | Blocked |

## Task Summary

| ID   | Title (short)                                  | Sev    | Size | Status | Blocked by |
|------|------------------------------------------------|--------|------|--------|------------|
| T001 | Calibrate OCR fuzzy threshold from corpus      | medium | M    | [ ]    | —          |
| T002 | Benchmark tessdata.best-eng vs fast-eng        | low    | S    | [!]    | T001       |
| T003 | Hybrid database updater (API + Wiki)           | medium | M    | [!]    | T014       |
| T010 | Fix stale infobox rect on OCR retry            | high   | S    | [ ]    | —          |
| T012 | Add Roman numeral OCR alias in item_actions    | medium | S    | [ ]    | —          |
| T013 | Filter weapon swap UI text from OCR            | medium | S    | [ ]    | —          |
| T014 | Remove Supabase dependency from data_update    | medium | M    | [ ]    | —          |
| T015 | Change default stop key to F9                  | low    | S    | [ ]    | —          |
| T016 | Integrate arctracker.io API for stash sync     | medium | L    | [~]    | —          |
| T017 | Fix ScanSettingsScreen ABC inheritance         | low    | S    | [ ]    | —          |
| T018 | Headless scan mode with JSON/CSV output        | low    | M    | [ ]    | —          |
| T019 | Per-session decision log for rule refinement   | low    | S    | [ ]    | —          |
| T020 | ARC Safe Recycle cross-check integration       | medium | M    | [ ]    | —          |
| T021 | Review Raider Lens overlay integration         | low    | M    | [ ]    | —          |
| T022 | Verify pytest accessible in all install paths  | low    | S    | [ ]    | —          |

**Recommended starting points:**
- **T010** — high-severity bug, zero external dependencies, small change.
- **T014** — security improvement, unblocks T003.
- **T017** — 2-line fix, improves type safety immediately.
