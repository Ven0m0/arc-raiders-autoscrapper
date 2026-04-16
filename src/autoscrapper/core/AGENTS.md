<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-15 | Updated: 2026-04-15 -->

# core/

## Purpose
Rule lookup and fuzzy item-action decision logic. Given an OCR-detected item name, resolves the correct action (`KEEP | SELL | RECYCLE`) by consulting custom rules, then bundled defaults, with fuzzy matching to handle minor OCR variations.

## Key Files

| File | Description |
|------|-------------|
| `item_actions.py` | `resolve_action(item_name, rules)` — primary entry point. Fuzzy-matches `item_name` against loaded rules using `rapidfuzz`. Contains the shared `threshold`/`score_cutoff` constant used by both OCR matching and rule lookup. |
| `__init__.py` | Package init — no side effects. |

## For AI Agents

### Working In This Directory
- The fuzzy threshold in `item_actions.py` is **shared** with OCR matching. Changing it (T001 tag) requires running the corpus replay (`scripts/replay_ocr_failure_corpus.py`) before shipping.
- `keep`, `sell`, `recycle` are compared as **lowercase strings** in some code paths — trailing whitespace or casing in rule files causes silent fallthrough to the default action.
- Rule precedence: custom rules must win over bundled defaults. If a default is winning, the merge order in this file is inverted.

### Testing Requirements
- `tests/autoscrapper/core/test_item_actions.py`
- Run: `uv run pytest tests/autoscrapper/core/ -x -q`

### Common Patterns
- `rapidfuzz.fuzz.WRatio` is the primary scorer; `score_cutoff` is the rejection floor.
- Item names from OCR may have trailing spaces — strip before lookup.

## Dependencies

### Internal
- `src/autoscrapper/items/rules_store.py` — provides the merged rule dict passed to `resolve_action`

### External
- `rapidfuzz` — fuzzy string matching
