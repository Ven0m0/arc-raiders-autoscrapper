from unittest.mock import patch
from autoscrapper.config import _migrate_config, CONFIG_VERSION


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
