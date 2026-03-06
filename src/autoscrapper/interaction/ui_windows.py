from __future__ import annotations

import os
import sys
import time
from typing import Optional, Tuple

import mss
import numpy as np
import pywinctl as pwc

from .inventory_grid import Cell
from . import input_driver as pdi


# Target window
def _default_target_app() -> str:
    if sys.platform.startswith("linux"):
        return "Arc Raiders"
    return "PioneerGame.exe"


TARGET_APP = os.environ.get("AUTOSCRAPPER_TARGET_APP") or _default_target_app()
WINDOW_TIMEOUT = 30.0
WINDOW_POLL_INTERVAL = 0.05

# Click pacing
ACTION_DELAY = 0.05
MOVE_DURATION = 0.05
SELL_RECYCLE_SPEED_MULT = (
    1.5  # extra slack vs default pacing (MOVE_DURATION/ACTION_DELAY)
)
SELL_RECYCLE_MOVE_DURATION = MOVE_DURATION * SELL_RECYCLE_SPEED_MULT
SELL_RECYCLE_ACTION_DELAY = ACTION_DELAY * SELL_RECYCLE_SPEED_MULT
SELL_RECYCLE_POST_DELAY = 0.1  # seconds to allow item collapse after confirm

# Scrolling
# Alternate 16/17 downward scroll clicks to advance between 4x5 grids.
SCROLL_CLICKS_PER_PAGE = 16
SCROLL_MOVE_DURATION = 0.5
SCROLL_INTERVAL = 0.04
SCROLL_SETTLE_DELAY = 0.05

_MSS: Optional["MSSBase"] = None


def _target_aliases(target_app: str) -> list[str]:
    target = (target_app or "").strip().lower()
    if not target:
        return []
    aliases = [target]
    # Windows Phone Link often uses multiple process/window hosts.
    if target in {"phone link", "phonelink", "phoneexperiencehost.exe"}:
        aliases.extend(
            [
                "phone link",
                "phoneexperiencehost.exe",
                "yourphoneappproxy.exe",
                "yourphone.exe",
            ]
        )
    # De-duplicate while preserving order
    seen: set[str] = set()
    out: list[str] = []
    for alias in aliases:
        if alias not in seen:
            seen.add(alias)
            out.append(alias)
    return out


def _window_app_and_title(win: pwc.Window) -> Tuple[str, str]:
    app = ""
    title = ""
    try:
        app = (win.getAppName() or "").strip()
    except Exception:
        app = ""
    try:
        if hasattr(win, "title"):
            title = (getattr(win, "title") or "").strip()
        elif hasattr(win, "getTitle"):
            title = (win.getTitle() or "").strip()
    except Exception:
        title = ""
    return app, title


def _window_matches_target(win: pwc.Window, target_app: str) -> bool:
    aliases = _target_aliases(target_app)
    if not aliases:
        return False
    app, title = _window_app_and_title(win)
    app_lower = app.lower()
    title_lower = title.lower()
    return any(alias in app_lower or alias in title_lower for alias in aliases)


def _activate_window_best_effort(win: pwc.Window) -> None:
    """
    Try to focus the window without failing the scan if activation is not supported.
    Intentionally does NOT call win.restore() — that unmaximizes the window and
    changes its size, corrupting all screen-coordinate calculations for the run.
    """
    try:
        if hasattr(win, "activate"):
            win.activate()
            return
    except Exception:
        pass
    try:
        if hasattr(win, "focus"):
            win.focus()
    except Exception:
        pass


def _find_matching_window(target_app: str) -> Optional[pwc.Window]:
    """
    Search all windows for the requested app/title substring.
    """
    try:
        windows = pwc.getAllWindows()
    except Exception:
        return None
    matches: list[pwc.Window] = []
    for win in windows or []:
        try:
            if not _window_matches_target(win, target_app):
                continue
            w = int(getattr(win, "width", 0) or 0)
            h = int(getattr(win, "height", 0) or 0)
            left = int(getattr(win, "left", 0) or 0)
            top = int(getattr(win, "top", 0) or 0)
            # Ignore tiny helper/sink windows and clearly hidden placeholders.
            if w < 200 or h < 300:
                continue
            if left < -10000 or top < -10000:
                continue
            if _window_matches_target(win, target_app):
                matches.append(win)
        except Exception:
            continue
    if not matches:
        return None
    if len(matches) == 1:
        return matches[0]

    def _score(win: pwc.Window) -> tuple[int, float, float]:
        try:
            w = max(1.0, float(getattr(win, "width", 0) or 0))
            h = max(1.0, float(getattr(win, "height", 0) or 0))
        except Exception:
            w, h = 1.0, 1.0
        aspect = h / w  # phone mirror windows are usually tall
        area = w * h
        tall_bonus = 1 if aspect > 1.2 else 0
        # Prefer tall windows first, then larger area, then taller aspect.
        return (tall_bonus, area, aspect)

    return max(matches, key=_score)


