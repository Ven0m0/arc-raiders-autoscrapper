"""Tests for ArcTracker API datasource functions."""

import pytest
from unittest.mock import patch, MagicMock

from autoscrapper.api.datasource import sync_hideout_to_progress
from autoscrapper.api.models import HideoutModule
from autoscrapper.config import ApiSettings, ProgressSettings


@pytest.fixture
def mock_api_settings():
    return ApiSettings(
        app_key="test_app",
        user_key="test_user",
        enabled=True,
        prefer_api=True,
        base_url="https://arctracker.io"
    )

@pytest.fixture
def mock_progress_settings():
    return ProgressSettings(
        all_quests_completed=False,
        active_quests=["Quest1"],
        completed_quests=[],
        hideout_levels={"generator": 1},
        last_updated="2023-01-01T00:00:00Z"
    )


@patch("autoscrapper.api.datasource.load_progress_settings")
@patch("autoscrapper.api.datasource.save_progress_settings")
@patch("autoscrapper.api.datasource.ArcTrackerClient")
def test_sync_hideout_not_configured(mock_client_class, mock_save, mock_load, mock_api_settings, mock_progress_settings):
    """Test behavior when API client is not configured."""
    # Setup mock client
    mock_client = MagicMock()
    mock_client.is_configured.return_value = False
    mock_client_class.return_value = mock_client

    mock_load.return_value = mock_progress_settings

    result = sync_hideout_to_progress(mock_api_settings)

    assert result == mock_progress_settings
    mock_save.assert_not_called()
    mock_client.get_user_hideout.assert_not_called()


@patch("autoscrapper.api.datasource.load_progress_settings")
@patch("autoscrapper.api.datasource.save_progress_settings")
@patch("autoscrapper.api.datasource.ArcTrackerClient")
def test_sync_hideout_no_data(mock_client_class, mock_save, mock_load, mock_api_settings, mock_progress_settings):
    """Test behavior when API returns no hideout data."""
    # Setup mock client
    mock_client = MagicMock()
    mock_client.is_configured.return_value = True
    mock_client.get_user_hideout.return_value = []
    mock_client_class.return_value = mock_client

    mock_load.return_value = mock_progress_settings

    result = sync_hideout_to_progress(mock_api_settings)

    assert result == mock_progress_settings
    mock_save.assert_not_called()
    mock_client.get_user_hideout.assert_called_once()


@patch("autoscrapper.api.datasource.load_progress_settings")
@patch("autoscrapper.api.datasource.save_progress_settings")
@patch("autoscrapper.api.datasource.ArcTrackerClient")
def test_sync_hideout_success(mock_client_class, mock_save, mock_load, mock_api_settings, mock_progress_settings):
    """Test successful sync of hideout modules."""
    # Setup mock client
    mock_client = MagicMock()
    mock_client.is_configured.return_value = True

    mock_modules = [
        HideoutModule(module_id="generator", name="Generator", current_level=2, max_level=3),
        HideoutModule(module_id="workbench", name="Workbench", current_level=1, max_level=3)
    ]
    mock_client.get_user_hideout.return_value = mock_modules
    mock_client_class.return_value = mock_client

    mock_load.return_value = mock_progress_settings

    result = sync_hideout_to_progress(mock_api_settings)

    # Check that settings were saved
    mock_save.assert_called_once()
    saved_settings = mock_save.call_args[0][0]

    # Verify levels were updated
    assert saved_settings.hideout_levels["generator"] == 2
    assert saved_settings.hideout_levels["workbench"] == 1

    # Verify other settings were preserved
    assert saved_settings.active_quests == mock_progress_settings.active_quests
    assert saved_settings.all_quests_completed == mock_progress_settings.all_quests_completed

    # Verify the returned result is the same as the saved one
    assert result == saved_settings


@patch("autoscrapper.api.datasource.load_api_settings")
@patch("autoscrapper.api.datasource.load_progress_settings")
@patch("autoscrapper.api.datasource.save_progress_settings")
@patch("autoscrapper.api.datasource.ArcTrackerClient")
def test_sync_hideout_uses_loaded_settings_when_none(mock_client_class, mock_save, mock_load_progress, mock_load_api, mock_api_settings, mock_progress_settings):
    """Test that it loads api settings if none are provided."""
    mock_load_api.return_value = mock_api_settings

    # Setup mock client to fail early so we just test loading settings
    mock_client = MagicMock()
    mock_client.is_configured.return_value = False
    mock_client_class.return_value = mock_client

    mock_load_progress.return_value = mock_progress_settings

    sync_hideout_to_progress(None)

    mock_load_api.assert_called_once()
    mock_client_class.assert_called_once_with(
        app_key=mock_api_settings.app_key,
        user_key=mock_api_settings.user_key,
        base_url=mock_api_settings.base_url
    )
