<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-15 | Updated: 2026-04-15 -->

# items/

## Purpose
Custom and default rule storage for item actions (`KEEP | SELL | RECYCLE`). Manages loading, merging, and diffing of rule sets. Custom rules always take precedence over bundled defaults.

## Key Files

| File | Description |
|------|-------------|
| `rules_store.py` | `RulesStore` — loads custom rules from a user-configured path, falls back to bundled defaults if missing. Merges with custom-over-default precedence. |
| `rules_diff.py` | Computes the diff between two rule sets (e.g., old defaults vs. new defaults) for display in the TUI maintenance screen. |
| `items_rules.default.json` | Bundled default rules. **Do not hand-edit** — regenerate via `scripts/update_snapshot_and_defaults.py`. |
| `items_rules.custom.json` | Example/template for user custom rules. Not committed with real user data. |
| `__init__.py` | Package init — no side effects. |

## For AI Agents

### Working In This Directory
- **Never hand-edit `items_rules.default.json`** — always use `scripts/update_snapshot_and_defaults.py`.
- Custom-over-default precedence is enforced in `rules_store.py`. If a default rule overrides a custom one, the merge order is wrong.
- Rule action values (`keep`, `sell`, `recycle`) must be lowercase strings with no trailing whitespace — see `src/autoscrapper/core/item_actions.py`.

### Testing Requirements
- `tests/autoscrapper/items/test_rules_store.py`
- Run: `uv run pytest tests/autoscrapper/items/ -x -q`

### Common Patterns
- `RulesStore.load()` is called once at scan start; it is not re-read during a scan.
- `rules_diff.py` is UI-only — it does not affect action resolution.

## Dependencies

### Internal
- `src/autoscrapper/core/item_actions.py` — consumes the merged rule dict from `RulesStore`
- `scripts/update_snapshot_and_defaults.py` — the only approved way to regenerate `items_rules.default.json`

### External
- Standard library `json` only
