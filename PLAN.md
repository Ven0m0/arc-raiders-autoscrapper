# Arc Raiders AutoScrapper — Technical Debt & Feature Plan

Generated: 2026-04-13  
Source: TODO.md + inline `# type: ignore` / `# noqa` audit of `src/` + arctracker.io API integration

---

## Dependency Graph

```
T001 ──► T002

T003  (independent)
T004  (independent)
T005  (independent)
T006  (independent)
T007  (independent)
T008  (independent)
T009  (independent)
T010  (independent)
T011  (independent)
T012  (independent)
T013  (independent)
T014  (independent)
T015  (independent)
```

**Wave 1** (parallelisable): T001, T003, T004, T005, T006, T007, T008, T009, T010, T011, T012, T013, T014, T015  
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
`/home/runner/work/arc-raiders-autoscrapper/arc-raiders-autoscrapper/scripts/replay_ocr_failure_corpus.py`
can sweep candidate thresholds and write reports. The remaining gap is to use
that existing corpus/replay path to validate the default threshold, confirm the
captured fields and reported metrics are sufficient for decision-making, and
extend the tooling only if the current output is missing data needed to judge
false positives versus `SKIP_UNLISTED` outcomes (items ignored that should be
actioned).

**Acceptance criteria**

- `capture_skip_unlisted_sample()` continues to persist the fields needed for
  replay-based calibration, including at minimum `raw_text`, `chosen_name`,
  `matched_name`, and the image path in the JSON-lines corpus.
- `/home/runner/work/arc-raiders-autoscrapper/arc-raiders-autoscrapper/scripts/replay_ocr_failure_corpus.py`
  is used as the primary replay harness; if it lacks any required metric or
  input option, T001 scopes the minimal extension instead of introducing a
  duplicate script.
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

Extend `scanner/actions.py:184` (`capture_skip_unlisted_sample()`) via the
existing corpus output at `artifacts/ocr/skip_unlisted/samples.jsonl` rather
than introducing a new `ocr_debug/` sink. Reuse
`/home/runner/work/arc-raiders-autoscrapper/arc-raiders-autoscrapper/scripts/replay_ocr_failure_corpus.py`
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

The project pins `tessdata.fast-eng` for speed.  `tessdata.best-eng` may
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

Start with `/home/runner/work/arc-raiders-autoscrapper/arc-raiders-autoscrapper/scripts/benchmark_tessdata_models.py`,
which already benchmarks `tessdata.fast-eng` vs `tessdata.best-eng` by
switching `TESSDATA_PREFIX` and writing a report. Use the corpus produced by
T001 as input to that script if needed. Only add a replay-script `--model` flag
or change `ocr/tesseract.py` directly if the existing benchmark script proves
insufficient; if so, document the specific gap before extending the tooling.

---

### T003 — Implement hybrid database updater from MetaForge API + Arc Raiders Wiki

