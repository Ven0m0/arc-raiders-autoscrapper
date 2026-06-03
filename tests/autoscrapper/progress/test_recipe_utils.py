"""Tests for recipe_utils.build_reverse_recipe_index."""

import pytest
from autoscrapper.progress.recipe_utils import build_reverse_recipe_index


def test_empty_items():
    assert build_reverse_recipe_index([]) == {}


def test_item_without_recipe():
    items = [{"id": "item-1", "name": "Widget"}]
    assert build_reverse_recipe_index(items) == {}


def test_single_ingredient():
    items = [{"id": "item-out", "recipe": {"ing-1": 2}}]
    result = build_reverse_recipe_index(items)
    assert result == {"ing-1": ["item-out"]}


def test_multiple_ingredients():
    items = [{"id": "item-out", "recipe": {"ing-1": 1, "ing-2": 3}}]
    result = build_reverse_recipe_index(items)
    assert result["ing-1"] == ["item-out"]
    assert result["ing-2"] == ["item-out"]


def test_shared_ingredient_across_items():
    items = [
        {"id": "item-a", "recipe": {"shared-ing": 1}},
        {"id": "item-b", "recipe": {"shared-ing": 2}},
    ]
    result = build_reverse_recipe_index(items)
    assert sorted(result["shared-ing"]) == ["item-a", "item-b"]


@pytest.mark.parametrize(
    "item",
    [
        {"id": None, "recipe": {"ing-1": 1}},
        {"recipe": {"ing-1": 1}},
    ],
)
def test_item_id_none_or_missing(item):
    result = build_reverse_recipe_index([item])
    assert result["ing-1"] == [""]


def test_non_dict_recipe_is_skipped():
    items = [{"id": "item-1", "recipe": ["ing-1", "ing-2"]}]
    assert build_reverse_recipe_index(items) == {}
