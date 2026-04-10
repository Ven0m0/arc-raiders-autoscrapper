from __future__ import annotations

import importlib
import threading
from dataclasses import dataclass
from typing import Optional

_WARMUP_LOCK = threading.Lock()
_WARMUP_DONE = threading.Event()
_WARMUP_STARTED = False
_WARMUP_ERROR: Optional[str] = None

_HEAVY_MODULES = (
    # Only modules that do NOT transitively import tesserocr are safe to
    # pre-import in a background thread.  tesserocr pulls in cysignals, which
    # installs OS signal handlers and requires the main thread.
    # Modules excluded for that reason:
    #   autoscrapper.ocr.inventory_vision  (→ tesseract → tesserocr)
    #   autoscrapper.scanner.scan_loop     (→ inventory_vision → tesserocr)
    #   autoscrapper.scanner.engine        (→ scan_loop → tesserocr)
    "autoscrapper.core.item_actions",
    "autoscrapper.interaction.ui_windows",
)


@dataclass(frozen=True)
class WarmupStatus:
    started: bool
    completed: bool
    failed: bool
    error: Optional[str]


def _set_warmup_error(error: Optional[str]) -> None:
    global _WARMUP_ERROR
    with _WARMUP_LOCK:
        _WARMUP_ERROR = error


def _get_warmup_error() -> Optional[str]:
    with _WARMUP_LOCK:
        return _WARMUP_ERROR


def _run_background_warmup() -> None:
    try:
        for module_name in _HEAVY_MODULES:
            importlib.import_module(module_name)
        # initialize_ocr() is intentionally NOT called here: tesserocr imports
        # cysignals which installs signal handlers, and signal handlers can only
        # be installed from the main thread.  OCR is lazily initialised on first
        # use (on the main thread) via the _get_api() lock in tesseract.py.
    except Exception as exc:  # pragma: no cover - defensive warmup fallback
        _set_warmup_error(f"{type(exc).__name__}: {exc}")
    finally:
        _WARMUP_DONE.set()


def start_background_warmup() -> None:
    global _WARMUP_STARTED
    with _WARMUP_LOCK:
        if _WARMUP_STARTED:
            return
        _WARMUP_STARTED = True
        thread = threading.Thread(
            target=_run_background_warmup,
            name="autoscrapper-warmup",
            daemon=True,
        )
        thread.start()


def warmup_status() -> WarmupStatus:
    with _WARMUP_LOCK:
        started = _WARMUP_STARTED
    error = _get_warmup_error()
    completed = _WARMUP_DONE.is_set()
    return WarmupStatus(
        started=started,
        completed=completed,
        failed=error is not None,
        error=error,
    )
