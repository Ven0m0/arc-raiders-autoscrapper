---
name: qlty-fix
description: Run qlty check/metrics/smells on all files, triage the output, and fix every actionable issue. Plugins covered: ruff, mypy, bandit, trufflehog, actionlint, zizmor, yamllint, biome.
---

# qlty-fix — Technical Debt Resolution

## When to use
Run at the start of any quality/debt-reduction session, or after a large merge when technical debt may have accumulated.

## Steps

### 1. Baseline capture
```bash
qlty check -a 2>&1 | tee /tmp/qlty-check.txt
qlty metrics -a 2>&1 | tee /tmp/qlty-metrics.txt
qlty smells -a 2>&1 | tee /tmp/qlty-smells.txt
```

### 2. Triage each finding into one of three buckets
- **Fix** — genuine bugs, security issues, type errors, hard complexity violations
- **Suppress** — confirmed false positives (add inline suppression with a comment explaining why)
- **Defer** — out-of-scope refactors (note in a follow-up, do NOT suppress silently)

### 3. Fix by plugin — work in this priority order

| Plugin | Action |
|--------|--------|
| `ruff` | `python3 -m uv run ruff check --fix src/ tests/` then `ruff format src/ tests/`; use `# noqa: RULE` only when auto-fix is wrong |
| `mypy` | Fix type annotations; use `# type: ignore[code]` only for unavoidable third-party gaps |
| `bandit` | Fix real security issues; mark false positives with `# nosec B<code> -- <reason>` |
| `trufflehog` | Rotate real secrets immediately; no suppressions for real secrets |
| `actionlint`/`zizmor` | Fix `.github/workflows/` — pin versions, add permissions |
| `yamllint` | Fix YAML formatting (trailing spaces, missing newlines, indentation) |
| `biome` | Fix any JS/TS files (likely none in this Python project) |
| Metrics | Reduce complexity only in files flagged over threshold; no speculative refactoring |
| Smells | Apply smells that improve clarity; skip anything that changes behavior |

### 4. Validate
```bash
qlty check -a       # must be clean
qlty metrics -a     # no files over threshold
qlty smells -a      # no actionable smells
python3 -m uv run ruff check src/ tests/
python3 -m uv run pytest
```

## Project-specific notes
- `src/autoscrapper/ocr/inventory_vision.py` is the highest-churn file — be careful when reducing complexity: do NOT move calibration constants or pixel-math helpers.
- Threshold constants (`score_cutoff`, `THRESHOLD`) are T001 — corpus replay required before shipping a new value.
- Do not hand-edit `src/autoscrapper/progress/data/*` or `items_rules.default.json`; regenerate via `scripts/update_snapshot_and_defaults.py`.
