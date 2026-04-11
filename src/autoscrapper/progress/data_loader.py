from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import orjson

from .quest_overrides import apply_quest_overrides

DATA_DIR = Path(__file__).resolve().parent / "data"


@dataclass(frozen=True, slots=True)
class GameData:
    items: list[dict]
    hideout_modules: list[dict]
    quests: list[dict]
    quest_graph: dict[str, Any]
    projects: list[dict]
    metadata: dict[str, str]


def _read_json(path: Path) -> Any:
    return orjson.loads(path.read_bytes())


def load_game_data(data_dir: Path | None = None) -> GameData:
    data_dir = data_dir or DATA_DIR

    items_path = data_dir / "items.json"
    quests_path = data_dir / "quests.json"
    quest_graph_path = data_dir / "quests_graph.json"
    hideout_modules_path = data_dir / "static" / "hideout_modules.json"
    projects_path = data_dir / "static" / "projects.json"
    metadata_path = data_dir / "metadata.json"

    if not items_path.exists() or not quests_path.exists() or not quest_graph_path.exists():
        raise FileNotFoundError(f"Missing data snapshot. Expected {items_path}, {quests_path}, and {quest_graph_path}.")

    items = _read_json(items_path)
    quests = apply_quest_overrides(_read_json(quests_path))
    quest_graph = _read_json(quest_graph_path)
    hideout_modules = _read_json(hideout_modules_path)
    projects = _read_json(projects_path)

    metadata: dict | None = None
    if metadata_path.exists():
        try:
            metadata = _read_json(metadata_path)
        except Exception:
            metadata = {}
    if metadata is None:
        metadata = {}

    return GameData(
        items=items if isinstance(items, list) else [],
        hideout_modules=hideout_modules if isinstance(hideout_modules, list) else [],
        quests=quests if isinstance(quests, list) else [],
        quest_graph=quest_graph if isinstance(quest_graph, dict) else {},
        projects=projects if isinstance(projects, list) else [],
        metadata=metadata if isinstance(metadata, dict) else {},
    )
