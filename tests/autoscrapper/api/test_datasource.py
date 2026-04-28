from unittest.mock import patch, MagicMock

from autoscrapper.api.datasource import get_data_source, APIDataSource
from autoscrapper.config import ApiSettings


def test_get_data_source_not_api():
    result = get_data_source("ocr", {})
    assert result is None


@patch("autoscrapper.api.datasource.load_api_settings")
@patch("autoscrapper.api.datasource.ArcTrackerClient")
def test_get_data_source_not_configured(mock_client_class, mock_load_settings):
    mock_settings = ApiSettings(app_key="", user_key="")
    mock_load_settings.return_value = mock_settings

    mock_client = MagicMock()
    mock_client.is_configured.return_value = False
    mock_client_class.return_value = mock_client

    result = get_data_source("api", {})

    assert result is None
    mock_client.is_configured.assert_called_once()


@patch("autoscrapper.api.datasource.ArcTrackerClient")
def test_get_data_source_configured(mock_client_class):
    mock_settings = ApiSettings(app_key="test_app", user_key="test_user", base_url="https://test.local")

    mock_client = MagicMock()
    mock_client.is_configured.return_value = True
    mock_client_class.return_value = mock_client

    actions = {"test_item": ["KEEP"]}

    result = get_data_source("api", actions, api_settings=mock_settings, dry_run=True)

    assert result is not None
    assert isinstance(result, APIDataSource)
    assert result.client == mock_client
    assert result.actions == actions
    assert result.dry_run is True

    mock_client_class.assert_called_once_with(app_key="test_app", user_key="test_user", base_url="https://test.local")


@patch("autoscrapper.api.datasource.load_api_settings")
@patch("autoscrapper.api.datasource.ArcTrackerClient")
def test_get_data_source_default_settings(mock_client_class, mock_load_settings):
    mock_settings = ApiSettings(app_key="default_app", user_key="default_user", base_url="https://arctracker.io")
    mock_load_settings.return_value = mock_settings

    mock_client = MagicMock()
    mock_client.is_configured.return_value = True
    mock_client_class.return_value = mock_client

    result = get_data_source("api", {})

    assert result is not None
    mock_load_settings.assert_called_once()
    mock_client_class.assert_called_once_with(
        app_key="default_app", user_key="default_user", base_url="https://arctracker.io"
    )
