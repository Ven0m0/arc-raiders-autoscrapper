<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-15 | Updated: 2026-04-15 -->

# tests/scripts/

## Purpose
Tests for developer scripts in `scripts/`. Currently focused on the OCR failure corpus replay script.

## Key Files

| File | Description |
|------|-------------|
| `test_replay_ocr_failure_corpus.py` | Tests for `scripts/replay_ocr_failure_corpus.py`: report structure, `captured_cleaned_text` field presence, fake match helper, no-match case. |

## For AI Agents

### Working In This Directory
- Test fixtures must include all required fields for the current `OcrFailureSample` schema (version 2: `captured_cleaned_text`).
- When adding new fields to the replay report output, add corresponding assertions here.

### Testing Requirements
Run: `uv run pytest tests/scripts/ -x -q`
