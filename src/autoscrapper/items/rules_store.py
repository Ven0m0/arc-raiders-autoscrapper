from __future__ import annotations

from pathlib import Path

import orjson
from ..core.item_actions import clean_ocr_text

_ITEM_NAMES: tuple[str, ...] | None = None


def get_item_names() -> tuple[str, ...]:
    global _ITEM_NAMES
    if _ITEM_NAMES is not None:
        return _ITEM_NAMES

    payload = load_rules()
    names: list[str] = []
    seen: set[str] = set()
    for entry in payload.get("items", []):
        if not isinstance(entry, dict):
            continue
        name = entry.get("name")
        if not isinstance(name, str):
            continue
        cleaned = clean_ocr_text(name)
        key = cleaned.casefold()
        if not cleaned or key in seen:
            continue
        seen.add(key)
        names.append(cleaned)

    _ITEM_NAMES = tuple(names)
    return _ITEM_NAMES


def reset_item_names_cache() -> None:
    global _ITEM_NAMES
    _ITEM_NAMES = None


DEFAULT_RULES_PATH = Path(__file__).with_name("items_rules.default.json")
CUSTOM_RULES_PATH = Path(__file__).with_name("items_rules.custom.json")


def active_rules_path() -> Path:
    return CUSTOM_RULES_PATH if CUSTOM_RULES_PATH.exists() else DEFAULT_RULES_PATH


def using_custom_rules() -> bool:
    return CUSTOM_RULES_PATH.exists()


def _coerce_payload(raw: object) -> dict:
    if isinstance(raw, dict):
        items = raw.get("items")
        if not isinstance(items, list):
            items = []
        metadata = raw.get("metadata") if isinstance(raw.get("metadata"), dict) else {}
        return {"metadata": metadata, "items": items}

    if isinstance(raw, list):
        return {"metadata": {}, "items": raw}

    return {"metadata": {}, "items": []}


def load_rules(path: Path | None = None) -> dict:
    rules_path = path or active_rules_path()
    if not rules_path.exists():
        return {"metadata": {}, "items": []}
    raw = orjson.loads(rules_path.read_bytes())
    return _coerce_payload(raw)


def save_rules(payload: dict, path: Path) -> None:
    items = payload.get("items")
    if not isinstance(items, list):
        items = []
    metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    metadata["itemCount"] = len(items)
    payload = {"metadata": metadata, "items": items}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(orjson.dumps(payload, option=orjson.OPT_INDENT_2))


def save_custom_rules(payload: dict) -> None:
    save_rules(payload, CUSTOM_RULES_PATH)


def normalize_action(value: str) -> str | None:
    raw = value.strip().lower()
    if raw in {"k", "keep"}:
        return "keep"
    if raw in {"s", "sell"}:
        return "sell"
    if raw in {"r", "recycle"}:
        return "recycle"
    return None
