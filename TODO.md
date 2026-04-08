# TODO

## OCR / Item Name Detection

### T001 — Calibrate OCR fuzzy threshold from live `SKIP_UNLISTED` data

- [ ] Current code default is 75; needs calibration from observed data.
- Severity: medium
- Acceptance criteria:
  - Capture raw OCR title strings for every `SKIP_UNLISTED` outcome during live runs.
  - Define the fuzzy threshold in one code path and apply the same value to every `match_item_name()` call site.
  - Replay the captured corpus against candidate thresholds and record the chosen match or no-match result for each sample.
  - Ship a threshold only if every captured sample either stays unmatched or resolves to the correct configured item name.
- Implementation hint: `match_item_name()` in `ocr/inventory_vision.py` is the single threshold source; use the raw title returned near line 802; emit corpus from the `SKIP_UNLISTED` branch in `scanner/actions.py`.

## Tooling

### T002 — Benchmark `tessdata.best-eng` against the OCR failure corpus (blocked by T001)

- [ ] Compare accuracy and speed of `tessdata.fast-eng` vs `tessdata.best-eng`.
- Severity: low
- Acceptance criteria:
  - Build a fixed corpus of failure-case title images with expected item names.
  - Run the same corpus with both models and record accuracy and elapsed time.
  - Keep the current package if `tessdata.best-eng` does not improve accuracy.
  - Update dependency and setup docs only if the selected model changes.
- Implementation hint: Dependency pin is in `pyproject.toml`; OCR initialization is in `ocr/tesseract.py` — only model selection input should change.
