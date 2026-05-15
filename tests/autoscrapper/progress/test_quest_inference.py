from __future__ import annotations

import logging
import pytest

from autoscrapper.progress.quest_inference import (
    _build_predecessors_by_id,
    _build_trader_sequences,
    infer_completed_from_active,
)


@pytest.fixture
def sample_quests():
    return [
        {"id": "q1", "name": "Quest 1", "trader": "Trader A", "sortOrder": 1},
        {"id": "q2", "name": "Quest 2", "trader": "Trader A", "sortOrder": 2},
        {"id": "q3", "name": "Quest 3", "trader": "Trader B", "sortOrder": 1},
        {"id": "q4", "name": "Quest 4", "trader": "Trader B", "sortOrder": 2},
    ]


@pytest.fixture
def sample_quest_graph():
    return {
        "nodes": {
            "n1": "Quest 1",
            "n2": "Quest 2",
            "n3": "Quest 3",
            "n4": "Quest 4",
        },
        "edges": [
            ["n1", "n2"],
            ["n3", "n4"],
            ["n2", "n4"],
        ],
    }


def test_build_predecessors_by_id_success(sample_quests, sample_quest_graph):
    predecessors = _build_predecessors_by_id(sample_quests, sample_quest_graph)
    assert predecessors == {
        "q1": set(),
        "q2": {"q1"},
        "q3": set(),
        "q4": {"q3", "q2"},
    }


def test_build_predecessors_by_id_invalid_graph(sample_quests):
    with pytest.raises(ValueError, match="Invalid quest graph format."):
        _build_predecessors_by_id(sample_quests, {"nodes": [], "edges": {}})


def test_build_predecessors_by_id_unresolved_nodes(sample_quests):
    invalid_graph = {
        "nodes": {"n1": "Quest 1", "nx": "Unknown Quest"},
        "edges": [],
    }
    with pytest.raises(ValueError, match="Quest graph contains nodes that could not be matched to quests: nx"):
        _build_predecessors_by_id(sample_quests, invalid_graph)


def test_build_predecessors_by_id_duplicate_name(caplog):
    quests = [
        {"id": "q1", "name": "Duplicate Quest"},
        {"id": "q2", "name": "Duplicate Quest"},
    ]
    graph = {"nodes": {"n1": "Duplicate Quest"}, "edges": []}

    with caplog.at_level(logging.WARNING):
        predecessors = _build_predecessors_by_id(quests, graph)

    assert "Duplicate quest name in data" in caplog.text
    assert "keeping first occurrence" in caplog.text
    # Predecessors should still be built for both IDs
    assert "q1" in predecessors
    assert "q2" in predecessors


def test_build_trader_sequences_success(sample_quests):
    trader_order, sequences = _build_trader_sequences(sample_quests)
    assert trader_order == ["Trader A", "Trader B"]
    assert sequences == {
        "Trader A": ["q1", "q2"],
        "Trader B": ["q3", "q4"],
    }


def test_infer_completed_from_active_single_match(sample_quests, sample_quest_graph):
    # Active is q2, meaning q1 must be completed
    # Trader A sequences: [q1, q2]
    # State (1, 0) means Trader A has 1 completed (q1) and Trader B has 0.
    # Active signature for (1, 0): q2 (from A), q3 (from B) - wait, if q3 is active, active_quests needs to contain q3 too.
    active_quests = ["q2", "q3"]
    completed = infer_completed_from_active(sample_quests, sample_quest_graph, active_quests)
    assert completed == ["q1"]


def test_infer_completed_from_active_ambiguous(sample_quests, sample_quest_graph):
    # If active is just q4, there are multiple states that could result in q4 being active if we didn't check predecessors carefully.
    # But let's construct a scenario where there are no strict sequences, or multiple states give the same active signature.
    # Actually, if active is q4, and predecessors are q2 and q3.
    # We can force the fallback by making the trader sequence empty, or graph ancestors needed.

    # Just use an active list that doesn't match any state strictly, forcing the graph ancestor fallback.
    # For instance, an active quest that doesn't follow the sequences properly.
    active_quests = ["q4"]
    completed = infer_completed_from_active(sample_quests, sample_quest_graph, active_quests)
    # Ancestors of q4: q2 and q3. Ancestor of q2 is q1.
    assert set(completed) == {"q1", "q2", "q3"}


def test_infer_completed_from_active_missing_active_quests(sample_quests, sample_quest_graph):
    active_quests = ["q1", "Unknown Quest"]
    with pytest.raises(ValueError, match="Active quests not found: Unknown Quest"):
        infer_completed_from_active(sample_quests, sample_quest_graph, active_quests)
