import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from autoscrapper.config import CONFIG_VERSION, _load_config_dict, _migrate_config


def test_migrate_config_no_version():
    """Test that a payload without a version is returned as-is."""
    payload = {"some_key": "some_value"}
    result = _migrate_config(payload.copy())
    assert result == payload


def test_migrate_config_non_integer_version():
    """Test that a payload with a non-integer version is returned as-is."""
    payload = {"version": "1.0", "some_key": "some_value"}
    result = _migrate_config(payload.copy())
    assert result == payload


def test_migrate_config_current_version():
    """Test that a payload with the current version is returned as-is."""
    payload = {"version": CONFIG_VERSION, "some_key": "some_value"}
    result = _migrate_config(payload.copy())
    assert result == payload


def test_migrate_config_future_version():
    """Test that a payload with a future version is returned as-is, but a warning is logged."""
    payload = {"version": CONFIG_VERSION + 1, "some_key": "some_value"}
    result = _migrate_config(payload.copy())
    assert result == payload


def test_migrate_config_old_version():
    """Test that a payload with an old version is migrated to the current version."""
    # Assuming CONFIG_VERSION is at least 1 and we migrate from 1
    # We will test a version older than current
    if CONFIG_VERSION > 1:
        payload = {"version": 1, "some_key": "some_value"}
        result = _migrate_config(payload.copy())
        assert result["version"] == CONFIG_VERSION
        assert result["some_key"] == "some_value"


@patch("autoscrapper.config._log.warning")
def test_migrate_config_future_version_warning(mock_warning):
    """Test that a warning is logged for future versions."""
    future_version = CONFIG_VERSION + 1
    payload = {"version": future_version, "some_key": "some_value"}
    _migrate_config(payload.copy())
    mock_warning.assert_called_once()
    assert "newer than current code version" in mock_warning.call_args[0][0]
    assert mock_warning.call_args[0][1] == future_version
    assert mock_warning.call_args[0][2] == CONFIG_VERSION


def migrate_1_to_2(payload):
    payload["step_1_applied"] = True
    return payload


def migrate_2_to_3(payload):
    payload["step_2_applied"] = True
    return payload


def migrate_3_to_4(payload):
    payload["step_3_applied"] = True
    return payload


dummy_migrations = {
    1: migrate_1_to_2,
    2: migrate_2_to_3,
    3: migrate_3_to_4,
}


@patch("autoscrapper.config._MIGRATIONS", new=dummy_migrations)
@patch("autoscrapper.config.CONFIG_VERSION", 4)
def test_migrate_config_applies_all_steps():
    """Test that all migration steps are applied sequentially up to CONFIG_VERSION."""
    payload = {"version": 1}
    result = _migrate_config(payload)

    assert result["version"] == 4
    assert result.get("step_1_applied") is True
    assert result.get("step_2_applied") is True
    assert result.get("step_3_applied") is True


@patch("autoscrapper.config.config_path")
def test_load_config_dict_file_not_found(mock_config_path):
    """Test that _load_config_dict returns an empty dict if the file is not found."""
    mock_path = MagicMock(spec=Path)
    mock_path.read_text.side_effect = FileNotFoundError()
    mock_config_path.return_value = mock_path

    result = _load_config_dict()
    assert result == {}


@patch("autoscrapper.config.config_path")
def test_load_config_dict_json_decode_error(mock_config_path):
    """Test that _load_config_dict returns an empty dict if the file contains invalid JSON."""
    mock_path = MagicMock(spec=Path)
    mock_path.read_text.return_value = "invalid json"
    mock_config_path.return_value = mock_path

    # json.loads will raise JSONDecodeError
    result = _load_config_dict()
    assert result == {}


@patch("autoscrapper.config.config_path")
def test_load_config_dict_os_error(mock_config_path):
    """Test that _load_config_dict returns an empty dict if an OSError occurs."""
    mock_path = MagicMock(spec=Path)
    mock_path.read_text.side_effect = OSError("Read error")
    mock_config_path.return_value = mock_path

    result = _load_config_dict()
    assert result == {}


@patch("autoscrapper.config.config_path")
def test_load_config_dict_not_a_dict(mock_config_path):
    """Test that _load_config_dict returns an empty dict if the JSON is not a dictionary."""
    mock_path = MagicMock(spec=Path)
    mock_path.read_text.return_value = "[1, 2, 3]"
    mock_config_path.return_value = mock_path

    result = _load_config_dict()
    assert result == {}


@patch("autoscrapper.config.config_path")
@patch("autoscrapper.config.config_path")
def test_load_config_dict_success(mock_config_path):
    """Test that _load_config_dict returns the loaded dictionary and applies migrations."""
    # Use an older version to verify migration is applied
    payload = {"version": 1, "scan": {"debug_ocr": True}}
    mock_path = MagicMock(spec=Path)
    mock_path.read_text.return_value = json.dumps(payload)
    mock_config_path.return_value = mock_path

    result = _load_config_dict()
    assert result["version"] == CONFIG_VERSION
    assert result["scan"]["debug_ocr"] is True
