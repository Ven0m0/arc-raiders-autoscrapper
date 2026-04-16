<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-15 | Updated: 2026-04-15 -->

# scripts/

## Purpose
Utility and setup scripts for the project — environment setup, data refresh, OCR benchmarking, and corpus management. These are developer-facing tools, not part of the application runtime.

## Key Files

| File | Description |
|------|-------------|
| `update_snapshot_and_defaults.py` | Regenerates `progress/data/*.json` and `items_rules.default.json` from live API data. **Use this instead of hand-editing generated files.** |
| `replay_ocr_failure_corpus.py` | Replays the OCR failure corpus against the current OCR pipeline. Run after changing thresholds or preprocessing logic. |
| `capture_ocr_fixture.py` | Captures a new OCR test fixture from a live game window. Used to add samples to the failure corpus. |
| `benchmark_tessdata_models.py` | Benchmarks multiple Tesseract model variants (fast/best) for accuracy vs. speed tradeoffs. |
| `setup-windows.ps1` | First-time Windows environment setup: installs Tesseract, Python, uv, and sets up the virtual environment. |
| `setup-linux.sh` | First-time Linux/WSL environment setup: equivalent of the Windows script for Linux targets. |

## For AI Agents

### Working In This Directory
- `update_snapshot_and_defaults.py` is the **only approved way** to modify `src/autoscrapper/progress/data/*` and `src/autoscrapper/items/items_rules.default.json`. Never hand-edit those files.
- Always run `--dry-run` first before a live data refresh.
- `replay_ocr_failure_corpus.py` is required after any change to OCR thresholds (`score_cutoff`) or preprocessing parameters — see the `corpus-replay` skill.

### Testing Requirements
- Script changes have tests in `tests/scripts/` (currently `test_replay_ocr_failure_corpus.py`).
- Run `uv run pytest tests/scripts/ -x -q` after modifying replay or snapshot scripts.

### Common Patterns
- Scripts use `sys.path.insert(0, str(SRC_DIR))` to import from `src/autoscrapper` without installing.
- Prefer `--dry-run` flags for any script that writes files or makes API calls.

## Dependencies

### Internal
- `src/autoscrapper/progress/data_update.py` — snapshot refresh
- `src/autoscrapper/progress/rules_generator.py` — default rule generation
- `src/autoscrapper/api/client.py` — MetaForge API access
- `src/autoscrapper/ocr/` — OCR pipeline for corpus replay and fixture capture

### External
- `uv` — Python environment management
- Tesseract — OCR engine (required for benchmark and fixture scripts)
