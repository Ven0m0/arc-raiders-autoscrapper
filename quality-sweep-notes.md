# Quality Sweep Notes (2026-04-12)

## Summary

| Category | Changes |
| --- | --- |
| Lint auto-fix | 0 (no violations found) |
| Format | 6 files reformatted |
| Unused imports | 0 (none found) |
| Dead code | 0 (none found) |

## Pre-existing Test Failures

The test suite has 2 pre-existing failures unrelated to this quality sweep:

1. `tests/autoscrapper/ocr/test_failure_corpus.py::test_resolve_image_path_traversal`
   - Error: `TypeError: OcrFailureSample.__init__() missing 1 required positional argument: 'schema_version'`
   - Root cause: test fixture missing schema_version field

2. `tests/scripts/test_replay_ocr_failure_corpus.py::test_evaluate_threshold_records_expected_status_and_correctness`
   - Error: field mismatch - result includes `captured_cleaned_text` but expected does not
   - Root cause: test expectation dict missing field

These failures existed before this sweep and are not caused by any changes made.