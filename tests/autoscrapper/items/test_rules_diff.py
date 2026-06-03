from __future__ import annotations


from autoscrapper.items.rules_diff import RuleChange, collect_rule_changes


def test_collect_rule_changes_invalid_payload():
    # Both payloads missing "items"
    assert collect_rule_changes({}, {}) == []

    # "items" is not a list
    assert collect_rule_changes({"items": {}}, {"items": []}) == []
    assert collect_rule_changes({"items": []}, {"items": "not a list"}) == []

    # Empty lists
    assert collect_rule_changes({"items": []}, {"items": []}) == []


def test_collect_rule_changes_match_by_id():
    default_payload = {
        "items": [
            {"id": "item1", "name": "Item One", "action": "keep"},
            {"id": "item2", "name": "Item Two", "action": "sell"},
        ]
    }
    updated_payload = {
        "items": [
            {"id": "item1", "name": "Item One", "action": "sell"},
            # Matches by ID, name differs but ID match takes precedence
            {"id": "item2", "name": "Different Name", "action": "keep"},
        ]
    }

    changes = collect_rule_changes(default_payload, updated_payload)
    assert len(changes) == 2

    # Check changes are sorted by name
    assert changes[0] == RuleChange(
        item_id="item2", name="Different Name", before_action="sell", after_action="keep", reasons=[]
    )
    assert changes[1] == RuleChange(
        item_id="item1", name="Item One", before_action="keep", after_action="sell", reasons=[]
    )


def test_collect_rule_changes_match_by_name():
    default_payload = {
        "items": [
            # Missing ID, only has name
            {"name": "Item No ID", "action": "keep"},
            {"id": "old_id", "name": "Item Change ID", "action": "sell"},
        ]
    }
    updated_payload = {
        "items": [
            {"name": "Item No ID", "action": "sell"},
            # New ID, but name matches
            {"id": "new_id", "name": "Item Change ID", "action": "keep"},
        ]
    }

    changes = collect_rule_changes(default_payload, updated_payload)
    assert len(changes) == 2

    assert changes[0] == RuleChange(
        item_id="new_id", name="Item Change ID", before_action="sell", after_action="keep", reasons=[]
    )
    assert changes[1] == RuleChange(
        item_id="", name="Item No ID", before_action="keep", after_action="sell", reasons=[]
    )


def test_collect_rule_changes_ignore_identical():
    default_payload = {
        "items": [
            {"id": "item1", "name": "Item One", "action": "keep"},
            # Same action using decision key
            {"id": "item2", "name": "Item Two", "decision": "sell"},
        ]
    }
    updated_payload = {
        "items": [
            {"id": "item1", "name": "Item One", "action": "keep"},
            {"id": "item2", "name": "Item Two", "action": "sell"},
        ]
    }

    assert collect_rule_changes(default_payload, updated_payload) == []


def test_collect_rule_changes_ignore_missing_action():
    default_payload = {
        "items": [
            {"id": "item1", "name": "Item One"},  # Missing action
            {"id": "item2", "name": "Item Two", "action": "keep"},
        ]
    }
    updated_payload = {
        "items": [
            {"id": "item1", "name": "Item One", "action": "keep"},
            {"id": "item2", "name": "Item Two"},  # Missing action in update
        ]
    }

    assert collect_rule_changes(default_payload, updated_payload) == []


def test_collect_rule_changes_ignore_non_dict():
    default_payload = {
        "items": [
            "not a dict",
            {"id": "item1", "name": "Item One", "action": "keep"},
        ]
    }
    updated_payload = {
        "items": [
            ["also not a dict"],
            {"id": "item1", "name": "Item One", "action": "sell"},
        ]
    }

    changes = collect_rule_changes(default_payload, updated_payload)
    assert len(changes) == 1
    assert changes[0].item_id == "item1"


def test_collect_rule_changes_unmatched():
    default_payload = {
        "items": [
            {"id": "item1", "name": "Item One", "action": "keep"},
        ]
    }
    updated_payload = {
        "items": [
            # ID and name don't match anything in default payload
            {"id": "item2", "name": "Item Two", "action": "sell"},
        ]
    }

    # Should not emit changes for new items, only changed rules
    assert collect_rule_changes(default_payload, updated_payload) == []


def test_collect_rule_changes_sorting():
    default_payload = {
        "items": [
            {"id": "3", "name": "Zebra", "action": "keep"},
            {"id": "1", "name": "apple", "action": "keep"},
            {"id": "2", "name": "Banana", "action": "keep"},
        ]
    }
    updated_payload = {
        "items": [
            {"id": "1", "name": "apple", "action": "sell"},
            {"id": "2", "name": "Banana", "action": "sell"},
            {"id": "3", "name": "Zebra", "action": "sell"},
        ]
    }

    changes = collect_rule_changes(default_payload, updated_payload)
    assert len(changes) == 3
    # Case insensitive sorting
    assert changes[0].name == "apple"
    assert changes[1].name == "Banana"
    assert changes[2].name == "Zebra"


def test_collect_rule_changes_reasons_extraction():
    default_payload = {
        "items": [
            {"id": "item1", "name": "Item One", "action": "keep"},
            {"id": "item2", "name": "Item Two", "action": "keep"},
            {"id": "item3", "name": "Item Three", "action": "keep"},
        ]
    }
    updated_payload = {
        "items": [
            {
                "id": "item1",
                "name": "Item One",
                "action": "sell",
                "analysis": ["Reason 1", "  Reason 2  ", "", "Reason 3"],
            },
            {"id": "item2", "name": "Item Two", "action": "sell", "analysis": "Not a list, should be ignored"},
            {
                "id": "item3",
                "name": "Item Three",
                "action": "sell",
                "analysis": [123, "Valid Reason"],  # Mixed types
            },
        ]
    }

    changes = collect_rule_changes(default_payload, updated_payload)
    # Sorted: Item One, Item Three, Item Two
    assert len(changes) == 3

    assert changes[0].name == "Item One"
    assert changes[0].reasons == ["Reason 1", "Reason 2", "Reason 3"]

    assert changes[1].name == "Item Three"
    assert changes[1].reasons == ["Valid Reason"]

    assert changes[2].name == "Item Two"
    assert changes[2].reasons == []
