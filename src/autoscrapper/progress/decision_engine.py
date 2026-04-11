from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .recipe_utils import build_reverse_recipe_index
from .weapon_grouping import WeaponGrouper

KEEP_ITEM_OVERRIDES = {
    "assorted-seeds": [
        "Valuable currency item",
        "Used for trading with Celeste",
    ],
    "chemicals": [
        "Override: keep progression material",
        "Manual default keep override",
    ],
    "crude-explosives": [
        "Override: keep progression material",
        "Manual default keep override",
    ],
}


def _normalize_item_id(item_id: str | None) -> str:
    return str(item_id or "").replace("_", "-")


@dataclass(frozen=True, slots=True)
class DecisionReason:
    decision: str
    reasons: list[str]
    dependencies: list[str] | None = None
    recycle_value_exceeds_item: bool = False


@dataclass(frozen=True, slots=True)
class CraftingValue:
    is_valuable: bool
    recipe_count: int
    details: str


@dataclass(frozen=True, slots=True)
class RecycleValue:
    is_valuable: bool
    description: str
    estimated_value: int


class DecisionEngine:
    def __init__(
        self,
        items: list[dict],
        hideout_modules: list[dict],
        quests: list[dict],
        projects: list[dict],
    ) -> None:
        self.items = {item.get("id"): item for item in items}
        self.hideout_modules = hideout_modules
        self.quests = quests
        self.projects = projects
        self.reverse_recipe_index = build_reverse_recipe_index(items)

        self._quest_requirements: dict[str, list[dict]] = defaultdict(list)
        for quest in quests:
            reqs = quest.get("requirements") or []
            if isinstance(reqs, list):
                for req in reqs:
                    item_id = req.get("item_id")
                    if item_id:
                        self._quest_requirements[item_id].append(quest)

        self._project_requirements: dict[str, list[dict]] = defaultdict(list)
        for project in projects:
            reqs = project.get("requirements") or []
            if isinstance(reqs, list):
                for req in reqs:
                    item_id = req.get("item_id")
                    if item_id:
                        self._project_requirements[item_id].append(project)

            phases = project.get("phases") or []
            if isinstance(phases, list):
                for phase in phases:
                    phase_reqs = phase.get("requirementItemIds") or []
                    if isinstance(phase_reqs, list):
                        for req in phase_reqs:
                            item_id = req.get("item_id")
                            if item_id:
                                # Avoid adding the same project multiple times if it appears in multiple phases
                                if project not in self._project_requirements[item_id]:
                                    self._project_requirements[item_id].append(project)

        self._upgrade_requirements: dict[str, list[tuple[dict, int]]] = defaultdict(list)
        for module in hideout_modules:
            levels = module.get("levels") or []
            if isinstance(levels, list):
                for level_data in levels:
                    level = level_data.get("level")
                    reqs = level_data.get("requirementItemIds") or []
                    if level is not None and isinstance(reqs, list):
                        for req in reqs:
                            item_id = req.get("item_id")
                            if item_id:
                                self._upgrade_requirements[item_id].append((module, level))

    def finalize_decision(self, item: dict, decision: DecisionReason) -> DecisionReason:
        final_decision = decision
        recycle_data = item.get("recyclesInto") or item.get("salvagesInto") or item.get("crafting")
        if recycle_data and isinstance(recycle_data, dict) and recycle_data:
            recycle_value = self.evaluate_recycle_value(item)
            if recycle_value.estimated_value > item.get("value", 0):
                final_decision = DecisionReason(
                    decision=final_decision.decision,
                    reasons=final_decision.reasons,
                    dependencies=final_decision.dependencies,
                    recycle_value_exceeds_item=True,
                )

        if final_decision.decision == "situational":
            final_decision = DecisionReason(
                decision="keep",
                reasons=final_decision.reasons + ["Override: treat 'Your Call' as Keep"],
                dependencies=final_decision.dependencies,
                recycle_value_exceeds_item=final_decision.recycle_value_exceeds_item,
            )

        return final_decision

    def get_decision(self, item: dict, user_progress: dict) -> DecisionReason:
        item_type = str(item.get("type", "")).lower()
        rarity = str(item.get("rarity", "")).lower()

        override_reasons = KEEP_ITEM_OVERRIDES.get(_normalize_item_id(item.get("id")))
        if override_reasons is not None:
            return self.finalize_decision(
                item,
                DecisionReason(
                    decision="keep",
                    reasons=override_reasons,
                ),
            )

        if rarity == "legendary":
            return self.finalize_decision(
                item,
                DecisionReason(
                    decision="keep",
                    reasons=[
                        "Legendary rarity - extremely valuable",
                        "Keep all legendaries",
                    ],
                ),
            )

        if item_type == "blueprint":
            return self.finalize_decision(
                item,
                DecisionReason(
                    decision="situational",
                    reasons=[
                        "Blueprint - valuable for unlocking crafting recipes",
                        "Review carefully before selling or recycling",
                    ],
                ),
            )

        if item_type == "weapon" or WeaponGrouper.is_weapon_variant(item):
            item_id = str(item.get("id", ""))
            tier = WeaponGrouper.get_tier_number(item_id)
            is_variant = tier > 0
            # base_name is the display name without roman numeral suffix (e.g. "Assault Rifle" from "Assault Rifle III")
            base_name = WeaponGrouper.get_base_name(str(item.get("name", ""))) if is_variant else ""
            # base_id is the item-ID root (e.g. "ar_standard" from "ar_standard-iii"); distinct from base_name
            base_id = WeaponGrouper.get_base_id(item_id) if is_variant else ""
            tier_label = f"Tier {tier} variant" if is_variant else "Weapon"
            reasons = [
                f"{tier_label} - review based on your current loadout",
                "Consider tier and your play style",
            ]
            if is_variant:
                # Prefer the human-readable base_name; fall back to the raw base_id
                reasons.append(f"Base weapon: {base_name}" if base_name else f"Base weapon family: {base_id}")
            return self.finalize_decision(
                item,
                DecisionReason(
                    decision="situational",
                    reasons=reasons,
                ),
            )

        if item_type == "ammunition":
            return self.finalize_decision(
                item,
                DecisionReason(
                    decision="situational",
                    reasons=[
                        "Ammunition - essential for weapons",
                        "Review based on your weapon loadout",
                    ],
                ),
            )

        if item_type in {"quick use", "quick_use"}:
            return self.finalize_decision(
                item,
                DecisionReason(
                    decision="situational",
                    reasons=[
                        "Consumable item - grenades, healing items, etc.",
                        "Review based on your current inventory needs",
                    ],
                ),
            )

        if item_type == "key":
            return self.finalize_decision(
                item,
                DecisionReason(
                    decision="situational",
                    reasons=[
                        "Key - opens locked areas and containers",
                        "Review based on areas you want to access",
                    ],
                ),
            )

        quest_use = self.is_used_in_active_quests(item, user_progress)
        if quest_use["is_used"]:
            return self.finalize_decision(
                item,
                DecisionReason(
                    decision="keep",
                    reasons=[f"Required for quest: {', '.join(quest_use['quest_names'])}"],
                    dependencies=quest_use["quest_names"],
                ),
            )

        project_use = self.is_used_in_active_projects(item, user_progress)
        if project_use["is_used"]:
            return self.finalize_decision(
                item,
                DecisionReason(
                    decision="keep",
                    reasons=[f"Needed for project: {', '.join(project_use['project_names'])}"],
                    dependencies=project_use["project_names"],
                ),
            )

        upgrade_use = self.is_needed_for_upgrades(item, user_progress)
        if upgrade_use["is_needed"]:
            return self.finalize_decision(
                item,
                DecisionReason(
                    decision="keep",
                    reasons=["Required for hideout upgrade: " + ", ".join(upgrade_use["module_names"])],
                    dependencies=upgrade_use["module_names"],
                ),
            )

        crafting_value = self.evaluate_crafting_value(item)
        if crafting_value.is_valuable:
            return self.finalize_decision(
                item,
                DecisionReason(
                    decision="situational",
                    reasons=[
                        f"Used in {crafting_value.recipe_count} crafting recipes",
                        crafting_value.details,
                    ],
                ),
            )

        if self.is_high_value_trinket(item):
            return self.finalize_decision(
                item,
                DecisionReason(
                    decision="sell_or_recycle",
                    reasons=[
                        f"High value ({item.get('value', 0)} coins)",
                        "No crafting or upgrade use",
                    ],
                ),
            )

        recycle_data = item.get("recyclesInto") or item.get("salvagesInto") or item.get("crafting")
        if recycle_data and isinstance(recycle_data, dict) and recycle_data:
            recycle_value = self.evaluate_recycle_value(item)
            if recycle_value.is_valuable:
                compare = (
                    "worth MORE than" if recycle_value.estimated_value > item.get("value", 0) else "worth less than"
                )
                return self.finalize_decision(
                    item,
                    DecisionReason(
                        decision="sell_or_recycle",
                        reasons=[
                            f"Recycles into: {recycle_value.description}",
                            "Recycle value: Components "
                            f"({recycle_value.estimated_value} coins) {compare} Item "
                            f"({item.get('value', 0)} coins)",
                        ],
                    ),
                )

        if rarity in {"rare", "epic"}:
            return self.finalize_decision(
                item,
                DecisionReason(
                    decision="situational",
                    reasons=[
                        f"{rarity.title()} rarity",
                        "May have future use - review carefully",
                    ],
                ),
            )

        return self.finalize_decision(
            item,
            DecisionReason(
                decision="sell_or_recycle",
                reasons=["No immediate use found", "Safe to sell or recycle"],
            ),
        )

    def is_used_in_active_quests(self, item: dict, user_progress: dict) -> dict[str, list[str] | bool]:
        quest_names: list[str] = []
        completed = set(user_progress.get("completedQuests", []))
        item_id = item.get("id")

        if item_id:
            for quest in self._quest_requirements.get(item_id, []):
                if quest.get("id") not in completed:
                    quest_names.append(quest.get("name", ""))

        return {"is_used": bool(quest_names), "quest_names": quest_names}

    def is_used_in_active_projects(self, item: dict, user_progress: dict) -> dict[str, list[str] | bool]:
        project_names: list[str] = []
        completed = set(user_progress.get("completedProjects", []))
        item_id = item.get("id")

        if item_id:
            for project in self._project_requirements.get(item_id, []):
                if project.get("id") not in completed:
                    project_names.append(project.get("name", ""))

        return {"is_used": bool(project_names), "project_names": project_names}

    def is_needed_for_upgrades(self, item: dict, user_progress: dict) -> dict[str, list[str] | bool]:
        module_names: list[str] = []
        hideout_levels = user_progress.get("hideoutLevels", {})
        item_id = item.get("id")

        if item_id:
            for module, level in self._upgrade_requirements.get(item_id, []):
                module_id = module.get("id")
                current_level = hideout_levels.get(module_id, 0)
                if level > current_level:
                    module_names.append(f"{module.get('name')} (Level {level})")

        return {"is_needed": bool(module_names), "module_names": module_names}

    def evaluate_crafting_value(self, item: dict) -> CraftingValue:
        recipe_count = len(self.reverse_recipe_index.get(item.get("id"), []))
        rarity = str(item.get("rarity", "")).lower()
        is_rare = rarity in {"rare", "epic", "legendary"}
        return CraftingValue(
            is_valuable=recipe_count > 2 or (recipe_count > 0 and is_rare),
            recipe_count=recipe_count,
            details=("Rare crafting material" if is_rare else "Common crafting ingredient"),
        )

    def is_high_value_trinket(self, item: dict) -> bool:
        high_value_threshold = 1000
        trinket_keywords = {"trinket", "misc", "collectible"}

        has_no_recipe = not item.get("recipe")
        recycle_data = item.get("recyclesInto") or item.get("salvagesInto") or item.get("crafting")
        has_no_recycle = not recycle_data
        item_type = str(item.get("type", "")).lower()
        is_trinket = any(keyword in item_type for keyword in trinket_keywords)

        return item.get("value", 0) >= high_value_threshold and has_no_recipe and has_no_recycle and is_trinket

    def evaluate_recycle_value(self, item: dict) -> RecycleValue:
        recycle_data = item.get("recyclesInto") or item.get("salvagesInto") or item.get("crafting")
        if not recycle_data or not isinstance(recycle_data, dict) or not recycle_data:
            return RecycleValue(is_valuable=False, description="Nothing", estimated_value=0)

        materials = []
        total_value = 0

        for item_id, quantity in recycle_data.items():
            output_item = self.items.get(item_id)
            if output_item:
                materials.append(f"{quantity}x {output_item.get('name')}")
                try:
                    total_value += int(output_item.get("value", 0)) * int(quantity)
                except (TypeError, ValueError):
                    continue

        return RecycleValue(
            is_valuable=total_value > item.get("value", 0) * 0.5,
            description=", ".join(materials),
            estimated_value=total_value,
        )

    def get_items_with_decisions(self, user_progress: dict) -> list[dict]:
        items_with_decisions: list[dict] = []
        for item in self.items.values():
            decision = self.get_decision(item, user_progress)
            items_with_decisions.append({**item, "decision_data": decision})
        return items_with_decisions
