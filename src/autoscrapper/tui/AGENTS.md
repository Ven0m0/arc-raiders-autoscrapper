<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-15 | Updated: 2026-04-15 -->

# tui/

## Purpose
Textual-based TUI screens and application shell. Provides the interactive user interface for configuring and running scans, managing rules, viewing progress, and adjusting settings. All Textual reactive state and widget composition lives here.

## Key Files

| File | Description |
|------|-------------|
| `app.py` | `AutoScrapperApp` — root Textual application. Mounts screens and handles top-level key bindings. |
| `app.tcss` | Textual CSS stylesheet for all screens. |
| `scan.py` | `ScanScreen` — starts the scan flow, spawns the scan thread, shows live progress. |
| `settings.py` | `SettingsScreen` — user-facing settings (OCR params, keybinds, rule file path). |
| `rules.py` | `RulesScreen` — displays and edits custom item rules. |
| `maintenance.py` | `MaintenanceScreen` — default rule diff, data refresh trigger. |
| `api_settings.py` | `ApiSettingsScreen` — MetaForge API key and endpoint configuration. |
| `status.py` | `StatusBar` widget — bottom-of-screen status display. |
| `common.py` | Shared Textual widgets and helpers used across screens. |
| `__init__.py` | Package init — no side effects. |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `progress/` | Progress review screens: quest/hideout state display (see `tests/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- **Never call blocking I/O or sleep on the Textual main thread.** All slow operations (scan, data refresh) must run in a worker thread via `self.run_worker()` or `asyncio.create_task()`.
- Reactive state changes must use `self.app.call_from_thread()` when originating from a worker thread — direct widget mutation from non-main threads will crash Textual.
- CSS lives exclusively in `app.tcss` — do not use inline styles.
- Screen navigation uses `self.app.push_screen()` / `self.app.pop_screen()`.

### Testing Requirements
- No dedicated TUI integration tests currently. Use manual testing via `uv run autoscrapper`.
- The `tui-reviewer` agent reviews changes to this directory for Textual misuse and threading violations.

### Common Patterns
- Screens inherit from `textual.screen.Screen`.
- Use `DataTable` for rule and item list displays.
- Progress widgets in `progress/` subpackage use `reactive` attributes for live updates.

## Dependencies

### Internal
- `src/autoscrapper/scanner/engine.py` — scan thread control
- `src/autoscrapper/items/rules_store.py` — rule loading and saving
- `src/autoscrapper/config.py` — persisted settings
- `src/autoscrapper/progress/` — progress state for the progress screens

### External
- `textual` — TUI framework (screens, widgets, CSS, reactive)
