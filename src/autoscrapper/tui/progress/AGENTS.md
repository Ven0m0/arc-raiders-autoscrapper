<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-15 | Updated: 2026-04-15 -->

# tui/progress/

## Purpose
Textual screens and widgets for displaying quest, hideout, and crafting progress state. Allows users to review and override what the decision engine considers "in progress" before running a scan.

## Key Files

| File | Description |
|------|-------------|
| `review.py` | `ProgressReviewScreen` — shows quest/hideout completion state, allows marking items as done. |
| `state.py` | `ProgressStateWidget` — reactive widget that reflects live progress state changes. |
| `base.py` | Shared base classes and helpers for progress screens. |
| `__init__.py` | Package init — no side effects. |

## For AI Agents

### Working In This Directory
- All Textual threading rules from `AGENTS.md` apply here: no blocking calls on the main thread, use `call_from_thread()` for worker-to-widget updates.
- Progress state displayed here comes from `src/autoscrapper/progress/data_loader.py` — changes to the data schema need matching updates in these widgets.

### Testing Requirements
- No dedicated tests currently. Manual validation via `uv run autoscrapper` → progress screens.

## Dependencies

### Internal
- `src/autoscrapper/progress/data_loader.py` — progress data source
- `src/autoscrapper/progress/quest_inference.py` — active quest computation
- `src/autoscrapper/tui/common.py` — shared widgets

### External
- `textual` — reactive widgets and screens
