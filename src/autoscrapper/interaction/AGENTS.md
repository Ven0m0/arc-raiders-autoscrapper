<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-15 | Updated: 2026-04-15 -->

# interaction/

## Purpose
Screen capture, inventory grid detection, coordinate translation, and platform input. Bridges between capture-space pixel coordinates (used by OCR) and screen-space coordinates (used for mouse/keyboard automation).

## Key Files

| File | Description |
|------|-------------|
| `ui_windows.py` | Window detection and coordinate translation. **Screen-space ↔ capture-space conversion lives here only.** Wraps `mss` for screen capture. |
| `inventory_grid.py` | Detects the inventory grid within a captured frame. Returns cell bounding boxes in capture-space pixels. |
| `input_driver.py` | Platform abstraction for mouse/keyboard input. Uses `pydirectinput-rgx` on Windows, `pynput` via `linux-input` extra on Linux. |
| `keybinds.py` | User-configurable keybind mappings for scan control actions. |
| `__init__.py` | Package init — no side effects. |

## For AI Agents

### Working In This Directory
- **Coordinate invariant**: image-processing coordinates are capture-space pixels. Screen-space translation belongs exclusively in `ui_windows.py`. Never apply DPI/offset corrections in `inventory_grid.py` or `ocr/`.
- The dark context menu opens to the **left** of the clicked cell — `_CONTEXT_MENU_*` constants in `inventory_vision.py` account for this. Do not move click targets right.
- `input_driver.py` must never be called directly from OCR or scanner logic — always go through the scanner action layer.

### Testing Requirements
- `tests/autoscrapper/interaction/test_keybinds.py`
- `tests/autoscrapper/interaction/test_ui_windows.py`
- Run: `uv run pytest tests/autoscrapper/interaction/ -x -q`

### Common Patterns
- `--dry-run` flag in the scanner disables all `input_driver` calls — use this for safe validation.
- Grid detection returns `List[Cell]`; each `Cell` carries `(page, row, col)` and capture-space bbox.

## Dependencies

### Internal
- `src/autoscrapper/ocr/inventory_vision.py` — consumes capture-space bboxes produced here
- `src/autoscrapper/scanner/scan_loop.py` — orchestrates capture → OCR → action

### External
- `mss` — fast cross-platform screen capture
- `pydirectinput-rgx` (Windows) / `pynput` (Linux) — keyboard and mouse input
- `opencv-python-headless` — image processing for grid detection
