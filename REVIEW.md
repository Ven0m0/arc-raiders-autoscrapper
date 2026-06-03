# PR Review Guide

This document describes the review conventions, severity levels, dispatch matrix, and hotspot invariants for this repository.

## Severity Levels

| Level | Label | Meaning |
|-------|-------|---------|
| **P0** | `critical` | Data loss, security vulnerability, or broken public API. Blocks merge. |
| **P1** | `major` | Correctness bug, missing None-guard, broken test. Must be resolved or explicitly deferred. |
| **P2** | `minor` | Performance regression, code smell, missing edge-case test. Should be resolved. |
| **P3** | `nit` | Style, naming, comment wording. Optional; author may decline. |

## Dispatch Matrix

| Changed path | Required reviewers |
|---|---|
| `src/autoscrapper/api/` | api-reviewer |
| `src/autoscrapper/ocr/`, `src/autoscrapper/scanner/` | ocr-reviewer, scan-validator |
| `src/autoscrapper/tui/` | tui-reviewer |
| `src/autoscrapper/progress/` | progress-reviewer |
| `src/autoscrapper/config.py` | config-reviewer |
| `.github/workflows/` | security-reviewer |
| `tests/` | test-generator (advisory) |

## Hotspot Invariants

### `api/client.py`
- `_rate_limit_lock` must guard all reads/writes to `rate_limit.is_rate_limited` and `rate_limit.seconds_until_reset`.
- Auth headers (`X-App-Key`, `Authorization`) must be injected directly in `_make_request`; never use a custom `httpx.Auth` subclass.
- Dead API methods (`get_user_rounds`, `get_user_loadout`, `get_user_blueprints`, `get_public_*`) must not be reintroduced.

### `api/models.py`
- `RoundEntry` and `Blueprint` are removed. Do not re-add them.
- `RateLimitState.is_rate_limited` and `seconds_until_reset` are properties; callers must not cache their return values across lock boundaries.

### `scanner/scan_loop.py`
- Decision log directory must use `tempfile.mkdtemp(prefix="autoscrapper_decisions_")` — never a predictable path.
- `_close_decision_log` must remove the temp directory via `shutil.rmtree`.

### `progress/update_report.py`
- `graph_gap_report` is called by `scripts/update_snapshot_and_defaults.py` at two call-sites. Do not remove or rename it.

### `tui/rules.py`
- `_filter_indices(query, search_data)` takes exactly two positional arguments. The old three-argument form is removed.

## Commit and Branch Policy

- Feature branches: `feature/<slug>`
- Bot/automation branches: `bot/<slug>`
- Consolidated review branches: `claude/<slug>`
- Squash-merge to `main`; no merge commits on `main`.
- All generated data files (`src/autoscrapper/progress/data/*.json`) are updated exclusively by the `daily-data-update` workflow.
