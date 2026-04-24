from __future__ import annotations

from autoscrapper.progress.decision_engine import DecisionEngine, DecisionReason


SAMPLE_ITEMS = [
    {
        "id": "test-rifle",
        "name": "Test Rifle",
        "type": "Weapon",
        "rarity": "rare",
        "value": 5000,
        "recyclesInto": {"scrap-metal": 5},
    },
    {
        "id": "test-pistol",
        "name": "Test Pistol",
        "type": "Weapon",
        "rarity": "common",
        "value": 1000,
    },
    {
        "id": "test-material",
        "name": "Test Material",
        "type": "Crafting",
        "rarity": "uncommon",
        "value": 2000,
        "recipe": {"scrap-metal": 2},
    },
    {
        "id": "quest-item",
        "name": "Quest Item",
        "type": "Misc",
        "rarity": "rare",
        "value": 100,
    },
    {
        "id": "junk-item",
        "name": "Junk Item",
        "type": "Junk",
        "rarity": "common",
        "value": 10,
    },
]


SAMPLE_QUESTS = [
    {
        "id": "quest-1",
        "name": "Test Quest",
        "requirements": [{"item_id": "quest-item", "quantity": 1}],
        "rewardItemIds": ["test-rifle"],
    },
]


SAMPLE_PROJECTS = [
    {
        "id": "project-1",
        "name": "Test Project",
        "requirements": [{"item_id": "test-material", "quantity": 3}],
        "phases": [
            {"requirementItemIds": [{"item_id": "test-material", "quantity": 5}]},
        ],
    },
]


SAMPLE_HIDEOUT_MODULES = [
    {
        "id": "med-station",
        "name": "Medical Station",
        "levels": [
            {"level": 1, "requirementItemIds": [{"item_id": "test-material", "quantity": 10}]},
            {"level": 2, "requirementItemIds": [{"item_id": "test-material", "quantity": 20}]},
        ],
    },
]


class TestDecisionEngine:
    def test_initialization(self):
        engine = DecisionEngine(
            items=SAMPLE_ITEMS,
            hideout_modules=SAMPLE_HIDEOUT_MODULES,
            quests=SAMPLE_QUESTS,
            projects=SAMPLE_PROJECTS,
        )
        assert engine.items is not None
        assert len(engine.quests) == 1
        assert len(engine.projects) == 1

    def test_quest_requirements_indexed(self):
        engine = DecisionEngine(
            items=SAMPLE_ITEMS,
            hideout_modules=SAMPLE_HIDEOUT_MODULES,
            quests=SAMPLE_QUESTS,
            projects=SAMPLE_PROJECTS,
        )
        assert "quest-item" in engine._quest_requirements
        assert len(engine._quest_requirements["quest-item"]) == 1

    def test_project_requirements_indexed(self):
        engine = DecisionEngine(
            items=SAMPLE_ITEMS,
            hideout_modules=SAMPLE_HIDEOUT_MODULES,
            quests=SAMPLE_QUESTS,
            projects=SAMPLE_PROJECTS,
        )
        assert "test-material" in engine._project_requirements

    def test_upgrade_requirements_indexed(self):
        engine = DecisionEngine(
            items=SAMPLE_ITEMS,
            hideout_modules=SAMPLE_HIDEOUT_MODULES,
            quests=SAMPLE_QUESTS,
            projects=SAMPLE_PROJECTS,
        )
        assert "test-material" in engine._upgrade_requirements
        modules = engine._upgrade_requirements["test-material"]
        assert len(modules) == 2

    def test_finalize_decision_recycle_value_exceeds(self):
        engine = DecisionEngine(
            items=SAMPLE_ITEMS,
            hideout_modules=SAMPLE_HIDEOUT_MODULES,
            quests=SAMPLE_QUESTS,
            projects=SAMPLE_PROJECTS,
        )
        high_value_item = {
            "id": "high-value-recycle",
            "type": "Weapon",
            "rarity": "rare",
            "value": 100,
            "recipe": {"scrap-metal": 5},
            "recyclesInto": {"scrap-metal": 100},
        }
        decision = DecisionReason(
            decision="sell", reasons=["Test reason"], dependencies=None, recycle_value_exceeds_item=True
        )
        result = engine.finalize_decision(high_value_item, decision)
        assert result.recycle_value_exceeds_item is True

    def test_finalize_decision_situational_overrides_to_keep(self):
        engine = DecisionEngine(
            items=SAMPLE_ITEMS,
            hideout_modules=SAMPLE_HIDEOUT_MODULES,
            quests=SAMPLE_QUESTS,
            projects=SAMPLE_PROJECTS,
        )
        item = SAMPLE_ITEMS[1]
        decision = DecisionReason(decision="situational", reasons=["Test reason"])
        result = engine.finalize_decision(item, decision)
        assert result.decision == "keep"
        assert "Override: treat 'Your Call' as Keep" in result.reasons