def escape_pressed() -> bool:
    """
    Detect whether F12 is currently pressed (abort key).
    """
    return pdi.escape_pressed()


def abort_if_escape_pressed() -> None:
    """
    Raise KeyboardInterrupt if F12 is down.
    """
    if escape_pressed():
        raise KeyboardInterrupt("F12 pressed")


def wait_for_target_window(
    target_app: str = TARGET_APP,
    timeout: float = WINDOW_TIMEOUT,
    poll_interval: float = WINDOW_POLL_INTERVAL,
) -> pwc.Window:
    """
    Wait until the active window belongs to the target process.
    """
    start = time.monotonic()
    while time.monotonic() - start < timeout:
        abort_if_escape_pressed()
        win = pwc.getActiveWindow()
        if win is not None and _window_matches_target(win, target_app):
            return win

        # Fallback: find a matching window even if it is not active and try to focus it.
        candidate = _find_matching_window(target_app)
        if candidate is not None:
            _activate_window_best_effort(candidate)
            sleep_with_abort(min(0.15, poll_interval))
            win_after = pwc.getActiveWindow()
            if win_after is not None and _window_matches_target(win_after, target_app):
                return win_after

        sleep_with_abort(poll_interval)

    raise TimeoutError(f"Timed out waiting for active window {target_app!r}")


def window_rect(win: pwc.Window) -> Tuple[int, int, int, int]:
    """
    (left, top, width, height) in screen coordinates for the window.
    """
    return int(win.left), int(win.top), int(win.width), int(win.height)


def window_display_info(
    win: pwc.Window,
) -> Tuple[str, Tuple[int, int], Tuple[int, int, int, int]]:
    """
    Return (display name, display size, work area) and enforce that the window is on a single monitor.
    """
    display_names = win.getDisplay()
    if not display_names:
        raise RuntimeError("Unable to determine which monitor the target window is on.")
    if len(display_names) > 1:
        joined = ", ".join(display_names)
        raise RuntimeError(
            f"Target window spans multiple monitors ({joined}); move it fully onto one display."
        )

    display_name = display_names[0]
    size = pwc.getScreenSize(display_name)
    work_area = pwc.getWorkArea(display_name)
    return display_name, size, work_area


