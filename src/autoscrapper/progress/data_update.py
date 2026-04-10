from __future__ import annotations

import json
import logging
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .data_loader import DATA_DIR
from .quest_overrides import apply_quest_overrides

_log = logging.getLogger(__name__)

METAFORGE_API_BASE = "https://metaforge.app/api/arc-raiders"
SUPABASE_URL = "https://unhbvkszwhczbjxgetgk.supabase.co/rest/v1"

SUPABASE_ANON_KEY = os.environ.get("METAFORGE_SUPABASE_ANON_KEY")


class DownloadError(RuntimeError):
    pass


def _fetch_json(url: str, headers: dict[str, str] | None = None) -> object:
    request_headers = {
        "Accept": "application/json",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/132.0.0.0 Safari/537.36"
        ),
    }
    if headers:
        request_headers.update(headers)

    req = Request(url, headers=request_headers)
    try:
        with urlopen(req, timeout=30) as resp:
            payload = resp.read().decode("utf-8")
            return json.loads(payload)
    except HTTPError as exc:
        raise DownloadError(f"HTTP {exc.code} for {url}") from exc
    except URLError as exc:
        raise DownloadError(f"Failed to reach {url}: {exc}") from exc


def _fetch_all_items() -> list[dict]:
    items: list[dict] = []
    current_page = 1
    has_next = True
    limit = 100

    while has_next:
        url = f"{METAFORGE_API_BASE}/items?page={current_page}&limit={limit}"
        response = _fetch_json(url)
        if not isinstance(response, dict):
            raise DownloadError("Unexpected response for items")
        data = response.get("data") or []
        if isinstance(data, list):
            items.extend(data)
        pagination = response.get("pagination") or {}
        has_next = bool(pagination.get("hasNextPage"))
        current_page += 1
        if has_next:
            time.sleep(0.1)

    return items


def _fetch_all_quests() -> list[dict]:
    quests: list[dict] = []
    current_page = 1
    has_next = True
    limit = 100

    while has_next:
        url = f"{METAFORGE_API_BASE}/quests?page={current_page}&limit={limit}"
        response = _fetch_json(url)
        if not isinstance(response, dict):
            raise DownloadError("Unexpected response for quests")
        data = response.get("data") or []
        if isinstance(data, list):
            quests.extend(data)
        pagination = response.get("pagination") or {}
        has_next = bool(pagination.get("hasNextPage"))
        current_page += 1
        if has_next:
            time.sleep(0.1)

    return quests


def _fetch_supabase_all(table: str) -> list[dict]:
    if not SUPABASE_ANON_KEY:
        raise DownloadError(
            "METAFORGE_SUPABASE_ANON_KEY environment variable is not set"
        )

    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    }
    page_size = 1000
    offset = 0
    all_rows: list[dict] = []

    while True:
        url = f"{SUPABASE_URL}/{table}?select=*&limit={page_size}&offset={offset}"
        batch = _fetch_json(url, headers=headers)
        if not isinstance(batch, list):
            raise DownloadError(f"Unexpected response for {table}: expected array")
        all_rows.extend(batch)
        if len(batch) < page_size:
            break
        offset += page_size
        time.sleep(0.1)

    return all_rows


def _build_component_map(components: list[dict]) -> dict[str, dict[str, int]]:
    component_map: dict[str, dict[str, int]] = {}
    for component in components:
        item_id = component.get("item_id")
        component_id = component.get("component_id")
        quantity = component.get("quantity")
        if not item_id or not component_id or quantity is None:
            continue
        component_map.setdefault(item_id, {})[component_id] = int(quantity)
    return component_map


def _map_metaforge_item(
    metaforge_item: dict,
    crafting_map: dict[str, dict[str, int]],
    recycle_map: dict[str, dict[str, int]],
) -> dict:
    stat_block = metaforge_item.get("stat_block") or {}
    return {
        "id": metaforge_item.get("id"),
        "name": metaforge_item.get("name"),
        "type": metaforge_item.get("item_type") or "Unknown",
        "rarity": (
            str(metaforge_item.get("rarity")).lower()
            if metaforge_item.get("rarity")
            else None
        ),
        "value": metaforge_item.get("value") or 0,
        "weightKg": stat_block.get("weight") or 0,
        "stackSize": stat_block.get("stackSize") or 1,
        "craftBench": metaforge_item.get("workbench") or None,
        "updatedAt": metaforge_item.get("updated_at")
        or datetime.now(UTC).isoformat(),
        "recipe": crafting_map.get(metaforge_item.get("id")) or None,
        "recyclesInto": recycle_map.get(metaforge_item.get("id")) or None,
    }


