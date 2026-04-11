import pytest
from unittest.mock import patch
from autoscrapper.items.rules_store import (
    normalize_action,
    active_rules_path,
    using_custom_rules,
    CUSTOM_RULES_PATH,
    DEFAULT_RULES_PATH,
)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("keep", "keep"),
        ("k", "keep"),
        ("KEEP", "keep"),
        (" K ", "keep"),
        ("sell", "sell"),
        ("s", "sell"),
        ("SELL", "sell"),
        (" S ", "sell"),
        ("recycle", "recycle"),
        ("r", "recycle"),
        ("RECYCLE", "recycle"),
        (" R ", "recycle"),
        ("invalid", None),
        ("", None),
        ("ks", None),
        ("123", None),
    ],
)
def test_normalize_action(value, expected):
    assert normalize_action(value) == expected


@patch("pathlib.Path.exists")
def test_active_rules_path_custom_exists(mock_exists):
    mock_exists.return_value = True
    assert active_rules_path() == CUSTOM_RULES_PATH


@patch("pathlib.Path.exists")
def test_active_rules_path_custom_missing(mock_exists):
    mock_exists.return_value = False
    assert active_rules_path() == DEFAULT_RULES_PATH


@patch("pathlib.Path.exists")
def test_using_custom_rules_true(mock_exists):
    mock_exists.return_value = True
    assert using_custom_rules() is True


@patch("pathlib.Path.exists")
def test_using_custom_rules_false(mock_exists):
    mock_exists.return_value = False
    assert using_custom_rules() is False
