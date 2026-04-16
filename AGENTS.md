# AGENTS.md

Canonical agent guide for this repository. `CLAUDE.md` is a symlink to this file.

## Project

Arc Raiders AutoScrapper is a Python 3.13 desktop automation app for Arc Raiders inventory management.
It uses Textual for the TUI, screen capture + OCR for item detection, rule lookup for `KEEP | SELL | RECYCLE`, and optional desktop input automation.
It does **not** hook into the game process.

## Stack

| Area | Details |
| --- | --- |
| Runtime | Python 3.13, `uv` |
| UI | `textual` |
| OCR | `tesserocr`, `tessdata.fast-eng` |
| Vision | `opencv-python-headless`, `Pillow`, `mss` |
| Matching | `rapidfuzz` |
| Input | `pydirectinput-rgx` (Windows), `pynput` via `linux-input` extra (Linux) |

## Commands

Prefer `python3 -m uv ...` in automation because `uv` may not be on `PATH`.

| Task | Command |
| --- | --- |
| Setup | `python3 -m uv sync` |
| Setup with Linux input | `python3 -m uv sync --extra linux-input` |
| Run TUI | `python3 -m uv run autoscrapper` |
| Scan | `python3 -m uv run autoscrapper scan` |
| Safe scan validation | `python3 -m uv run autoscrapper scan --dry-run` |
| Lint | `python3 -m uv run ruff check src/ tests/` |
| Format | `python3 -m uv run ruff format src/ tests/ scripts/` |
| Tests | `python3 -m uv run pytest` |
| Types | `python3 -m uv run basedpyright src/` |
| Broad repo checks | `python3 -m uv run prek run --all-files` |
| Refresh generated data/rules | `python3 -m uv run python scripts/update_snapshot_and_defaults.py` |
| Dry-run data refresh | `python3 -m uv run python scripts/update_snapshot_and_defaults.py --dry-run` |
| Qlty check | `qlty check -a` |
| Qlty metrics | `qlty metrics -a` |
| Qlty smells | `qlty smells -a` |

## Python Tooling

| Tool | Purpose | Config |
| --- | --- | --- |
| `basedpyright` | Type checking (replaces mypy) | `[tool.basedpyright]` in `pyproject.toml` |
| `ruff` | Lint (`E`, `F` rules) + format | `[tool.ruff]` in `pyproject.toml` |

- **basedpyright** runs on every `.py` edit via PostToolUse hook in `.claude/settings.json`. It logs errors to the terminal — no auto-fix.
- **ruff** auto-fixes lint issues and formats on every edit via the same hook.
- mypy was removed; basedpyright covers equivalent type safety with faster feedback.

## Validation

| Change type | Minimum validation |
| --- | --- |
| Python source | `python3 -m uv run ruff check src/ tests/` + `python3 -m uv run pytest` |
| Tech debt / quality pass | `qlty check -a` + `qlty metrics -a` + `qlty smells -a` |
| OCR / scanner / interaction / input | Standard validation + `python3 -m uv run autoscrapper scan --dry-run` against a live Arc Raiders window |
| Generated data / default rules | Use the updater script; usually run `--dry-run` first |
| Docs / agent guidance only | Verify affected files, links, and instructions stay accurate |

Notes:
- Local tests exist and should be run for code changes even though GitHub Actions currently runs Ruff only.
- Do not claim end-to-end validation unless a live Arc Raiders window was used.
- Prefer `--dry-run` before anything that could click in-game.

## Repository Map

| Path | Purpose |
| --- | --- |
| `src/autoscrapper/tui/` | Textual screens; `scan.py` starts the scan flow |
| `src/autoscrapper/scanner/` | Engine, page loop, reporting, action execution |
| `src/autoscrapper/interaction/` | Screen capture, grid detection, platform input |
| `src/autoscrapper/ocr/` | Tesseract init, preprocessing, infobox/item extraction |
| `src/autoscrapper/core/item_actions.py` | Rule lookup and fuzzy decision logic |
| `src/autoscrapper/items/rules_store.py` | Load/save custom rules; custom overrides bundled defaults |
| `src/autoscrapper/progress/` | Quest/hideout/crafting data and default-rule generation |
| `scripts/update_snapshot_and_defaults.py` | Regenerates progress snapshots and bundled default rules |
| `src/autoscrapper/config.py` | Persisted config dataclasses and versioning |
| `tests/` | Pytest suite |

