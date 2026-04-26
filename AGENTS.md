# Arc Raiders AutoScrapper — Agent Guide

> **Quick Links**: [Cross-Reference](./.kilo/CROSS_REFERENCE.md) • [Skills](./.kilo/skills/) • [Agents](./.kilo/agents/)

This is the canonical guide for AI agents and contributors working on Arc Raiders AutoScrapper. For IDE-specific guidance, see [`.github/copilot-instructions.md`](./.github/copilot-instructions.md).

---

## Executive Summary

**Arc Raiders AutoScrapper** is a desktop automation tool for Arc Raiders inventory management using:
- **Textual** (Python TUI framework) for the interface
- **Tesseract OCR** (via tesserocr) for item name recognition
- **OpenCV/Pillow** for screen capture and image preprocessing
- **RapidFuzz** for fuzzy item name matching
- **pydirectinput/pynput** for optional desktop input automation

**Tech Stack**: Python 3.13, `uv` package manager, Ruff (lint/format), basedpyright (type-check), pytest

---

## System Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Textual TUI   │────▶│   Scanner Loop   │────▶│   OCR Engine    │
│  (tui/*.py)     │     │ (scanner/*.py)   │     │ (ocr/*.py)      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │                           │
                               ▼                           ▼
                        ┌──────────────┐          ┌──────────────┐
                        │ Interaction  │          │  Tesseract   │
                        │(interaction/)│          │   OCR API    │
                        └──────────────┘          └──────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │ Item Actions │
                        │(rules, sell, │
                        │  recycle)    │
                        └──────────────┘
```

---

## Repository Layout

```
src/autoscrapper/
├── tui/                    # Textual UI screens
│   ├── app.py             # Main app entry
│   ├── scan.py            # Scan orchestration screen
│   └── *.tcss             # Stylesheets
├── scanner/               # Core scan engine
│   ├── scan_loop.py       # Page iteration logic
│   └── actions.py         # Action dispatch
├── ocr/                   # OCR pipeline
│   ├── inventory_vision.py # Image preprocessing, OCR
│   └── tesseract_init.py  # Tesseract API setup
├── interaction/           # Screen capture & input
│   ├── screen_capture.py  # mss-based capture
│   ├── grid_detection.py  # Inventory grid detection
│   └── input_driver.py    # Platform input (Windows/Linux)
├── core/                  # Business logic
│   └── item_actions.py    # Rule lookup, fuzzy matching
├── items/                 # Item rules
│   ├── rules_store.py     # Custom/default rule loading
│   └── items_rules.default.json  # Generated default rules
├── progress/              # Game data & quest tracking
│   ├── data/              # Generated JSON snapshots
│   └── data_update.py     # MetaForge API integration
└── config.py              # Persisted configuration
```

---

## Essential Commands

| Task | Command |
|------|---------|
| **Setup** | `uv sync` |
| **Run TUI** | `uv run autoscrapper` |
| **Dry-run scan** | `uv run autoscrapper scan --dry-run` |
| **Validate** | `uv run ruff check src/ tests/ scripts/ && uv run basedpyright src/ && uv run pytest` |
| **Format** | `uv run ruff format src/ tests/ scripts/` |
| **Update data** | `uv run python scripts/update_snapshot_and_defaults.py --dry-run` |

---

## Using Agents & Skills

### Quick Reference

| I need to... | Use |
|--------------|-----|
| Validate my changes | `/verify` or skill `verify` |
| Fix OCR misreads | `/ocr-corpus-replay` → `ocr-reviewer` agent |
| Add item rule | `/add-rule` skill |
| Update game data | `/patch-update` skill |
| Fix scan failures | `/diagnose-scan` → dispatch to specialist agent |
| Generate tests | `test-generator` agent |
| Review code | `{domain}-reviewer` agent (e.g., `ocr-reviewer`, `tui-reviewer`) |

### Agent Dispatch Pattern

When code changes are ready for review, invoke the appropriate specialist agent:

```
# OCR/vision changes
Agent: ocr-reviewer

# Scanner/interaction changes  
Agent: scan-validator

# TUI changes
Agent: tui-reviewer

# Rule logic changes
Agent: rules-reviewer

# Config changes
Agent: config-reviewer

# Data pipeline changes
Agent: data-pipeline-reviewer
```

See [`.kilo/CROSS_REFERENCE.md`](./.kilo/CROSS_REFERENCE.md) for the complete command/skill/agent matrix.

---

## Critical Invariants (DO NOT BREAK)

### OCR & Threading
1. **`initialize_ocr()` must run on main thread** before any scan threads start
2. **Four separate Tesseract API locks**: `_api_lock`, `_api_line_lock`, `_api_single_word_lock`, `_api_sparse_lock`
3. **2× upscaling in `inventory_vision.py`**: OCR boxes must be halved before reuse in original-space
4. **Capture-space ≠ Screen-space**: Image coordinates vs input coordinates — translation happens in `interaction/ui_windows.py`

### Data Integrity
5. **Never hand-edit** `src/autoscrapper/progress/data/*` — use `scripts/update_snapshot_and_defaults.py`
6. **Never hand-edit** `src/autoscrapper/items/items_rules.default.json` — same script
7. **Custom rules take precedence** over default rules
8. **Bump `CONFIG_VERSION`** and add migration when config fields change

### Validation Requirements
9. **OCR/scanner changes**: Require `autoscrapper scan --dry-run` against live game window
10. **Threshold changes**: Require corpus replay (`ocr-corpus-replay`) before shipping

---

## Validation Checklist by Change Type

| Change Type | Required Validation |
|-------------|---------------------|
| Python source | `ruff check` + `basedpyright` + `pytest` |
| Workflow files | `pre-commit run --files .github/workflows/*.yml` |
| OCR/scanner/input | Standard + `autoscrapper scan --dry-run` (live window) |
| Config fields | Version bump + migration + round-trip test |
| Generated data | Use updater script with `--dry-run` first |

---

## Hotspots (Extra Review Required)

Files that require careful review for any changes:

- `src/autoscrapper/ocr/inventory_vision.py` — Coordinate spaces, preprocessing, Tesseract config
- `src/autoscrapper/scanner/scan_loop.py` — Timing, page detection, action dispatch
- `src/autoscrapper/core/item_actions.py` — Rule lookup, fuzzy thresholds
- `src/autoscrapper/items/rules_store.py` — Rule precedence, loading logic
- `src/autoscrapper/config.py` — Versioning, migrations

---

## Common Workflows

### 1. Fix OCR Misreads
```
/diagnose-scan → analyze output → /ocr-corpus-replay → /add-fixture → /verify
```

### 2. New Game Patch
```
/patch-update → check for unlisted items → /add-rule (gaps) → /verify → /ci-promote
```

### 3. Before Committing
```
/verify → /precommit-fix (if needed) → /upstream-sync → /merge-to-main
```

### 4. Clean Debug Artifacts
```
/clean-debug → /dead-code-sweep → /verify
```

---

## Git & Remote Rules

- **Fork only**: `https://github.com/Ven0m0/arc-raiders-autoscrapper`
- **Never push to upstream**: `zappybiby/ArcRaiders-AutoScrapper`
- **Always sync first**: Run `upstream-sync` skill before pushing
- **PR target**: Use `--repo Ven0m0/arc-raiders-autoscrapper` with `gh pr create`

---

## Documentation Hierarchy

| File | Purpose |
|------|---------|
| `AGENTS.md` (this file) | Canonical repo-wide rules |
| `.github/copilot-instructions.md` | Quick startup for IDE |
| `.github/instructions/*.md` | Path-specific rules |
| `.kilo/CROSS_REFERENCE.md` | Command/skill/agent lookup |
| `.kilo/rules/*.md` | Tool usage and coding standards |
| `.kilo/agents/*.md` | Specialist agent definitions |
| `.kilo/skills/*/SKILL.md` | Workflow procedures |

---

## Troubleshooting

| Symptom | Solution |
|---------|----------|
| `uv run` fails with module error | Use `uv run <cmd>` (uv handles its own PATH) |
| Pre-commit hook fails | See `/precommit-fix` skill |
| OCR returns "UNAVAILABLE" | See `/ocr-unavailable` skill (context menu misread) |
| Scan wrong decisions | See `/scan-failed` skill (rule precedence issue) |
| Workflow YAML invalid | `pre-commit run --files .github/workflows/<name>.yml` |

---

*Last updated: 2026-04-26*
*See [`.kilo/CROSS_REFERENCE.md`](./.kilo/CROSS_REFERENCE.md) for the complete skill/agent index.*
