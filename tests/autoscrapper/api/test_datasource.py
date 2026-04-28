import pytest
from unittest.mock import patch, MagicMock

from autoscrapper.api.datasource import fetch_stash_as_scan_results
from autoscrapper.api.models import StashData, StashItem
from autoscrapper.config import ApiSettings


@pytest.fixture
def mock_actions():
    return {"matriarch reactor": ["KEEP"], "fabric": ["SELL"], "water": ["RECYCLE"]}


def test_fetch_stash_as_scan_results(mock_actions):
    api_settings = ApiSettings(app_key="test_app", user_key="test_user")

    mock_client = MagicMock()

    mock_stash = StashData(
        used_slots=3,
        items=[
            StashItem(
                item_id="1",
                name="Matriarch Reactor",
                quantity=1,
                slot=0,
                item_type="Refined",
                rarity="Common",
                value=100,
            ),
            StashItem(item_id="2", name="Fabric", quantity=5, slot=1, item_type="Material", rarity="Common", value=10),
            StashItem(item_id="3", name="Water", quantity=1, slot=2, item_type="Material", rarity="Common", value=0),
            StashItem(
                item_id="4", name="Unknown Item", quantity=1, slot=3, item_type="Other", rarity="Common", value=0
            ),
        ],
    )
    mock_client.get_all_stash_items.return_value = mock_stash

    with patch("autoscrapper.api.datasource.ArcTrackerClient", return_value=mock_client):
        results, stats = fetch_stash_as_scan_results(mock_actions, api_settings=api_settings)

    assert len(results) == 4

    assert results[0].item_name == "Matriarch Reactor"
    assert results[0].decision == "KEEP"
    assert results[0].action_taken == "skipped"

    assert results[1].item_name == "Fabric"
    assert results[1].decision == "SELL"
    assert results[1].action_taken == "sell"
    assert results[1].note == "Qty: 5"

    assert results[2].item_name == "Water"
    assert results[2].decision == "RECYCLE"
    assert results[2].action_taken == "recycle"

    assert results[3].item_name == "Unknown Item"
    assert results[3].decision is None
    assert results[3].action_taken == "no-action"

    assert stats.items_in_stash == 3
    assert stats.stash_count_text == "3"


def test_fetch_stash_as_scan_results_api_error(mock_actions):
    api_settings = ApiSettings(app_key="test_app", user_key="test_user")

    mock_client = MagicMock()
    mock_client.get_all_stash_items.return_value = StashData(api_error="Connection failed")

    with patch("autoscrapper.api.datasource.ArcTrackerClient", return_value=mock_client):
        results, stats = fetch_stash_as_scan_results(mock_actions, api_settings=api_settings)

    assert results == []
    assert stats.items_in_stash is None
    assert stats.stash_count_text == "api-error"


def test_fetch_stash_as_scan_results_dry_run(mock_actions):
    api_settings = ApiSettings(app_key="test_app", user_key="test_user")

    mock_client = MagicMock()
    mock_stash = StashData(
        used_slots=1,
        items=[
            StashItem(item_id="1", name="Fabric", quantity=1, slot=0, item_type="Material", rarity="Common", value=10),
        ],
    )
    mock_client.get_all_stash_items.return_value = mock_stash

    with patch("autoscrapper.api.datasource.ArcTrackerClient", return_value=mock_client):
        results, stats = fetch_stash_as_scan_results(mock_actions, api_settings=api_settings, dry_run=True)

    assert len(results) == 1
    assert results[0].item_name == "Fabric"
    assert results[0].decision == "SELL"
    assert results[0].action_taken == "dry-run"
