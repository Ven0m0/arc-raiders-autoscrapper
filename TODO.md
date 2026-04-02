# TODO

## OCR / Item Name Detection

- [x] Switch PSM from `SINGLE_BLOCK` to `SINGLE_LINE` in `ocr/tesseract.py`
- [x] Add Tesseract character whitelist (`ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 '-`)
- [x] Add 2× upscale (`cv2.INTER_CUBIC`) in `preprocess_for_ocr()` before grayscale conversion
- [x] Add `rapidfuzz>=3.0` dependency
- [x] Implement `match_item_name()` with WRatio fuzzy fallback in `choose_decision()` (threshold=85)
- [x] Log SKIP_UNLISTED raw OCR text in `scan_loop.py` for diagnosis
- [x] Crop `infobox_bgr` to title strip (top 22%) before `preprocess_for_ocr` in `ocr_infobox()`
- [x] Pass `top_fraction=1.0` to `_extract_title_from_data` after crop (strip is already the ROI)
- [x] Remove `sell_bbox`/`recycle_bbox` extraction from `ocr_infobox()` — verify downstream never uses these fields, then drop both `_extract_action_line_bbox` calls
- [x] Populate `_ITEM_NAMES` at startup from `rules_store` (names already in `items_rules.default.json`)
- [x] Add module-level `_last_roi_hash`/`_last_ocr_result` cache in `inventory_vision.py` — skip OCR if title strip hash matches previous call
- [x] Retry infobox color detection with wider tolerance (`tolerance_max=50`) before returning `UNREADABLE_NO_INFOBOX` — handles non-standard monitor gamma/HDR
- [ ] Tune fuzzy match threshold (currently 85) — collect SKIP_UNLISTED raw OCR texts from real runs and verify no false positives at lower thresholds

## Config

- [x] Split `except (OSError, json.JSONDecodeError)` into separate handlers with distinct log levels (`debug` vs `warning`)
- [x] Log when `_coerce_positive_int`/`_coerce_non_negative_int` silently ignores an invalid value
- [x] Add upper bounds to config fields — delays ≤ 5000ms, retry counts ≤ 10 — with validation warnings
- [x] Implement config version migration (`_migrate_vN_to_vN+1()`) — `CONFIG_VERSION` is incremented but never checked on load

## Error Handling

- [x] Log bare `except Exception` in `ocr/tesseract.py` init candidate loop
- [x] Log bare `except Exception` in `ocr/inventory_vision.py` confidence grouping and string extraction
- [x] Log `except Exception` in `scanner/engine.py` progress display failure
- [x] Log `getTitle()` and MSS `close()` failures in `interaction/ui_windows.py`
- [x] Consolidate duplicate delay constants in `scanner/actions.py` — `INPUT_ACTION_DELAY` etc. duplicate `ScanSettings` defaults; derive from `ScanSettings()` instead

## Tooling

- [x] Replace `opencv-python` with `opencv-python-headless` (no GUI code in codebase, saves ~100MB)
- [x] Replace `black` with `ruff` (lint + format); add `[tool.ruff]` config
- [x] Update `.pre-commit-config.yaml` to use `astral-sh/ruff-pre-commit` hooks
- [x] Replace `.github/workflows/black.yml` with `ruff.yml`
- [ ] Benchmark `tessdata.best-eng` vs current `tessdata.fast-eng` against known OCR failure cases — best model is ~10MB vs 4MB and may improve accuracy for unusual item abbreviations

## Rules Mismatches

- [x] Fix `fabric`: action=keep but analysis says no use — change to sell
- [x] Fix `rusted-tools`: action=keep but analysis only contains recycle math — change to sell
- [x] Fix `gas-grenade`: action=sell but analysis has Override:Keep — change to keep
- [x] Fix `blue-light-stick`: action=sell but analysis has Override:Keep — change to keep
- [x] Fix `green-light-stick`: action=sell but analysis has Override:Keep — change to keep
- [x] Fix `yellow-light-stick`: action=sell but analysis has Override:Keep — change to keep
- [ ] Confirm `stitcher-i`/`stitcher-ii` action=sell is intentional (default keeps both); fix to keep if not
- [ ] Revert `wasp-driver` from keep to recycle once quest "The Trifecta" is complete (recycle 840 > sell 640)