**Anchor:** `TODO.md:3` (GitHub issue #41)  
**Severity:** medium  
**Category:** feature  
**Size:** M (20–100 LOC)

**Context**

GitHub issue #41 points at ARLO's `update_db.py`, which uses a hybrid updater:
MetaForge API data for items, sell prices, stack sizes, recycle components, and
quests, then Arc Raiders Wiki scraping for workshop upgrades, expedition
requirements, and project-use enrichment.  This repo already has an updater in
`src/autoscrapper/progress/data_update.py` and
`scripts/update_snapshot_and_defaults.py` that merges MetaForge with the
RaidTheory fallback; the missing piece is an optional wiki-enrichment phase that
improves item-usage coverage without replacing the current primary/fallback
pipeline.

**Acceptance criteria**

- Add `requests` and `beautifulsoup4` as optional extras in `pyproject.toml`
  (e.g. `[project.optional-dependencies] scraper = [...]`).
- Extend the existing maintenance update flow (not the live scan path) with a
  hybrid-source mode patterned after ARLO's `update_db.py`.
- MetaForge remains the primary source for items, sell prices, stack sizes,
  recycle components, and quest requirements/rewards.
- Arc Raiders Wiki scraping enriches the update output with normalized workshop
  upgrades, expedition requirements, and project-use data keyed by canonical
  item names.
- The current MetaForge + RaidTheory fallback behavior remains intact when the
  wiki scrape is unavailable or incomplete.
- A dry-run entrypoint exits 0 and reports item/source coverage without writing
  tracked files.
- `metadata.json` (or a sibling report artifact) records which fields came from
  MetaForge, RaidTheory fallback, and wiki enrichment.
- `README.md` documents the new extra, data sources, and dry-run workflow.

**Implementation hint**

Start from `/home/runner/work/arc-raiders-autoscrapper/arc-raiders-autoscrapper/src/autoscrapper/progress/data_update.py`
and `/home/runner/work/arc-raiders-autoscrapper/arc-raiders-autoscrapper/scripts/update_snapshot_and_defaults.py`
so the repo keeps one canonical updater.  Reuse ARLO's split of concerns:
`requests.get(..., timeout=30)` for MetaForge/Wiki fetches,
`BeautifulSoup(html, "html.parser")` for wiki parsing, and a name-based merge
step that enriches the existing item snapshot with workshop / expedition /
project-use fields instead of creating a parallel JSON pipeline.

---

### T004 — Promote ScanProgress and ScanSettingsScreen to formal ABCs

**Anchor:** `src/autoscrapper/scanner/progress.py:7`  
**Severity:** medium  
**Category:** refactor · debt  
**Size:** S (< 20 LOC)

**Context**

`ScanProgress` (`scanner/progress.py:7`) and `ScanSettingsScreen._compose_form`
/ `_load_into_fields` (`tui/settings.py:254-258`) both use bare
`raise NotImplementedError` without `ABC` + `@abstractmethod`.  A caller can
instantiate `ScanProgress()` directly and receive a runtime crash instead of an
import-time type error.  `basedpyright` cannot enforce the contract either.

**Acceptance criteria**

- `ScanProgress` inherits `abc.ABC`; all ten methods carry `@abstractmethod`.
- `ScanSettingsScreen._compose_form` and `_load_into_fields` carry
  `@abstractmethod`; `ScanSettingsScreen` inherits `abc.ABC`.
- `NullScanProgress` and `RichScanProgress` retain all concrete implementations;
  no runtime behaviour changes.
- `python3 -m uv run basedpyright src/` reports no new errors after the change.
- `python3 -m uv run pytest` passes.

**Implementation hint**

```python
from abc import ABC, abstractmethod

class ScanProgress(ABC): ...
class ScanSettingsScreen(Screen, ABC): ...
```

Textual does not block ABC co-inheritance with `Screen`.

---

### T005 — Replace isAlive type: ignore with a typed LiveWindow protocol

**Anchor:** `src/autoscrapper/scanner/scan_loop.py:483`  
**Severity:** low  
**Category:** debt · refactor  
**Size:** S (< 20 LOC)

**Context**

`scan_loop.py:483` suppresses `attr-defined` because `pywinctl` has no type
stubs and `isAlive` is accessed without a typed protocol.  The existing
`hasattr` guard already prevents `AttributeError`; the suppression is the only
code smell.

**Acceptance criteria**

- Define `class LiveWindow(Protocol): isAlive: bool` in
  `interaction/ui_windows.py`.
- Annotate the `window` field on `ScanContext` (or its definition site) as
  `LiveWindow | None`.
- Remove `# type: ignore[attr-defined]` from `scan_loop.py:483`.
- `basedpyright src/` reports no new errors.

**Implementation hint**

Use `typing.Protocol`.  Do not add `@runtime_checkable` unless `isinstance`
checks are introduced elsewhere.

---

### T006 — Add cv2 type stubs so inventory_grid.py drops its type: ignore

**Anchor:** `src/autoscrapper/interaction/inventory_grid.py:13`  
**Severity:** low  
**Category:** debt  
**Size:** S (< 20 LOC)

**Context**

`import cv2  # type: ignore` suppresses the missing-stubs error for
`opencv-python-headless`.  The `opencv-stubs` package on PyPI provides partial
stubs covering the functions used in `inventory_grid.py`.

**Acceptance criteria**

- Add `opencv-stubs` as a dev dependency via `uv add --dev opencv-stubs`.
- Remove `# type: ignore` from `inventory_grid.py:13`.
- `basedpyright src/` shows no new errors for `inventory_grid.py`.
- `python3 -m uv run pytest` continues to pass.

**Implementation hint**

`python3 -m uv add --dev opencv-stubs`.  Stubs cover `cv2.threshold`,
`cv2.findContours`, `cv2.THRESH_*` constants used in this file.  Check stubs
coverage for `inventory_vision.py` (heavier cv2 usage) before removing that
file's ignores.

---

### T007 — Fix on_screen_resume signature to match Textual Screen override contract

**Anchor:** `src/autoscrapper/tui/scan.py:197`  
**Severity:** low  
**Category:** debt · refactor  
**Size:** S (< 20 LOC)

**Context**

`on_screen_resume(self, _event)` carries `# type: ignore[override]` because the
`Screen.on_screen_resume` handler in the pinned Textual version does not accept
an event parameter.  Textual routes handlers without an event arg if the method
signature omits it.

**Acceptance criteria**

- Change signature to `def on_screen_resume(self) -> None:`.
- Remove `# type: ignore[override]`.
- `basedpyright src/` reports no new errors for `scan.py`.
- Manual or automated test confirms the screen auto-pops when scan completes.

**Implementation hint**

Confirm correct signature against the installed Textual version in
`pyproject.toml` before changing.  Textual message dispatch uses introspection;
removing `_event` is safe.

---

### T008 — Narrow bare-Exception catch in MaintenanceScreen._run_update

**Anchor:** `src/autoscrapper/tui/maintenance.py:42`  
**Severity:** medium  
**Category:** debt · error-handling  
**Size:** S (< 20 LOC)

**Context**

`except Exception as exc:  # noqa: BLE001` at `maintenance.py:42` masks
`KeyboardInterrupt`, `SystemExit`, and other non-error base exceptions.  The
callee `update_data_snapshot()` failure modes are network errors, JSON parse
errors, and file-write errors — all catchable specifically.

**Acceptance criteria**

- Identify all exception types raised by `update_data_snapshot()` and its
  callees.
- Replace `except Exception` with an explicit union (e.g.
  `except (OSError, ValueError, httpx.HTTPError)`).
- Remove `# noqa: BLE001`.
- `python3 -m uv run ruff check src/` passes without the suppression.
- Existing pytest tests for the maintenance screen continue to pass.

**Implementation hint**

Trace the `update_data_snapshot()` call graph in `progress/` to enumerate
raises.  Combine types into a single `except (TypeA, TypeB, TypeC)` clause.

---

### T009 — Convert rich_support.py re-export imports to __all__ declaration

**Anchor:** `src/autoscrapper/scanner/rich_support.py:21`  
**Severity:** low  
**Category:** debt · docs  
**Size:** S (< 20 LOC)

**Context**

`from rich.text import Text as Text  # noqa: F401` marks `Text` as a public
re-export via the `as Name` trick but requires a noqa suppression and is
inconsistent with other symbols in the file.  Downstream importers cannot
discover the module's public API without reading every import.

**Acceptance criteria**

- Add `__all__: list[str]` at module level listing every symbol this module
  intends to export.
- Remove `# noqa: F401` from the `Text` import line.
- Keep all existing `from rich.X import Y as Y` patterns (required by
  type-checkers for re-export recognition).
- `python3 -m uv run ruff check src/` passes without suppressions in this file.

**Implementation hint**

Add `__all__ = ["Align", "Console", "Group", ..., "Text"]` after the try/except
imports. In this repo, the explicit `as Name` form alone does not satisfy Ruff
F401 for `Text`; the `# noqa: F401` becomes redundant only once `Text` is
included in `__all__` (or otherwise referenced) as a deliberate re-export.

---

### T010 — Fix stale infobox rect causing wrong OCR crops at session end

**Anchor:** `src/autoscrapper/scanner/scan_loop.py`  
**Severity:** high  
**Category:** bug  
**Size:** S (< 20 LOC)

**Context**

OCR retry passes in `_ScanRunner._ocr_infobox_with_retries` reuse the
previously-detected infobox rect without re-detecting. When the context menu
closed between attempts, the scanner cropped the "TAB | CLOSE" button bar at
screen bottom, producing empty or garbage item names.

**Acceptance criteria**

- On retry (`ocr_attempt > 0`), re-capture the full window and call
  `find_infobox()` to get a fresh rect.
- Break early if detection returns `None` (menu closed).
- `ocr_debug/` crops no longer contain "TAB CLOSE" text on retry attempts.

---

### T011 — Remove dead code block in `_extract_title_from_data`

**Anchor:** `src/autoscrapper/ocr/inventory_vision.py:720–740`  
**Severity:** low  
**Category:** debt · cleanup  
**Size:** S (< 20 LOC)

**Context**

Duplicate function body (including a `_group_score` re-definition) after a
`return` statement — unreachable and misleading.

**Acceptance criteria**

- Delete lines 720–740 entirely.
- `python3 -m uv run ruff check src/` passes.

---

### T012 — Add Roman numeral tier suffix correction for OCR misreads

**Anchor:** `src/autoscrapper/core/item_actions.py`  
**Severity:** medium  
**Category:** ocr · bug  
**Size:** S (< 20 LOC)

**Context**

Tesseract misreads Roman numeral suffixes on ALL-CAPS weapon names: `IV→1V`,
`III→111`, `II→11`, `I→1`. This causes rule lookups to fail for tiered weapons.

**Acceptance criteria**

- Add `OCR_ALIASES` dict and `_fix_roman_ocr_suffix()` function called from
  `normalize_item_name()`.
- OCR-aliased names resolve correctly to the canonical item name.

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

- Skip lines matching UI keywords (`swap with`, `swap`) on first pass.
- On retry (`_retry_with_larger=True`), widen `top_fraction` to `0.35` to
  capture the actual name below the UI element.

---

### T014 — Remove Supabase dependency from data_update.py

**Anchor:** `src/autoscrapper/progress/data_update.py`  
**Severity:** medium  
**Category:** data · security  
**Size:** M (20–100 LOC)

**Context**

Upstream fetches item components and recycle components from a Supabase endpoint
using a hardcoded anon JWT. This creates a dependency on an external service that
may change, and the hardcoded JWT is a credential that should never be committed.

**Acceptance criteria**

- Use `?includeComponents=true` on the MetaForge `/items` API instead.
- Extract components inline from the response using `_extract_component_dict()`.
- Remove all Supabase code (`SUPABASE_URL`, `SUPABASE_ANON_KEY`,
  `_fetch_supabase_all`, `_build_component_map`).
- `python3 -m uv run ruff check src/` passes.

---

### T015 — Change default stop key from Escape to F9

**Anchor:** `src/autoscrapper/interaction/keybinds.py`  
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

**Anchor:** `PLAN2.md`  
**Severity:** medium  
**Category:** feature  
**Size:** L (100–500 LOC)

**Context**

Implement arctracker.io API integration to fetch user stash, hideout, and
projects data directly, bypassing OCR and guaranteeing accurate data.

**Authentication:** Dual-key system
- App Key (`arc_k1_...`): Registered via Developer Dashboard
- User Key (`arc_u1_...`): Created by users in Settings > Developer Access

**Public endpoints** (no auth required): `/api/items`, `/api/quests`, `/api/hideout`, `/api/projects`  
**User endpoints** (require both keys): `/api/v2/user/stash`, `/api/v2/user/hideout`, `/api/v2/user/projects`  
**Rate limits:** 500 requests/hour per app

**Acceptance criteria**

1. `ArctrackerSettings` dataclass in `config.py` with `app_key`, `user_key`,
   `enable_sync`, `auto_fetch_on_scan`. Bump `CONFIG_VERSION` to 6.
2. `src/autoscrapper/api/` package with `client.py`, `models.py`, `datasource.py`.
3. `ArctrackerClient` with rate limit tracking, retry logic, and error handling.
4. TUI settings screen for API key configuration with "Test Connection" button.
5. API-based scan mode as alternative to OCR; same decision rule application.
6. Auto-sync hideout and project progress from API.
7. Graceful fallback to OCR when API fails or rate limited.
8. All existing OCR functionality continues to work unchanged.

**Files to create:**
- `src/autoscrapper/api/__init__.py`
- `src/autoscrapper/api/client.py`
- `src/autoscrapper/api/models.py`
- `src/autoscrapper/api/datasource.py`
- `tests/api/test_client.py`

**Files to modify:**
- `src/autoscrapper/config.py`
- `src/autoscrapper/tui/settings.py`
- `src/autoscrapper/tui/app.py`
- `src/autoscrapper/tui/scan.py`
- `src/autoscrapper/scanner/engine.py`
- `src/autoscrapper/progress/progress_config.py`
- `pyproject.toml`

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
| T003 | Hybrid database updater (API + Wiki)      | medium | M    | —          |
| T004 | Promote ScanProgress/ScanSettingsScreen ABC| medium | S    | —          |
| T005 | LiveWindow Protocol for isAlive access     | low    | S    | —          |
| T006 | Add opencv-stubs dev dependency            | low    | S    | —          |
| T007 | Fix on_screen_resume signature             | low    | S    | —          |
| T008 | Narrow bare-Exception in MaintenanceScreen | medium | S    | —          |
| T009 | Add __all__ to rich_support.py             | low    | S    | —          |
| T010 | Fix stale infobox rect on OCR retry       | high   | S    | —          |
| T011 | Remove dead code in _extract_title_from_data| low    | S    | —          |
| T012 | Add Roman numeral OCR alias correction     | medium | S    | —          |
| T013 | Filter weapon swap UI text from OCR        | medium | S    | —          |
| T014 | Remove Supabase dependency from data_update| medium | M    | —          |
| T015 | Change default stop key to F9              | low    | S    | —          |
| T016 | Integrate arctracker.io API for stash sync | medium | L    | —          |

**Recommended starting point:** T004 — zero external dependencies, fully
validatable with `basedpyright + pytest`, no game window required.