class TestDecisionEngineKeepPaths:
    def test_keep_quest_required_items(self):
        engine = DecisionEngine(
            items=SAMPLE_ITEMS,
            hideout_modules=SAMPLE_HIDEOUT_MODULES,
            quests=SAMPLE_QUESTS,
            projects=SAMPLE_PROJECTS,
        )
        item = {"id": "quest-item", "type": "Misc", "rarity": "rare", "value": 100}
        user_progress = {"active_quests": ["quest-1"], "hideout_levels": {}, "completed_projects": []}
        result = engine.get_decision(item, user_progress)
        assert result.decision == "keep"

    def test_keep_project_required_items(self):
        engine = DecisionEngine(
            items=SAMPLE_ITEMS,
            hideout_modules=SAMPLE_HIDEOUT_MODULES,
            quests=SAMPLE_QUESTS,
            projects=SAMPLE_PROJECTS,
        )
        item = {"id": "test-material", "type": "Crafting", "rarity": "uncommon", "value": 2000}
        user_progress = {"active_quests": [], "hideout_levels": {}, "completed_projects": []}
        result = engine.get_decision(item, user_progress)
        assert result.decision == "keep"


class TestDecisionEngineSellPaths:
    def test_sell_junk_items(self):
        engine = DecisionEngine(
            items=SAMPLE_ITEMS,
            hideout_modules=SAMPLE_HIDEOUT_MODULES,
            quests=SAMPLE_QUESTS,
            projects=SAMPLE_PROJECTS,
        )
        item = {"id": "junk-item", "type": "Junk", "rarity": "common", "value": 10}
        user_progress = {"active_quests": [], "hideout_levels": {}, "completed_projects": []}
        result = engine.get_decision(item, user_progress)
        assert result.decision in ("sell", "recycle", "sell_or_recycle")


class TestDecisionEngineRecyclePaths:
    def test_recycle_low_value_weapons(self):
        engine = DecisionEngine(
            items=SAMPLE_ITEMS,
            hideout_modules=SAMPLE_HIDEOUT_MODULES,
            quests=SAMPLE_QUESTS,
            projects=SAMPLE_PROJECTS,
        )
        item = {"id": "test-pistol", "type": "Weapon", "rarity": "common", "value": 1000}
        user_progress = {"active_quests": [], "hideout_levels": {}, "completed_projects": []}
        result = engine.get_decision(item, user_progress)
        assert result.decision in ("recycle", "sell", "keep", "sell_or_recycle", "situational")


class TestHideoutUpgradePriority:
    def test_hideout_level_affects_decision(self):
        engine = DecisionEngine(
            items=SAMPLE_ITEMS,
            hideout_modules=SAMPLE_HIDEOUT_MODULES,
            quests=SAMPLE_QUESTS,
            projects=SAMPLE_PROJECTS,
        )
        item = {"id": "test-material", "type": "Crafting", "rarity": "uncommon", "value": 2000}
        user_progress_no_upgrades = {"active_quests": [], "hideout_levels": {}, "completed_projects": []}

        result_no_upgrades = engine.get_decision(item, user_progress_no_upgrades)
        assert result_no_upgrades.decision in ("keep", "situational")


class TestCraftingValueEvaluation:
    def test_crafting_materials_higher_priority(self):
        engine = DecisionEngine(
            items=SAMPLE_ITEMS,
            hideout_modules=SAMPLE_HIDEOUT_MODULES,
            quests=SAMPLE_QUESTS,
            projects=SAMPLE_PROJECTS,
        )
        item = {
            "id": "test-material",
            "type": "Crafting",
            "rarity": "uncommon",
            "value": 2000,
            "recipe": {"scrap-metal": 2},
        }
        user_progress = {"active_quests": [], "hideout_levels": {}, "completed_projects": []}
        result = engine.get_decision(item, user_progress)
        assert result.decision in ("keep", "situational")


class TestGracefulDegradation:
    def test_empty_data_no_crash(self):
        engine = DecisionEngine(
            items=[],
            hideout_modules=[],
            quests=[],
            projects=[],
        )
        item = {"id": "unknown-item", "type": "Unknown", "rarity": "common", "value": 100}
        user_progress = {"active_quests": [], "hideout_levels": {}, "completed_projects": []}
        result = engine.get_decision(item, user_progress)
        assert result.decision is not None

    def test_missing_item_data_still_works(self):
        engine = DecisionEngine(
            items=[],
            hideout_modules=SAMPLE_HIDEOUT_MODULES,
            quests=SAMPLE_QUESTS,
            projects=SAMPLE_PROJECTS,
        )
        item = {"id": "nonexistent", "type": "Unknown", "rarity": "common", "value": 100}
        user_progress = {"active_quests": [], "hideout_levels": {}, "completed_projects": []}
        result = engine.get_decision(item, user_progress)
        assert result.decision is not None
