import pytest
from autoscrapper.core.item_actions import (
    normalize_item_name,
    clean_ocr_text,
    _normalize_action,
    choose_decision,
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


@pytest.mark.parametrize(
    "item_name, actions, expected",
    [
        # Empty/whitespace item name
        ("", {"item": ["KEEP"]}, (None, None)),
        ("   ", {"item": ["KEEP"]}, (None, None)),
        # Item not in actions map
        ("unknown item", {"known item": ["KEEP"]}, (None, None)),
        # Item in actions map with 1 decision
        ("known item", {"known item": ["KEEP"]}, ("KEEP", None)),
        # Item in actions map with >1 decisions
        ("known item", {"known item": ["KEEP", "SELL"]}, ("KEEP", "Multiple decisions ['KEEP', 'SELL']; chose KEEP.")),
        # Item case-insensitive matching / extra whitespace
        ("  Known Item  ", {"known item": ["SELL"]}, ("SELL", None)),
    ],
)
def test_choose_decision(item_name, actions, expected):
    assert choose_decision(item_name, actions) == expected
