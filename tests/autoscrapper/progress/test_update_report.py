from typing import Any, Dict, List

from autoscrapper.progress.update_report import diff_quests
def test_diff_quests_empty_lists() -> None:
    """Test that empty inputs result in zero counts and empty lists."""
    before: List[Dict[str, Any]] = []
    after: List[Dict[str, Any]] = []

    diff = diff_quests(before, after)

    assert diff["beforeCount"] == 0
    assert diff["afterCount"] == 0
    assert diff["addedCount"] == 0
    assert diff["removedCount"] == 0
    assert diff["changedCount"] == 0
    assert diff["added"] == []
    assert diff["removed"] == []
    assert diff["changed"] == []
def test_diff_quests_ignores_invalid_entries() -> None:
    """Test that non-dict objects and dicts without valid IDs are ignored."""
    before: List[Any] = [
        "not a dict",
        None,
        123,
        {"name": "No ID Quest"},  # Dict without 'id'
        {"id": " ", "name": "Empty ID Quest"},  # Dict with blank 'id'
        {"id": "q1", "name": "Valid Before"},
    ]
    after: List[Any] = [
        {"id": "q2", "name": "Valid After"},
        {"id": "", "name": "Empty ID"},
    ]

    diff = diff_quests(before, after)

    assert diff["beforeCount"] == 1
    assert diff["afterCount"] == 1
    assert diff["removedCount"] == 1
    assert diff["addedCount"] == 1
    assert diff["removed"][0]["id"] == "q1"
    assert diff["added"][0]["id"] == "q2"
def test_diff_quests_additions_and_removals() -> None:
    """Test that new quests are tracked as additions and missing quests as removals."""
    before = [
        {"id": "q1", "name": "Quest 1", "trader": "Trader A", "xp": 100, "sortOrder": 1},
        {"id": "q2", "name": "Quest 2", "trader": "Trader B", "xp": 200, "sortOrder": 2},
    ]
    after = [
        {"id": "q2", "name": "Quest 2", "trader": "Trader B", "xp": 200, "sortOrder": 2},
        {"id": "q3", "name": "Quest 3", "trader": "Trader C", "xp": 300, "sortOrder": 3},
    ]

    diff = diff_quests(before, after)

    assert diff["beforeCount"] == 2
    assert diff["afterCount"] == 2
    assert diff["addedCount"] == 1
    assert diff["removedCount"] == 1
    assert diff["changedCount"] == 0

    assert diff["removed"][0] == {
        "id": "q1", "name": "Quest 1", "trader": "Trader A", "xp": 100, "sortOrder": 1
    }
    assert diff["added"][0] == {
        "id": "q3", "name": "Quest 3", "trader": "Trader C", "xp": 300, "sortOrder": 3
    }
def test_diff_quests_changes() -> None:
    """Test that specific fields changing between versions are accurately tracked."""
    before = [
        {
            "id": "q1",
            "name": "Old Name",
            "trader": "Old Trader",
            "sortOrder": 1,
            "xp": 100,
            "requirements": ["req1"],
            "rewardItemIds": ["rew1"],
            "ignored_field": "old"
        }
    ]
    after = [
        {
            "id": "q1",
            "name": "New Name",
            "trader": "New Trader",
            "sortOrder": 2,
            "xp": 200,
            "requirements": ["req1", "req2"],
            "rewardItemIds": ["rew2"],
            "ignored_field": "new"
        }
    ]

    diff = diff_quests(before, after)

    assert diff["changedCount"] == 1
    assert diff["addedCount"] == 0
    assert diff["removedCount"] == 0

    change_entry = diff["changed"][0]
    assert change_entry["id"] == "q1"
    assert change_entry["name"] == "New Name"  # Uses 'after' name

    changes = change_entry["changes"]
    assert "name" in changes
    assert changes["name"] == {"before": "Old Name", "after": "New Name"}
    assert changes["trader"] == {"before": "Old Trader", "after": "New Trader"}
    assert changes["sortOrder"] == {"before": 1, "after": 2}
    assert changes["xp"] == {"before": 100, "after": 200}
    assert changes["requirements"] == {"before": ["req1"], "after": ["req1", "req2"]}
    assert changes["rewardItemIds"] == {"before": ["rew1"], "after": ["rew2"]}

    # Check that untracked fields are not in the diff
    assert "ignored_field" not in changes
def test_diff_quests_no_changes() -> None:
    """Test that quests with identical tracked fields result in no changes."""
    before = [
        {"id": "q1", "name": "Quest 1", "trader": "Trader A", "untracked_field": "A"}
    ]
    after = [
        {"id": "q1", "name": "Quest 1", "trader": "Trader A", "untracked_field": "B"}
    ]

    diff = diff_quests(before, after)

    assert diff["changedCount"] == 0
    assert diff["addedCount"] == 0
    assert diff["removedCount"] == 0
    assert diff["changed"] == []

def test_diff_quests_sorting() -> None:
    """Test that the changed list is sorted by name, then id."""
    before = [
        {"id": "z-id", "name": "B Quest", "xp": 10},
        {"id": "a-id", "name": "B Quest", "xp": 10},
        {"id": "x-id", "name": "A Quest", "xp": 10},
    ]
    after = [
        {"id": "z-id", "name": "B Quest", "xp": 20},
        {"id": "a-id", "name": "B Quest", "xp": 20},
        {"id": "x-id", "name": "A Quest", "xp": 20},
    ]

    diff = diff_quests(before, after)

    assert diff["changedCount"] == 3

    # Should sort: A Quest (x-id), B Quest (a-id), B Quest (z-id)
    assert diff["changed"][0]["id"] == "x-id"
    assert diff["changed"][1]["id"] == "a-id"
    assert diff["changed"][2]["id"] == "z-id"
