from __future__ import annotations

_UNREADABLE_REASONS: dict[str, str] = {
    "UNREADABLE_NO_INFOBOX": "infobox missing",
    "UNREADABLE_NO_OCR": "ocr not run",
    "UNREADABLE_OCR_FAILED": "ocr failed",
    "UNREADABLE_TITLE": "title unreadable",
}

_SKIP_REASONS: dict[str, str] = {
    "SKIP_NO_NAME": "missing OCR name",
    "SKIP_NO_ACTION_MAP": "no action map loaded",
    "SKIP_UNLISTED": "no configured decision",
    "SKIP_NO_ACTION_BBOX": "action not found in item infobox",
    "SKIP_NO_INFOBOX": "infobox missing",
}


def _describe_action(action_taken: str) -> tuple[str, list[str]]:
    """
    Normalize the action label (for display) and attach human-readable details.
    """
    details: list[str] = []
    if action_taken.startswith("SKIP_"):
        reason = _SKIP_REASONS.get(action_taken, action_taken.removeprefix("SKIP_").replace("_", " ").lower())
        details.append(reason)
        return "SKIP", details

    if action_taken.startswith("UNREADABLE_"):
        reason = _UNREADABLE_REASONS.get(
            action_taken,
            action_taken.removeprefix("UNREADABLE_").replace("_", " ").lower(),
        )
        details.append(reason)
        return "UNREADABLE", details

    if action_taken.startswith("DRY_RUN_"):
        base = action_taken.removeprefix("DRY_RUN_")
        details.append("dry run")
        return f"DRY-{base}", details

    return action_taken, details


def _outcome_style(label: str) -> str:
    base = label.replace("DRY-", "")
    return {
        "KEEP": "green",
        "RECYCLE": "cyan",
        "SELL": "magenta",
        "UNREADABLE": "yellow",
        "SKIP": "red",
    }.get(base, "white")