def _map_metaforge_quest(metaforge_quest: dict) -> dict:
    position = metaforge_quest.get("position") or {}
    sort_order = position.get("y", metaforge_quest.get("sort_order", 0))

    required_items = metaforge_quest.get("required_items") or []
    rewards = metaforge_quest.get("rewards") or []

    reward_item_ids: list[str] = []
    if isinstance(rewards, list):
        for reward in rewards:
            reward_item_id: str | None = None
            if isinstance(reward, dict):
                reward_item_id = reward.get("item_id")
                if not reward_item_id:
                    reward_item = reward.get("item")
                    if isinstance(reward_item, dict):
                        reward_item_id = reward_item.get("id")
                    elif isinstance(reward_item, str):
                        reward_item_id = reward_item
            elif isinstance(reward, str):
                reward_item_id = reward

            if isinstance(reward_item_id, str) and reward_item_id:
                reward_item_ids.append(reward_item_id)

    # Keep IDs stable while removing duplicates.
    reward_item_ids = list(dict.fromkeys(reward_item_ids))

    return {
        "id": metaforge_quest.get("id"),
        "name": metaforge_quest.get("name"),
        "objectives": metaforge_quest.get("objectives") or [],
        "requirements": required_items,
        "rewardItemIds": reward_item_ids,
        "rewards": rewards,
        "trader": metaforge_quest.get("trader_name") or "Unknown",
        "xp": metaforge_quest.get("xp") or 0,
        "sortOrder": sort_order,
    }


def _build_quests_by_trader(quests: list[dict]) -> dict[str, list[dict]]:
    by_trader: dict[str, list[dict]] = {}
    for quest in quests:
        trader = quest.get("trader") or "Unknown"
        by_trader.setdefault(trader, []).append(
            {
                "id": quest.get("id"),
                "name": quest.get("name"),
                "sortOrder": quest.get("sortOrder", 0),
            }
        )

    for trader, quests_list in by_trader.items():
        quests_list.sort(key=lambda q: q.get("sortOrder") or 0)

    return by_trader


def update_data_snapshot(data_dir: Path | None = None) -> dict:
    data_dir = data_dir or DATA_DIR
    (data_dir / "static").mkdir(parents=True, exist_ok=True)

    metaforge_items = _fetch_all_items()
    metaforge_quests = _fetch_all_quests()

    try:
        components = _fetch_supabase_all("arc_item_components")
    except DownloadError as exc:
        _log.warning("Skipping crafting component data (Supabase unavailable): %s", exc)
        components = []
    try:
        recycle_components = _fetch_supabase_all("arc_item_recycle_components")
    except DownloadError as exc:
        _log.warning("Skipping recycle component data (Supabase unavailable): %s", exc)
        recycle_components = []

    crafting_map = _build_component_map(components)
    recycle_map = _build_component_map(recycle_components)

    mapped_items = [
        _map_metaforge_item(item, crafting_map, recycle_map) for item in metaforge_items
    ]
    mapped_quests = [_map_metaforge_quest(quest) for quest in metaforge_quests]
    mapped_quests = apply_quest_overrides(mapped_quests)

    (data_dir / "items.json").write_text(
        json.dumps(mapped_items, indent=2), encoding="utf-8"
    )
    (data_dir / "quests.json").write_text(
        json.dumps(mapped_quests, indent=2), encoding="utf-8"
    )

    quests_by_trader = {
        "generatedAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "source": "quests.json",
        "traders": _build_quests_by_trader(mapped_quests),
    }
    (data_dir / "quests_by_trader.json").write_text(
        json.dumps(quests_by_trader, indent=2), encoding="utf-8"
    )

    metadata = {
        "lastUpdated": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "source": "https://metaforge.app/arc-raiders",
        "version": "autoscrapper-data-1",
        "itemCount": len(mapped_items),
        "questCount": len(mapped_quests),
        # Kept for compatibility with older metadata consumers.
        "hasPriceOverrides": False,
    }
    (data_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )

    return metadata
