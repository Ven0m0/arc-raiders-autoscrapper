# Improvement Goal

## Objective

Improve OCR accuracy and test pass rate for arc-raiders-autoscrapper.

## Target Metric

- **Metric name**: primary (pytest pass rate)
- **Target value**: 1.0
- **Direction**: higher_is_better

## Scope

- **In scope**: `src/autoscrapper/` - focus on `ocr/`, `core/item_actions.py`, `items/rules_store.py`, `scanner/`
- **Out of scope**: `tests/` (sealed), `scripts/`, generated data files (`progress/data/*`, `items_rules.default.json`)

## Milestones (optional)

M1, Target=0.90, Strategy Focus=Fix obvious test failures, quick wins
M2, Target=0.95, Strategy Focus=OCR accuracy improvements
M3, Target=1.00, Strategy Focus=All tests passing

## Experiment Ideas (optional)

- Improve fuzzy-match threshold calibration in `core/item_actions.py`
- Tune OCR preprocessing in `ocr/inventory_vision.py`
- Fix edge cases in rule resolution in `items/rules_store.py`
