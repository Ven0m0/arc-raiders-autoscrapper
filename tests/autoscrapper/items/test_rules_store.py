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


def test_default_rules_no_slash_in_item_names():
    """Assert no item name in the bundled default rules contains '/'.

    The Tesseract whitelist includes '/' but clean_ocr_text strips it before
    fuzzy matching. If any item name contained '/', it would never match.
    This test documents that the asymmetry has no live impact.
    """
    import json
    from autoscrapper.items.rules_store import DEFAULT_RULES_PATH

    data = json.loads(DEFAULT_RULES_PATH.read_text(encoding="utf-8"))
    items = data if isinstance(data, list) else data.get("items", [])
    names_with_slash = [
        entry.get("name", "") if isinstance(entry, dict) else str(entry)
        for entry in items
        if "/" in (entry.get("name", "") if isinstance(entry, dict) else str(entry))
    ]
    assert names_with_slash == [], f"Item names containing '/': {names_with_slash}"