## Critical Invariants

- Preserve custom-over-default rule precedence.
- Do **not** hand-edit `src/autoscrapper/progress/data/*` or `src/autoscrapper/items/items_rules.default.json`; regenerate via `scripts/update_snapshot_and_defaults.py`.
- Bump the config version in `src/autoscrapper/config.py` when changing persisted config fields.
- `initialize_ocr()` must run on the main thread before the scan thread starts; it eagerly inits all four PSM APIs (`SINGLE_BLOCK`, `SINGLE_LINE`, `SINGLE_WORD`, `SPARSE_TEXT`).
- Each Tesseract API instance has its own lock (`_api_lock`, `_api_line_lock`, `_api_single_word_lock`, `_api_sparse_lock`); do **not** collapse them back to a single shared lock.
- Image-processing coordinates are capture-space pixels; screen-space translation belongs in `src/autoscrapper/interaction/ui_windows.py`.
- The dark context menu opens to the **left** of the clicked cell; `_CONTEXT_MENU_*` constants in `inventory_vision.py` are normalized by 1920. The positional offsets are still uncalibrated — prefer `find_infobox` path and live recalibration via `/calibrate-vision` before shipping positional-crop changes.
- `ocr_infobox_with_context(window_bgr, rect)` is the preferred infobox OCR call (passes full window for upward title-band extension). Use `ocr_infobox(crop)` only when the full window is not available.
- `find_context_menu_crop` rejects crops with `dark_fraction < 0.20` on the left half (gray < 40); this threshold is calibration-sensitive — do not tighten without corpus replay.
- Keep the fuzzy-match threshold shared between OCR matching and rule lookup. Changing `threshold`/`score_cutoff` values (T001) requires corpus replay before shipping.
- `ocr_debug/` is disposable debug output and is safe to clear between sessions. Failure-path artifacts (`title_strip_fail_raw`, `title_strip_fail_processed`, `ctx_menu_lines_fail.json`) are written automatically and consumed by `/add-fixture` and `/triage-failures`.

## Hotspots

- `src/autoscrapper/ocr/`, `src/autoscrapper/interaction/`, and `src/autoscrapper/scanner/` are tightly coupled.
- `src/autoscrapper/ocr/inventory_vision.py` is the hottest and most calibration-sensitive file.
- `src/autoscrapper/core/item_actions.py` and `src/autoscrapper/items/rules_store.py` define action resolution behavior.
- `src/autoscrapper/progress/` changes often imply regenerating bundled data.

## Remotes

- `upstream` → `https://github.com/zappybiby/ArcRaiders-AutoScrapper.git` (canonical source)
- `origin` → your fork; sync from upstream before pushing: `git pull --autostash upstream main`

## Git Workflow

- Conventional commits: `feat:`, `fix:`, `chore:`, `docs:` prefixes on commit messages and branch names.
- Sync from upstream before pushing: `git pull --autostash upstream main`

## Windows Setup

- Tesseract system deps installed via `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\setup-windows.ps1`
- tesserocr wheel is pinned in `pyproject.toml` via a Windows-specific GitHub release URL; do not upgrade without testing.

## Agent Workflow

- Make minimal, targeted edits.
- Use project skills in `.claude/skills/` and specialist agents in `.claude/agents/` when the task matches — see table below.
- Read the relevant module before editing; update adjacent docs only when behavior or workflow changes.
- Use script-driven or tool-driven changes instead of manual rewrites for generated assets.
- Call out any unverified behavior clearly in summaries and PR text.
- **Search**: Use `Grep` (ripgrep) for text search — never bash `grep`. Use AST-grep for structural/syntactic search. Use LSP symbol tools for definition/reference navigation.
- **File writing on WSL**: "Error writing file" on `/mnt/c/...` paths means the parent directory doesn't exist — run `mkdir -p <dir>` via Bash before `Write`. Always use the `Write` tool, never bash echo/heredoc.

