# Arc Raiders AutoScrapper
>Always use the mcp-use, language-optimization, codebase-index, lint-and-validate skills. Use octocode, exa, ref-tools, gh_grep mcp-servers, github_mcp_server, fast-filesystem mcp-servers. Canonical repo guidance lives in `AGENTS.md`.
Keep `CLAUDE.md` as a symlink to that file.

Use this file for short repo-wide Copilot startup guidance only.
Put detailed rules in `AGENTS.md`; keep path-specific rules in `.github/instructions/*.instructions.md`.

## Default Workflow

- Use the `mcp-use` and `language-optimization` skills by default.
- Add `copilot-init`, `codebase-index`, `workflow-development`, or `docs-writer` only when the task matches.
- Prefer MCP-first workflows: `octocode`, `exa`, `ref-tools`, `gh_grep`.
- Make minimal, targeted edits and preserve existing conventions.

## Stack Snapshot

- Python `3.13.x` only + `uv`
- Textual TUI
- OCR: `tesserocr` + `tessdata.fast-eng`
- Vision: `opencv-python-headless`, `Pillow`, `mss`
- Matching: `rapidfuzz`
- Input: `pydirectinput-rgx` (Windows), `pynput` via `linux-input` extra (Linux)
- Serialization: `orjson`

## Guardrails

- Keep Python version changes pinned to `3.13.x`; do **not** move to Python `3.14+` until the remaining Windows `tesserocr`/tooling migration work is resolved.
- Keep `AGENTS.md` as the canonical repo guide; do not duplicate large rule sets here.
- Do **not** hand-edit generated progress data or `src/autoscrapper/items/items_rules.default.json`; use `scripts/update_snapshot_and_defaults.py`.
- Do **not** hand-edit `uv.lock`; use `uv add/remove/sync`.
- Bump `CONFIG_VERSION` and add a migration when persisted config fields change.
- `initialize_ocr()` must run on the main thread before scan threads start.
- Keep capture-space image coordinates separate from screen-space input coordinates.
- Keep OCR matching and rule lookup on the same fuzzy-match threshold.
- Prefer `--dry-run` before anything that could click in-game.
- Call out unverified behavior clearly.

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
| Types | `python3 -m uv run basedpyright src/` |
| Broad checks | `python3 -m uv run prek run --all-files` |

## Validation

- Python changes: run Ruff + pytest.
- OCR / scanner / interaction changes: also run `python3 -m uv run autoscrapper scan --dry-run` against a live Arc Raiders window.
- Workflow changes: run `python3 -m uv run prek run --files .github/workflows/<name>.yml`.
- Docs-only changes: verify file accuracy, links, hierarchy, and referenced commands.
- Do not claim end-to-end validation without a live game window.

See `AGENTS.md` for repository map, hotspots, and full invariants.
