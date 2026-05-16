from __future__ import annotations

_INDEX_CACHE: dict[int, tuple[list[dict], dict[str, list[str]]]] = {}


def build_reverse_recipe_index(items: list[dict]) -> dict[str, list[str]]:
    """Build a reverse recipe index mapping ingredient IDs to output item IDs."""
    items_id = id(items)
    if items_id in _INDEX_CACHE:
        # Check if the list is the exact same object by identity
        cached_items, cached_index = _INDEX_CACHE[items_id]
        if cached_items is items:
            return cached_index

    reverse_index: dict[str, list[str]] = {}
    for item in items:
        recipe = item.get("recipe")
        if not isinstance(recipe, dict):
            continue
        for ingredient_id in recipe.keys():
            used_by = reverse_index.setdefault(ingredient_id, [])
            used_by.append(item.get("id", ""))

    _INDEX_CACHE.clear()
    _INDEX_CACHE[items_id] = (items, reverse_index)
    return reverse_index