## Skills & Agents

Invoke skills with `/skill-name`. Use agents via `Agent(subagent_type="agent-name")`.

### Workflow Skills (`.claude/skills/`)

| Skill | When to use |
| --- | --- |
| `/diagnose-scan` | First stop for any scan failure — runs dry-run, classifies output, dispatches to specialist |
| `/verify` | Full lint + types + tests before committing |
| `/ci-promote` | Pre-push checklist + PR creation |
| `/data-snapshot-updater` | Regenerate progress data and default rules from Metaforge |
| `/upstream-sync` | Sync fork from upstream before pushing |
| `/threshold-change` | Safe fuzzy-threshold tuning with before/after corpus replay |
| `/threshold-corpus-replay` | Validate a specific threshold candidate against corpus |
| `/ocr-corpus-replay` | Validate OCR code changes against failure corpus |
| `/calibrate-vision` | Recalibrate context-menu crop constants in `inventory_vision.py` |
| `/add-fixture` | Lock in a new OCR regression fixture from `ocr_debug/` |
| `/add-rule` | Add or edit a custom item rule |
| `/config-bump` | Safely version-bump a config field change with migration |
| `/scan-report` | Classify and summarize last dry-run output from `/tmp/scan-diag.txt` |
| `/triage-failures` | Analyze OCR failure corpus for systematic misread patterns |
| `/clean-debug` | Prune stale `ocr_debug/` images |
| `/benchmark` | Benchmark tessdata model variants (fast vs best) |

Context docs (not user-invocable, referenced by other skills): `ocr-debug`, `scan-failed`, `ocr-unavailable`.

### Specialist Agents (`.claude/agents/`)

| Agent | When to use |
| --- | --- |
| `ocr-reviewer` | After editing `ocr/` or `scanner/` — coordinate space bugs, upscale artifacts, threshold regressions |
| `scan-validator` | After editing `scanner/` or `interaction/` — timing, page detection, action dispatch |
| `rules-reviewer` | After editing `item_actions.py` or `rules_store.py` — precedence bugs, action mapping |
| `config-reviewer` | After editing `config.py` — version bump, migration path, serialization |
| `tui-reviewer` | After editing `tui/` — threading violations, reactive state bugs, worker lifecycle |
| `progress-reviewer` | After editing `progress/` — quest inference, crafting overrides, generated-file bypass |
| `data-pipeline-reviewer` | After editing `data_update.py` — field mapping, pagination, merge bugs |
| `api-reviewer` | After editing `api/` — slot mapping, None-guards, Cell coordinate plumbing |
| `security-reviewer` | After editing `interaction/` or `scanner/` — input validation, window targeting |
| `visual-analysis-ocr` | Inspect `ocr_debug/` PNG images for visual diagnosis |

<!-- rtk-instructions v2 -->
# RTK (Rust Token Killer) - Token-Optimized Commands

## Golden Rule

**Always prefix commands with `rtk`**. If RTK has a dedicated filter, it uses it. If not, it passes through unchanged. This means RTK is always safe to use.

**Important**: Even in command chains with `&&`, use `rtk`:
```bash
# ❌ Wrong
git add . && git commit -m "msg" && git push

# ✅ Correct
rtk git add . && rtk git commit -m "msg" && rtk git push
```

## RTK Commands by Workflow

### Build & Compile (80-90% savings)
```bash
rtk cargo build         # Cargo build output
rtk cargo check         # Cargo check output
rtk cargo clippy        # Clippy warnings grouped by file (80%)
rtk tsc                 # TypeScript errors grouped by file/code (83%)
rtk lint                # ESLint/Biome violations grouped (84%)
rtk prettier --check    # Files needing format only (70%)
rtk next build          # Next.js build with route metrics (87%)
```

