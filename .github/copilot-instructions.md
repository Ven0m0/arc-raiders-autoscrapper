# Arc Raiders AutoScrapper

Canonical repo guidance lives in `AGENTS.md`. Keep `CLAUDE.md` as a
symlink to that file.

## Start here

- Read `AGENTS.md` first for the repo map, invariants, and validation rules.
- Use `mcp-use` and `language-optimization` by default; add
  `codebase-index`, `workflow-development`, `docs-writer`, or `update-data`
  when the task matches.
- Prefer MCP tools such as `octocode`, `exa`, `ref-tools`, and `gh_grep`
  before broad shell or web searches.
- Keep edits minimal and avoid duplicating large rule blocks outside
  `AGENTS.md`.

## Working norms

- Runtime: Python 3.13 with `uv`; prefer `python3 -m uv ...` in automation.
- Validate Python changes with `python3 -m uv run ruff check src/ tests/
  scripts/`, `python3 -m uv run basedpyright src/`, and
  `python3 -m uv run pytest`.
- Validate workflow changes with `python3 -m uv run prek run --files
  .github/workflows/<name>.yml`.
- For docs and agent-guidance changes, verify paths, links, commands, and the
  instruction hierarchy.

## Repo guardrails

- Do not hand-edit `src/autoscrapper/progress/data/*` or
  `src/autoscrapper/items/items_rules.default.json`; regenerate via
  `scripts/update_snapshot_and_defaults.py`.
- Bump `CONFIG_VERSION` and add a migration when persisted config fields
  change.
- `initialize_ocr()` must run on the main thread before scan threads start.
- Keep capture-space image coordinates separate from screen-space input
  coordinates.
- Keep the OCR item-name fuzzy-match threshold aligned with rule lookup.

## Hotspots

- `src/autoscrapper/ocr/`, `src/autoscrapper/interaction/`, and
  `src/autoscrapper/scanner/` are tightly coupled.
- `src/autoscrapper/ocr/inventory_vision.py` is the most calibration-sensitive
  file.
- `src/autoscrapper/core/item_actions.py`,
  `src/autoscrapper/items/rules_store.py`, and `src/autoscrapper/config.py`
  control core scan behavior and persisted config.
