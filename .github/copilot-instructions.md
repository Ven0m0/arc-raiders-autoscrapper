# Arc Raiders AutoScrapper
>Always use the mcp-use, language-optimization skills. Use octocode, exa, ref-tools, gh_grep mcp-servers

Canonical repo guidance lives in `AGENTS.md`.
Keep `CLAUDE.md` as a symlink to that file.

Use this file for concise repository-wide Copilot guidance only.
Detailed rules belong in `AGENTS.md`; path-specific rules belong in `.github/instructions/*.instructions.md`.

## Preferred Workflow

- Use the `mcp-use` and `language-optimization` skills by default.
- Add `ai-tuning`, `codebase-index`, `workflow-development`, or `docs-writer` when the task matches.
- Prefer MCP-first workflows and use `octocode`, `exa`, and `ref-tools` before generic shell or web searches when they fit the task.
- Make minimal, targeted edits and preserve existing conventions.

## Stack

- Python 3.13 + `uv`
- Textual TUI
- OCR: `tesserocr` + `tessdata.fast-eng`
- Vision: `opencv-python-headless`, `Pillow`, `mss`
- Matching: `rapidfuzz`
- Input: `pydirectinput-rgx` (Windows), `pynput` via `linux-input` extra (Linux)
- Serialization: `orjson`

## Commands

| Task | Command |
| --- | --- |
| Setup | `python3 -m uv sync` |
| Setup with Linux input | `python3 -m uv sync --extra linux-input` |
| Run app | `python3 -m uv run autoscrapper` |
| Safe scan | `python3 -m uv run autoscrapper scan --dry-run` |
| Lint | `python3 -m uv run ruff check src/ tests/` |
| Format | `python3 -m uv run ruff format src/ tests/ scripts/` |
| Test | `python3 -m uv run pytest` |
| Types | `python3 -m uv run mypy src/ tests/` |
| Broad checks | `python3 -m uv run prek run --all-files` |
| Refresh generated data/rules | `python3 -m uv run python scripts/update_snapshot_and_defaults.py` |
| Preview generated data/rules | `python3 -m uv run python scripts/update_snapshot_and_defaults.py --dry-run` |

## Validation

- Python changes: run Ruff + pytest.
- OCR / scanner / interaction changes: also run `python3 -m uv run autoscrapper scan --dry-run` against a live Arc Raiders window.
- Docs-only changes: verify file accuracy, links, and instruction hierarchy.
- Do not claim end-to-end validation without a live game window.
- GitHub Actions currently runs Ruff only; local pytest still matters for code changes.

## Repo-Specific Guardrails

- Preserve custom-over-default rule precedence.
- Do **not** hand-edit `src/autoscrapper/progress/data/*` or `src/autoscrapper/items/items_rules.default.json`; regenerate via `scripts/update_snapshot_and_defaults.py`.
- Do **not** hand-edit `uv.lock`; use `uv add/remove/sync` instead.
- Bump `CONFIG_VERSION` and add a migration when changing persisted config fields.
- `initialize_ocr()` must run on the main thread before scan threads start.
- Keep capture-space image coordinates separate from screen-space input coordinates.
- `inventory_vision.py` upscales OCR images 2×; any OCR bbox must be converted back to original-space coordinates before reuse. `find_action_bbox_by_ocr()` already returns original-space coords.
- Keep OCR item-name matching and rule lookup on the same fuzzy-match threshold.
- Prefer `--dry-run` before any workflow that could click in-game.
- Call out unverified behavior clearly.

## Hotspots

- `src/autoscrapper/ocr/`, `src/autoscrapper/interaction/`, and `src/autoscrapper/scanner/` are tightly coupled.
- `src/autoscrapper/ocr/inventory_vision.py` is the most calibration-sensitive file.
- `src/autoscrapper/core/item_actions.py` + `src/autoscrapper/items/rules_store.py` control item-action lookup.
- `src/autoscrapper/config.py` owns persisted config versioning.
- `src/autoscrapper/progress/` + `scripts/update_snapshot_and_defaults.py` control generated progress data and default rules.

See `AGENTS.md` for the full repository map, agent inventory, skills inventory, and detailed invariants.


## vexp context tools <!-- vexp v1.3.11 -->

**MANDATORY: use `run_pipeline` — do NOT grep, glob, or read files manually.**
vexp returns pre-indexed, graph-ranked context in a single call.

### Workflow
1. `run_pipeline` with your task description — ALWAYS FIRST (replaces all other tools)
2. Make targeted changes based on the context returned
3. `run_pipeline` again only if you need more context

### Available MCP tools
- `run_pipeline` — **PRIMARY TOOL**. Runs capsule + impact + memory in 1 call.
  Auto-detects intent. Includes file content. Example: `run_pipeline({ "task": "fix auth bug" })`
- `get_context_capsule` — lightweight, for simple questions only
- `get_impact_graph` — impact analysis of a specific symbol
- `search_logic_flow` — execution paths between functions
- `get_skeleton` — compact file structure
- `index_status` — indexing status
- `get_session_context` — recall observations from sessions
- `search_memory` — cross-session search
- `save_observation` — persist insights (prefer run_pipeline's observation param)

### Agentic search
- Do NOT use built-in file search, grep, or codebase indexing — always call `run_pipeline` first
- If you spawn sub-agents or background tasks, pass them the context from `run_pipeline`
  rather than letting them search the codebase independently

### Smart Features
Intent auto-detection, hybrid ranking, session memory, auto-expanding budget.

### Multi-Repo
`run_pipeline` auto-queries all indexed repos. Use `repos: ["alias"]` to scope. Run `index_status` to see aliases.
<!-- /vexp -->