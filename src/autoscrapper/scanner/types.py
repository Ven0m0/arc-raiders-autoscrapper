from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ScanStats:
    """
    Aggregate metrics for the scan useful for reporting.
    """

    items_in_stash: int | None
    stash_count_text: str
    pages_planned: int
    pages_scanned: int
    processing_seconds: float
