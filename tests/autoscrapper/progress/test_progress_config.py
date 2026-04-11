from autoscrapper.progress.progress_config import group_quests_by_trader

def test_group_quests_by_trader_empty():
    assert group_quests_by_trader([]) == {}

def test_group_quests_by_trader_basic_grouping():
    quests = [
        {"id": "q1", "trader": "Alice"},
        {"id": "q2", "trader": "Bob"},
        {"id": "q3", "trader": "Alice"},
    ]
    result = group_quests_by_trader(quests)
    assert set(result.keys()) == {"Alice", "Bob"}
    assert [q["id"] for q in result["Alice"]] == ["q1", "q3"]
    assert [q["id"] for q in result["Bob"]] == ["q2"]

def test_group_quests_by_trader_sorting():
    quests = [
        {"id": "q1", "trader": "Alice", "sortOrder": 2},
        {"id": "q2", "trader": "Alice", "sortOrder": 1},
        {"id": "q3", "trader": "Bob", "sortOrder": 10},
        {"id": "q4", "trader": "Bob", "sortOrder": 5},
    ]
    result = group_quests_by_trader(quests)
    assert [q["id"] for q in result["Alice"]] == ["q2", "q1"]
    assert [q["id"] for q in result["Bob"]] == ["q4", "q3"]

def test_group_quests_by_trader_default_trader():
    quests = [
        {"id": "q1"},
        {"id": "q2", "trader": None},
        {"id": "q3", "trader": ""},
        {"id": "q4", "trader": "Alice"},
    ]
    result = group_quests_by_trader(quests)
    assert set(result.keys()) == {"Unknown", "Alice"}
    assert [q["id"] for q in result["Unknown"]] == ["q1", "q2", "q3"]

def test_group_quests_by_trader_default_sort_order():
    quests = [
        {"id": "q1", "trader": "Alice", "sortOrder": 2},
        {"id": "q2", "trader": "Alice"},
        {"id": "q3", "trader": "Alice", "sortOrder": None},
        {"id": "q4", "trader": "Alice", "sortOrder": -1},
    ]
    result = group_quests_by_trader(quests)
    assert [q["id"] for q in result["Alice"]] == ["q4", "q2", "q3", "q1"]
