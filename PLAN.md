# PLAN

## Prioritized Task Graph

Topological order: `T001 -> T002 -> T004 -> T003`

## Tasks

### T001 — Calibrate OCR fuzzy threshold from live `SKIP_UNLISTED` data
- Anchor: `/home/runner/work/arc-raiders-autoscrapper/arc-raiders-autoscrapper/src/autoscrapper/ocr/inventory_vision.py:574`
- Severity: medium
- Category: bug
- Estimated LOC: M
- Blocking IDs: none
- Acceptance criteria:
  - Capture raw OCR title strings for every `SKIP_UNLISTED` outcome during live runs.
  - Define the fuzzy threshold in one code path and apply the same value to every `match_item_name()` call site.
  - Replay the captured corpus against candidate thresholds and record the chosen match or no-match result for each sample.
  - Ship a threshold only if every captured sample either stays unmatched or resolves to the correct configured item name.
- Implementation hint: Use `match_item_name()` in `inventory_vision.py:574` as the single threshold source, use the raw title returned near `inventory_vision.py:802`, and use the `SKIP_UNLISTED` branch in `scanner/actions.py:167` to emit the corpus.

### T002 — Benchmark `tessdata.best-eng` against the OCR failure corpus
- Anchor: `/home/runner/work/arc-raiders-autoscrapper/arc-raiders-autoscrapper/pyproject.toml:22`
- Severity: low
- Category: performance
- Estimated LOC: M
- Blocking IDs: `T001`
- Acceptance criteria:
  - Build a fixed corpus of failure-case title images with expected item names.
  - Run the same corpus with `tessdata.fast-eng` and `tessdata.best-eng` and record accuracy and elapsed time.
  - Keep the current package if `tessdata.best-eng` does not improve accuracy on the corpus.
  - Update dependency and setup documentation only if the selected model changes.
- Implementation hint: Compare the dependency at `pyproject.toml:22`; keep OCR initialization in `ocr/tesseract.py` unchanged except for model selection input.

### T004 — Route `wasp-driver` to recycle after `The Trifecta`
- Anchor: `/home/runner/work/arc-raiders-autoscrapper/arc-raiders-autoscrapper/src/autoscrapper/progress/rules_generator.py:19`
- Severity: medium
- Category: bug
- Estimated LOC: M
- Blocking IDs: none
- Acceptance criteria:
  - Verify that source snapshot data for `wasp-driver` contains recycle outputs before applying a recycle-value rule.
  - Keep `wasp-driver` while any incomplete quest still requires `item_id` `wasp-driver`.
  - After `the-trifecta` is completed, emit `recycle` when recycle output value exceeds sale value.
  - Do not let the generic rare-item keep path override a profitable recycle result.
- Implementation hint: Adjust the interaction between `DecisionEngine.finalize_decision()` in `decision_engine.py`, quest gating in `decision_engine.py:is_used_in_active_quests()`, and `_to_action()` in `rules_generator.py`; regenerate defaults via `scripts/update_snapshot_and_defaults.py`.

### T003 — Reconcile `stitcher-i` and `stitcher-ii` default rule intent
- Anchor: `/home/runner/work/arc-raiders-autoscrapper/arc-raiders-autoscrapper/src/autoscrapper/progress/decision_engine.py:131`
- Severity: low
- Category: debt
- Estimated LOC: S
- Blocking IDs: none
- Acceptance criteria:
  - Confirm the intended default action for `stitcher-i` and `stitcher-ii` from the repository's rule-generation policy or authoritative rule source.
  - If the intended action is keep, close the stale TODO and leave generated defaults unchanged.
  - If the intended action is sell, add explicit rule logic so both items serialize as `sell` in generated defaults.
  - Preserve custom-rule precedence over generated defaults.
- Implementation hint: Inspect the weapon branch in `DecisionEngine.get_decision()` at `decision_engine.py:131`; apply any explicit override before `generate_rules_from_active()` writes `items_rules.default.json`; regenerate with `scripts/update_snapshot_and_defaults.py`.