def window_monitor_rect(win: pwc.Window) -> Tuple[int, int, int, int]:
    """
    Return (left, top, right, bottom) bounds for the physical monitor containing
    the window center.

    This differs from the OS "work area", which excludes taskbars/docks and can
    cause false warnings for borderless fullscreen windows.
    """
    win_left, win_top, win_width, win_height = window_rect(win)
    center_x = win_left + (win_width // 2)
    center_y = win_top + (win_height // 2)

    sct = _get_mss()
    monitors = getattr(sct, "monitors", None)
    if not monitors or len(monitors) < 2:
        raise RuntimeError("Unable to determine monitor bounds via mss.")

    # Index 0 is the "all monitors" virtual rectangle.
    for mon in monitors[1:]:
        mon_left = int(mon["left"])
        mon_top = int(mon["top"])
        mon_right = mon_left + int(mon["width"])
        mon_bottom = mon_top + int(mon["height"])
        if mon_left <= center_x < mon_right and mon_top <= center_y < mon_bottom:
            return mon_left, mon_top, mon_right, mon_bottom

    raise RuntimeError("Unable to map target window to a monitor via mss.")


def _get_mss() -> "MSSBase":
    """
    Lazily create an MSS instance for screen capture.
    """
    global _MSS
    if sys.platform not in ("win32", "linux"):
        raise RuntimeError(
            "Screen capture requires Windows or Linux; this build targets X11/XWayland."
        )

    if _MSS is None:
        _MSS = mss.mss()
    return _MSS


def capture_region(region: Tuple[int, int, int, int]) -> np.ndarray:
    """
    Capture a BGR screenshot of the given region (left, top, width, height).
    """
    left, top, width, height = region
    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid capture region size: width={width}, height={height}")

    sct = _get_mss()
    bbox = {
        "left": int(left),
        "top": int(top),
        "width": int(width),
        "height": int(height),
    }

    try:
        shot = sct.grab(bbox)
    except Exception as exc:
        raise RuntimeError(
            f"mss failed to capture the requested region {bbox}: {exc}"
        ) from exc

    frame = np.asarray(shot)
    if frame.shape[2] == 4:
        frame = frame[:, :, :3]  # drop alpha, keep BGR order
    return np.ascontiguousarray(frame)


def sleep_with_abort(duration: float) -> None:
    """
    Sleep for a specific duration and honor Escape aborts.
    """
    time.sleep(duration)
    abort_if_escape_pressed()


def pause_action(duration: float = ACTION_DELAY) -> None:
    """
    Standard pause to keep a safe delay between input/processing steps.
    """
    sleep_with_abort(duration)


def timed_action(func, *args, **kwargs) -> None:
    """
    Run an input action while checking for Escape.
    """
    abort_if_escape_pressed()
    func(*args, **kwargs)


def click_absolute(x: int, y: int, pause: float = ACTION_DELAY) -> None:
    timed_action(pdi.leftClick, x, y)
    pause_action(pause)


def click_window_relative(
    x: int,
    y: int,
    window_left: int,
    window_top: int,
    pause: float = ACTION_DELAY,
) -> None:
    click_absolute(int(window_left + x), int(window_top + y), pause=pause)


def move_absolute(
    x: int,
    y: int,
    duration: float = MOVE_DURATION,
    pause: float = ACTION_DELAY,
) -> None:
    timed_action(pdi.moveTo, x, y, duration=duration)
    pause_action(pause)


def move_window_relative(
    x: int,
    y: int,
    window_left: int,
    window_top: int,
    duration: float = MOVE_DURATION,
    pause: float = ACTION_DELAY,
) -> None:
    move_absolute(
        int(window_left + x), int(window_top + y), duration=duration, pause=pause
    )


def drag_absolute(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    duration: float = MOVE_DURATION,
    pause: float = ACTION_DELAY,
) -> None:
    timed_action(
        pdi.dragTo,
        int(start_x),
        int(start_y),
        int(end_x),
        int(end_y),
        duration=max(0.0, float(duration)),
    )
    pause_action(pause)


def drag_window_relative(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    window_left: int,
    window_top: int,
    duration: float = MOVE_DURATION,
    pause: float = ACTION_DELAY,
) -> None:
    drag_absolute(
        int(window_left + start_x),
        int(window_top + start_y),
        int(window_left + end_x),
        int(window_top + end_y),
        duration=duration,
        pause=pause,
    )


def open_cell_menu(cell: Cell, window_left: int, window_top: int) -> None:
    """
    Hover the cell, then left-click and right-click to open its context menu.
    """
    abort_if_escape_pressed()
    cx, cy = _cell_screen_center(cell, window_left, window_top)
    timed_action(pdi.moveTo, cx, cy, duration=MOVE_DURATION)
    pause_action()
    timed_action(pdi.leftClick, cx, cy)
    pause_action()
    timed_action(pdi.rightClick, cx, cy)
    pause_action()


def scroll_to_next_grid_at(
    clicks: int,
    grid_center_abs: Tuple[int, int],
    safe_point_abs: Optional[Tuple[int, int]] = None,
) -> None:
    """
    Scroll with the cursor positioned inside the grid to ensure the carousel moves.
    Optionally park the cursor back at a safe point afterwards.
    """
    abort_if_escape_pressed()
    gx, gy = grid_center_abs
    scroll_clicks = -abs(clicks)

    # Match the working standalone script: slow move into position, click, then vertical scroll.
    pdi.moveTo(gx, gy, duration=SCROLL_MOVE_DURATION)
    pause_action()
    abort_if_escape_pressed()
    pdi.leftClick(gx, gy)
    pause_action()

    print(
        f"[scroll] vscroll clicks={scroll_clicks} interval={SCROLL_INTERVAL} at=({gx},{gy})",
        flush=True,
    )
    pdi.vscroll(clicks=scroll_clicks, interval=SCROLL_INTERVAL)
    sleep_with_abort(SCROLL_SETTLE_DELAY)

    if safe_point_abs is not None:
        sx, sy = safe_point_abs
        move_absolute(sx, sy)


def _cell_screen_center(
    cell: Cell, window_left: int, window_top: int
) -> Tuple[int, int]:
    cx, cy = cell.safe_center
    return int(window_left + cx), int(window_top + cy)
