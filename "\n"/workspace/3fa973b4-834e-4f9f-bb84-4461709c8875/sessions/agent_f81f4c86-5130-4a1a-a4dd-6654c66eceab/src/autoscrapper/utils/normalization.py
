"""Shared normalization utilities for quest names and other text."""

from __future__ import annotations

import re
from typing import Any


def normalize_quest_name(value: str | Any) -> str:
    """
    Normalize a quest name for comparison and lookup.

    This function is used across multiple modules to ensure consistent
    quest name normalization. It performs the following operations:
    1. Converts to lowercase
    2. Removes apostrophes and right single quotation marks
    3. Replaces non-alphanumeric characters with spaces
    4. Collapses multiple spaces into one
    5. Strips leading/trailing whitespace

    Args:
        value: The quest name to normalize. If not a string, it's converted to one.

    Returns:
        The normalized quest name.
    """
    normalized = str(value or "").lower().replace("'", "").replace("\u2019", "")
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def normalize_text(value: Any) -> str:
    """Normalize arbitrary text by stripping whitespace."""
    if not isinstance(value, str):
        return ""
    return value.strip()
