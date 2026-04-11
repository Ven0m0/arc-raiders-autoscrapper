from typing import Any
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import orjson

from autoscrapper.progress.data_loader import GameData
from autoscrapper.progress.decision_engine import DecisionReason
from autoscrapper.progress.rules_generator import (
    _iso_now,
    _to_action,
    generate_rules_from_active,
    write_rules,
)


def test_to_action_keep() -> None:
    reason = DecisionReason(decision="keep", reasons=[])
    assert _to_action(reason) == "keep"


def test_to_action_situational() -> None:
    reason = DecisionReason(decision="situational", reasons=[])
    assert _to_action(reason) == "keep"


def test_to_action_recycle() -> None:
    reason = DecisionReason(decision="sell_or_recycle", reasons=[], recycle_value_exceeds_item=True)
    assert _to_action(reason) == "recycle"


def test_to_action_sell() -> None:
    reason = DecisionReason(decision="sell_or_recycle", reasons=[])
    assert _to_action(reason) == "sell"


def test_iso_now() -> None:
    now = _iso_now()
    assert now.endswith("Z")
    assert "+00:00" not in now
    # Should be parsable
    datetime_str = now.replace("Z", "+00:00")
    from datetime import datetime

    datetime.fromisoformat(datetime_str)


def test_write_rules(tmp_path: Path) -> None:
    output = {"test": "data"}
    file_path = tmp_path / "subdir" / "rules.json"
    write_rules(output, file_path)

    assert file_path.exists()
    content = orjson.loads(file_path.read_bytes())
    assert content == output


@pytest.fixture
def mock_game_data() -> GameData:
    items = [
        {"id": "item1", "name": "Item 1", "value": 100},
        {"id": "item2", "name": "Item 2", "value": 200},
        {"id": "item3", "name": "Item 3", "value": 50},
    ]
    hideout_modules = [
        {
            "id": "module1",
            "name": "Module 1",
            "maxLevel": 1,
            "levels": [{"level": 1, "requirementItemIds": [{"item_id": "item1"}]}],
        }
    ]
    quests = [
        {"id": "quest1", "name": "Quest 1", "trader": "trader1", "requirements": [{"item_id": "item1"}]},
        {"id": "quest2", "name": "Quest 2", "trader": "trader1", "requirements": [{"item_id": "item2"}]},
    ]
    projects: list[dict[str, Any]] = []
    quest_graph: dict[str, object] = {"nodes": {}, "edges": []}
    metadata = {"source": "test", "version": "1.0", "lastUpdated": "2023-01-01T00:00:00Z"}

    return GameData(
        items=items,
        hideout_modules=hideout_modules,
        quests=quests,
        quest_graph=quest_graph,
        projects=projects,
        metadata=metadata,
    )


@patch("autoscrapper.progress.rules_generator.load_game_data")
def test_generate_rules_with_active_quests(mock_load: MagicMock, mock_game_data: GameData) -> None:
    mock_load.return_value = mock_game_data

    result = generate_rules_from_active(active_quests=["Quest 1"], hideout_levels={})

    assert result["metadata"]["itemCount"] == 3
    assert "activeQuests" in result["metadata"]
    assert result["metadata"]["activeQuests"][0]["name"] == "Quest 1"

    # Item 1 is required for active Quest 1 (keep)
    item1_rule = next(item for item in result["items"] if item["id"] == "item1")
    assert item1_rule["action"] == "keep"

    # Item 2 is not required for Quest 1 but it's required for uncompleted Quest 2.
    item2_rule = next(item for item in result["items"] if item["id"] == "item2")
    assert item2_rule["action"] == "keep"

    # Item 3 is completely unused, should be sell
    item3_rule = next(item for item in result["items"] if item["id"] == "item3")
    assert item3_rule["action"] == "sell"


@patch("autoscrapper.progress.rules_generator.load_game_data")
def test_generate_rules_missing_active_quests(mock_load: MagicMock, mock_game_data: GameData) -> None:
    mock_load.return_value = mock_game_data

    with pytest.raises(ValueError, match="Active quests not found: Nonexistent Quest"):
        generate_rules_from_active(active_quests=["Nonexistent Quest"], hideout_levels={})


@patch("autoscrapper.progress.rules_generator.load_game_data")
def test_generate_rules_no_active_quests_no_override(mock_load: MagicMock, mock_game_data: GameData) -> None:
    mock_load.return_value = mock_game_data

    with pytest.raises(ValueError, match="No active quests provided."):
        generate_rules_from_active(active_quests=[], hideout_levels={})


@patch("autoscrapper.progress.rules_generator.load_game_data")
def test_generate_rules_all_quests_completed(mock_load: MagicMock, mock_game_data: GameData) -> None:
    mock_load.return_value = mock_game_data

    result = generate_rules_from_active(active_quests=[], hideout_levels={}, all_quests_completed=True)

    assert result["metadata"].get("allQuestsCompleted") is True
    assert "activeQuests" not in result["metadata"]

    # Since all quests are completed, neither item is needed for quests
    item1_rule = next(item for item in result["items"] if item["id"] == "item1")
    assert item1_rule["action"] == "keep"  # Still kept because of hideout upgrade requirement


@patch("autoscrapper.progress.rules_generator.load_game_data")
def test_generate_rules_completed_quests_override(mock_load: MagicMock, mock_game_data: GameData) -> None:
    mock_load.return_value = mock_game_data

    result = generate_rules_from_active(
        active_quests=[],
        hideout_levels={"module1": 1},  # module 1 upgraded
        completed_quests_override=["quest1", "quest2"],
    )

    # Both quests completed, module upgraded
    item1_rule = next(item for item in result["items"] if item["id"] == "item1")
    item2_rule = next(item for item in result["items"] if item["id"] == "item2")

    assert item1_rule["action"] == "sell"
    assert item2_rule["action"] == "sell"
