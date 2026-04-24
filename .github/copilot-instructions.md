Arc Raiders AutoScrapper uses Python 3.13, `uv`, Textual, Tesseract OCR, OpenCV, screen capture, and optional desktop input automation.

## Rule

Use this file for startup guidance only. Keep detailed repo rules in `AGENTS.md`, and path-specific instructions in `.github/instructions/*.instructions.md`.

- Keep `CLAUDE.md` as a symlink to `AGENTS.md`.
- Prefer MCP tools and repo skills before broad shell or web searches.
- Keep edits minimal, targeted, and repo-specific.
- Do not hand-edit generated progress data or `src/autoscrapper/items/items_rules.default.json`.

## Core Commands

| Command | Purpose |
|---------|---------|
| `python3 -m uv sync` | Install dependencies |
| `python3 -m uv sync --extra linux-input` | Install Linux input extra |
| `python3 -m uv run ruff check src/ tests/ scripts/` | Lint Python |
| `python3 -m uv run ruff format src/ tests/ scripts/` | Format Python |
| `python3 -m uv run basedpyright src/` | Type-check Python |
| `python3 -m uv run pytest` | Run tests |
| `python3 -m uv run autoscrapper` | Launch TUI |
| `python3 -m uv run autoscrapper scan --dry-run` | Safe dry-run scan |

## High-Risk Invariants

Treat these as non-negotiable when editing OCR, scanner, interaction, rules, or config:

- `initialize_ocr()` must run on the **main thread** before scan threads start.
- Keep capture-space image coordinates separate from screen-space input coordinates.
- Keep OCR fuzzy matching aligned with rule lookup thresholds (shared threshold).
- Bump `CONFIG_VERSION` and add a migration when persisted config fields change.
- Convert OCR boxes back to original-space coordinates before reuse (2× upscale).

## Preferred Repo Skills

Use these first when they match the task:
`mcp-use`, `language-optimization`, `codebase-index`, `workflow-development`, `docs-writer`, `update-data`, `validate`, `lint-and-validate`, `copilot-init`.