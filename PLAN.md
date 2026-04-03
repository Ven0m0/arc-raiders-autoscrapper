# PLAN

## Prioritized Task Graph

Topological order: `T001 -> T002`

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
