import pytest

from autoscrapper.core.item_actions import (
    _normalize_action,
    clean_ocr_text,
    normalize_item_name,
)


@pytest.mark.parametrize(
    "name, expected",
    [
        ("  Item Name  ", "item name"),
        ("ITEM", "item"),
        ("item", "item"),
        ("", ""),
        ("   ", ""),
        ("Mixed Case", "mixed case"),
    ],
)
def test_normalize_item_name(name, expected):
    assert normalize_item_name(name) == expected


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("Multiple   Spaces", "Multiple Spaces"),
        ("Special#$ Characters!", "Special Characters!"),
        ("  LeadingTrailing  ", "LeadingTrailing"),
        ("Item-Name (123),!?:&+", "Item-Name (123),!?:&+"),
        ("Newline\nTest", "Newline Test"),
    ],
)
def test_clean_ocr_text(raw, expected):
    assert clean_ocr_text(raw) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("keep", "KEEP"),
        ("SELL", "SELL"),
        (" recycle ", "RECYCLE"),
        ("your_call", "KEEP"),
        ("your call", "KEEP"),
        ("sell_or_recycle", "SELL"),
        ("sell or recycle", "SELL"),
        ("crafting material", "KEEP"),
        ("KEEP", "KEEP"),
        ("RECYCLE", "RECYCLE"),
        ("SELL", "SELL"),
        ("UNKNOWN", None),
        (None, None),
        (123, None),
    ],
)
def test__normalize_action(value, expected):
    assert _normalize_action(value) == expected
