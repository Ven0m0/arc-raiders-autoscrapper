import pytest
from autoscrapper.items.rules_store import normalize_action


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
