from autoscrapper.progress.recipe_utils import build_reverse_recipe_index


def test_build_reverse_recipe_index_empty():
    assert build_reverse_recipe_index([]) == {}


def test_build_reverse_recipe_index_no_recipe():
    items = [
        {"id": "item1"},
        {"id": "item2", "recipe": None},
        {"id": "item3", "recipe": "invalid"},
    ]
    assert build_reverse_recipe_index(items) == {}


def test_build_reverse_recipe_index_valid():
    items = [
        {
            "id": "item1",
            "recipe": {
                "ing1": 2,
                "ing2": 1,
            },
        },
        {
            "id": "item2",
            "recipe": {
                "ing2": 5,
                "ing3": 1,
            },
        },
    ]
    expected = {
        "ing1": ["item1"],
        "ing2": ["item1", "item2"],
        "ing3": ["item2"],
    }
    assert build_reverse_recipe_index(items) == expected


def test_build_reverse_recipe_index_missing_id():
    items = [
        {
            "recipe": {
                "ing1": 1,
            },
        },
    ]
    assert build_reverse_recipe_index(items) == {"ing1": [""]}
