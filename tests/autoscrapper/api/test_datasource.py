"""Tests for ArcTracker API datasource functions."""

import pytest
from unittest.mock import patch, MagicMock
from typing import cast

from autoscrapper.api.datasource import (
    fetch_stash_as_scan_results,
    sync_hideout_to_progress,
    get_data_source,
    APIDataSource,
)
from autoscrapper.api.models import StashData, StashItem, HideoutModule
from autoscrapper.config import ApiSettings, ProgressSettings
from autoscrapper.core.item_actions import ActionMap


@pytest.fixture
def mock_actions():
    return {"matriarch reactor": ["KEEP"], "fabric": ["SELL"], "water": ["RECYCLE"]}


@pytest.fixture
def mock_api_settings():
    return ApiSettings(
        app_key="test_app", user_key="test_user", enabled=True, prefer_api=True, base_url="https://arctracker.io"
    )


@pytest.fixture
def mock_progress_settings():
    return ProgressSettings(
        all_quests_completed=False,
        active_quests=["Quest1"],
        completed_quests=[],
        hideout_levels={"generator": 1},
        last_updated="2023-01-01T00:00:00Z",
    )


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
    assert results[1].item_name == "Fabric"
    assert results[1].decision == "SELL"
    assert results[2].item_name == "Water"
    assert results[2].decision == "RECYCLE"
    assert results[3].item_name == "Unknown Item"
    assert results[3].decision is None
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
            StashItem(item_id="1", name="Fabric", quantity=1, slot=0, item_type="Material", rarity="Common", value=10)
        ],
    )
    mock_client.get_all_stash_items.return_value = mock_stash

    with patch("autoscrapper.api.datasource.ArcTrackerClient", return_value=mock_client):
        results, stats = fetch_stash_as_scan_results(mock_actions, api_settings=api_settings, dry_run=True)

    assert len(results) == 1
    assert results[0].item_name == "Fabric"
    assert results[0].action_taken == "dry-run"


@patch("autoscrapper.api.datasource.load_progress_settings")
@patch("autoscrapper.api.datasource.save_progress_settings")
@patch("autoscrapper.api.datasource.ArcTrackerClient")
def test_sync_hideout_not_configured(
    mock_client_class, mock_save, mock_load, mock_api_settings, mock_progress_settings
):
    mock_client = MagicMock()
    mock_client.is_configured.return_value = False
    mock_client_class.return_value = mock_client
    mock_load.return_value = mock_progress_settings

    result = sync_hideout_to_progress(mock_api_settings)

    assert result == mock_progress_settings
    mock_save.assert_not_called()


@patch("autoscrapper.api.datasource.load_progress_settings")
@patch("autoscrapper.api.datasource.save_progress_settings")
@patch("autoscrapper.api.datasource.ArcTrackerClient")
def test_sync_hideout_success(mock_client_class, mock_save, mock_load, mock_api_settings, mock_progress_settings):
    mock_client = MagicMock()
    mock_client.is_configured.return_value = True
    mock_modules = [
        HideoutModule(module_id="generator", name="Generator", current_level=2, max_level=3),
        HideoutModule(module_id="workbench", name="Workbench", current_level=1, max_level=3),
    ]
    mock_client.get_user_hideout.return_value = mock_modules
    mock_client_class.return_value = mock_client
    mock_load.return_value = mock_progress_settings

    _ = sync_hideout_to_progress(mock_api_settings)

    mock_save.assert_called_once()
    saved_settings = mock_save.call_args[0][0]
    assert saved_settings.hideout_levels["generator"] == 2
    assert saved_settings.hideout_levels["workbench"] == 1


def test_get_data_source_not_api():
    result = get_data_source("ocr", cast(ActionMap, {}))
    assert result is None


@patch("autoscrapper.api.datasource.load_api_settings")
@patch("autoscrapper.api.datasource.ArcTrackerClient")
def test_get_data_source_not_configured(mock_client_class, mock_load_settings):
    mock_settings = ApiSettings(app_key="", user_key="")
    mock_load_settings.return_value = mock_settings
    mock_client = MagicMock()
    mock_client.is_configured.return_value = False
    mock_client_class.return_value = mock_client

    result = get_data_source("api", cast(ActionMap, {}))

    assert result is None


@patch("autoscrapper.api.datasource.ArcTrackerClient")
def test_get_data_source_configured(mock_client_class):
    mock_settings = ApiSettings(app_key="test_app", user_key="test_user", base_url="https://test.local")
    mock_client = MagicMock()
    mock_client.is_configured.return_value = True
    mock_client_class.return_value = mock_client

    actions: ActionMap = {"test_item": ["KEEP"]}
    result = get_data_source("api", actions, api_settings=mock_settings, dry_run=True)

    assert result is not None
    assert isinstance(result, APIDataSource)
    assert result.client == mock_client
    assert result.dry_run is True


@patch("autoscrapper.api.datasource.load_api_settings")
@patch("autoscrapper.api.datasource.ArcTrackerClient")
def test_get_data_source_default_settings(mock_client_class, mock_load_settings):
    mock_settings = ApiSettings(app_key="default_app", user_key="default_user", base_url="https://arctracker.io")
    mock_load_settings.return_value = mock_settings
    mock_client = MagicMock()
    mock_client.is_configured.return_value = True
    mock_client_class.return_value = mock_client

    result = get_data_source("api", cast(ActionMap, {}))

    assert result is not None
