# Arc Raiders AutoScrapper — Technical Debt & Feature Plan

Generated: 2026-04-13  
Source: TODO.md + inline `# type: ignore` / `# noqa` audit of `src/`

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
```

**Wave 1** (parallelisable): T001, T003, T004, T005, T006, T007, T008, T009  
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

`DEFAULT_ITEM_NAME_MATCH_THRESHOLD = 75` is a hand-picked constant.
`capture_skip_unlisted_sample()` in `scanner/actions.py:184-196` already emits
raw OCR strings and match metadata to disk, but no replay harness exists to
sweep candidate thresholds against that corpus.  A wrong threshold causes either
false-positive matches (item misidentified → wrong action) or excessive
`SKIP_UNLISTED` outcomes (items ignored that should be actioned).

**Acceptance criteria**

- `capture_skip_unlisted_sample()` persists at minimum `raw_text`,
  `chosen_name`, `matched_name`, and the image path to a JSON-lines file per
  session.
- A replay script accepts a corpus directory and a list of integer candidate
  thresholds; it outputs per-threshold accuracy metrics (match rate,
  false-positive count).
- `DEFAULT_ITEM_NAME_MATCH_THRESHOLD` changes only after replay confirms every
  existing corpus sample either stays unmatched or resolves to the correct item
  name.
- The chosen value is documented with the corpus commit hash in a comment
  adjacent to the constant definition at `inventory_vision.py:47`.
- `match_item_name_result()` continues to accept an explicit `threshold`
  override; any caller that hard-codes a different value is updated to use the
  constant.

**Implementation hint**

Emit corpus from `scanner/actions.py:184` (`capture_skip_unlisted_sample()`) to
a JSONL file under `ocr_debug/`.  Add `scripts/replay_threshold.py` that calls
`match_item_name_result(raw, threshold=t)` for each candidate `t` and computes
accuracy.  Single source-of-truth constant: `ocr/inventory_vision.py:47`.

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

`ocr/tesseract.py` initialises the API; swap the `dataPath` arg to point at the
`best-eng` data directory.  Benchmark via the replay script from T001 with an
extra `--model` flag.

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
imports.  Ruff F401 is satisfied by the explicit `as Name` form, so the noqa
becomes redundant once `__all__` is present.

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
| T003 | Add ARLO web-scraper data-update path      | medium | M    | —          |
| T004 | Promote ScanProgress/ScanSettingsScreen ABC| medium | S    | —          |
| T005 | LiveWindow Protocol for isAlive access     | low    | S    | —          |
| T006 | Add opencv-stubs dev dependency            | low    | S    | —          |
| T007 | Fix on_screen_resume signature             | low    | S    | —          |
| T008 | Narrow bare-Exception in MaintenanceScreen | medium | S    | —          |
| T009 | Add __all__ to rich_support.py             | low    | S    | —          |

**Recommended starting point:** T004 — zero external dependencies, fully
validatable with `basedpyright + pytest`, no game window required.
