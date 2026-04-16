"""ArcTracker API models for API responses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class StashItem:
    """An item in the user's stash."""

    item_id: str
    name: str
    quantity: int
    slot: int | None
    item_type: str
    rarity: str
    value: int

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> StashItem:
        """Create a StashItem from API response data."""
        return cls(
            item_id=str(data.get("id", "")),
            name=str(data.get("name", "")),
            quantity=int(data.get("quantity", 1)),
            slot=data.get("slot"),
            item_type=str(data.get("type", "")),
            rarity=str(data.get("rarity", "")),
            value=int(data.get("value", 0)),
        )


@dataclass(frozen=True, slots=True)
class StashResponse:
    """Response from the stash API endpoint."""

    items: list[StashItem]
    total_slots: int
    used_slots: int
    page: int
    per_page: int
    total_items: int

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> StashResponse:
        """Create a StashResponse from API response data."""
        items_data = data.get("items", [])
        items = [StashItem.from_api(item) for item in items_data if isinstance(item, dict)]

        meta = data.get("meta", {})
        return cls(
            items=items,
            total_slots=int(data.get("totalSlots", 0)),
            used_slots=int(data.get("usedSlots", 0)),
            page=int(meta.get("page", 1)),
            per_page=int(meta.get("perPage", 50)),
            total_items=int(meta.get("total", 0)),
        )


@dataclass(frozen=True, slots=True)
class HideoutModule:
    """A hideout module with its upgrade progress."""

    module_id: str
    name: str
    current_level: int
    max_level: int

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> HideoutModule:
        """Create a HideoutModule from API response data."""
        return cls(
            module_id=str(data.get("id", "")),
            name=str(data.get("name", "")),
            current_level=int(data.get("currentLevel", 0)),
            max_level=int(data.get("maxLevel", 0)),
        )


@dataclass(frozen=True, slots=True)
class ProjectPhase:
    """A single phase of a project."""

    phase_number: int
    name: str
    completed: bool

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ProjectPhase:
        """Create a ProjectPhase from API response data."""
        return cls(
            phase_number=int(data.get("phase", 0)),
            name=str(data.get("name", "")),
            completed=bool(data.get("completed", False)),
        )


@dataclass(frozen=True, slots=True)
class ProjectProgress:
    """A project with its completion progress."""

    project_id: str
    name: str
    current_phase: int
    max_phases: int
    completed: bool
    phases: list[ProjectPhase]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ProjectProgress:
        """Create a ProjectProgress from API response data."""
        phases_data = data.get("phases", [])
        phases = [ProjectPhase.from_api(p) for p in phases_data if isinstance(p, dict)]

        return cls(
            project_id=str(data.get("id", "")),
            name=str(data.get("name", "")),
            current_phase=int(data.get("currentPhase", 0)),
            max_phases=int(data.get("maxPhases", 0)),
            completed=bool(data.get("completed", False)),
            phases=phases,
        )


@dataclass(frozen=True, slots=True)
class PublicItem:
    """A public item from the /api/items endpoint (no auth required)."""

    item_id: str
    name: str
    item_type: str
    rarity: str
    value: int
    weight_kg: float
    stack_size: int
    craft_bench: str | None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> PublicItem:
        """Create a PublicItem from API response data."""
        return cls(
            item_id=str(data.get("id", "")),
            name=str(data.get("name", "")),
            item_type=str(data.get("type", "")),
            rarity=str(data.get("rarity", "")),
            value=int(data.get("value", 0)),
            weight_kg=float(data.get("weightKg", 0)),
            stack_size=int(data.get("stackSize", 1)),
            craft_bench=data.get("craftBench"),
        )