### Test (90-99% savings)
```bash
rtk cargo test          # Cargo test failures only (90%)
rtk vitest run          # Vitest failures only (99.5%)
rtk playwright test     # Playwright failures only (94%)
rtk test <cmd>          # Generic test wrapper - failures only
```

### Git (59-80% savings)
```bash
rtk git status          # Compact status
rtk git log             # Compact log (works with all git flags)
rtk git diff            # Compact diff (80%)
rtk git show            # Compact show (80%)
rtk git add             # Ultra-compact confirmations (59%)
rtk git commit          # Ultra-compact confirmations (59%)
rtk git push            # Ultra-compact confirmations
rtk git pull            # Ultra-compact confirmations
rtk git branch          # Compact branch list
rtk git fetch           # Compact fetch
rtk git stash           # Compact stash
rtk git worktree        # Compact worktree
```

Note: Git passthrough works for ALL subcommands, even those not explicitly listed.

### GitHub (26-87% savings)
```bash
rtk gh pr view <num>    # Compact PR view (87%)
rtk gh pr checks        # Compact PR checks (79%)
rtk gh run list         # Compact workflow runs (82%)
rtk gh issue list       # Compact issue list (80%)
rtk gh api              # Compact API responses (26%)
```

### JavaScript/TypeScript Tooling (70-90% savings)
```bash
rtk pnpm list           # Compact dependency tree (70%)
rtk pnpm outdated       # Compact outdated packages (80%)
rtk pnpm install        # Compact install output (90%)
rtk npm run <script>    # Compact npm script output
rtk npx <cmd>           # Compact npx command output
rtk prisma              # Prisma without ASCII art (88%)
```

### Files & Search (60-75% savings)
```bash
rtk ls <path>           # Tree format, compact (65%)
rtk read <file>         # Code reading with filtering (60%)
rtk grep <pattern>      # Search grouped by file (75%)
rtk find <pattern>      # Find grouped by directory (70%)
```

### Analysis & Debug (70-90% savings)
```bash
rtk err <cmd>           # Filter errors only from any command
rtk log <file>          # Deduplicated logs with counts
rtk json <file>         # JSON structure without values
rtk deps                # Dependency overview
rtk env                 # Environment variables compact
rtk summary <cmd>       # Smart summary of command output
rtk diff                # Ultra-compact diffs
```

### Infrastructure (85% savings)
```bash
rtk docker ps           # Compact container list
rtk docker images       # Compact image list
rtk docker logs <c>     # Deduplicated logs
rtk kubectl get         # Compact resource list
rtk kubectl logs        # Deduplicated pod logs
```

### Network (65-70% savings)
```bash
rtk curl <url>          # Compact HTTP responses (70%)
rtk wget <url>          # Compact download output (65%)
```

### Meta Commands
```bash
rtk gain                # View token savings statistics
rtk gain --history      # View command history with savings
rtk discover            # Analyze Claude Code sessions for missed RTK usage
rtk proxy <cmd>         # Run command without filtering (for debugging)
rtk init                # Add RTK instructions to CLAUDE.md
rtk init --global       # Add RTK to ~/.claude/CLAUDE.md
```

## Token Savings Overview

| Category | Commands | Typical Savings |
|----------|----------|-----------------|
| Tests | vitest, playwright, cargo test | 90-99% |
| Build | next, tsc, lint, prettier | 70-87% |
| Git | status, log, diff, add, commit | 59-80% |
| GitHub | gh pr, gh run, gh issue | 26-87% |
| Package Managers | pnpm, npm, npx | 70-90% |
| Files | ls, read, grep, find | 60-75% |
| Infrastructure | docker, kubectl | 85% |
| Network | curl, wget | 65-70% |

Overall average: **60-90% token reduction** on common development operations.
<!-- /rtk-instructions -->

## vexp <!-- vexp v1.3.11 -->

**MANDATORY: use `run_pipeline` — do NOT grep or glob the codebase.**
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