from __future__ import annotations


QUEST_TRADER_OVERRIDES = {
    "combat-recon": "Shani",
    "bombing-run": "Shani",
    "on-deaf-ears": "Lance",
    "on-the-map": "Lance",
    "a-prime-specimen": "Shani",
}


def apply_quest_overrides(quests: list[dict]) -> list[dict]:
    """Apply quest overrides without mutating the original list."""
    updated = []
    for quest in quests:
        quest_id = quest.get("id")
        override_trader = QUEST_TRADER_OVERRIDES.get(quest_id) if isinstance(quest_id, str) else None
        if override_trader:
            updated.append({**quest, "trader": override_trader})
        else:
            updated.append(quest)
    return updated
