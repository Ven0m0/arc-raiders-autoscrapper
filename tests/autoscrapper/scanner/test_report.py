from autoscrapper.scanner.report import _item_label
from autoscrapper.core.item_actions import ItemActionResult
from autoscrapper.interaction.inventory_grid import Cell


def test_item_label_prefers_item_name_over_raw_text():
    cell = Cell(0, 0, 0, 0, 0, 0, 0, (0, 0, 0, 0))
    result = ItemActionResult(
        page=0,
        cell=cell,
        item_name="Cleaned Item Name",
        decision=None,
        action_taken="",
        raw_item_text="Raw Item Text",
    )
    assert _item_label(result) == "Cleaned Item Name"


def test_item_label_uses_raw_text_when_item_name_is_empty():
    cell = Cell(0, 0, 0, 0, 0, 0, 0, (0, 0, 0, 0))
    result = ItemActionResult(
        page=0,
        cell=cell,
        item_name="",
        decision=None,
        action_taken="",
        raw_item_text="Raw Item Text",
    )
    assert _item_label(result) == "Raw Item Text"


def test_item_label_uses_unreadable_when_both_empty():
    cell = Cell(0, 0, 0, 0, 0, 0, 0, (0, 0, 0, 0))
    result = ItemActionResult(
        page=0,
        cell=cell,
        item_name="",
        decision=None,
        action_taken="",
        raw_item_text="",
    )
    assert _item_label(result) == "<unreadable>"


def test_item_label_uses_unreadable_when_both_none():
    cell = Cell(0, 0, 0, 0, 0, 0, 0, (0, 0, 0, 0))
    result = ItemActionResult(
        page=0,
        cell=cell,
        item_name=None,
        decision=None,
        action_taken="",
        raw_item_text=None,
    )
    assert _item_label(result) == "<unreadable>"
