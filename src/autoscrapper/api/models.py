"""ArcTracker API models for API responses."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

type ItemDecision = Literal["KEEP", "SELL", "RECYCLE"]


@dataclass(slots=True)
class RateLimitState:
    """Tracks rate limit information from API responses."""

    limit: int = 500
    remaining: int = 500
    reset_timestamp: float = 0.0
    last_request_timestamp: float = 0.0

    @property
    def is_rate_limited(self) -> bool:
        """Check if we're currently rate limited."""
        if self.remaining <= 0:
            now = time.time()
            if now < self.reset_timestamp:
                return True
        return False

    @property
    def seconds_until_reset(self) -> float:
        """Seconds until rate limit resets."""
        now = time.time()
        return max(0.0, self.reset_timestamp - now)

    def time_until_next_request(self, min_interval: float = 8.0) -> float:
        """Calculate time to wait before next request."""
        now = time.time()
        time_since_last = now - self.last_request_timestamp
        cooldown = max(0.0, min_interval - time_since_last)

        if self.is_rate_limited:
            return max(cooldown, self.seconds_until_reset)
        return cooldown


class StashItem(BaseModel):
    """An item in the user's stash."""

    model_config = ConfigDict(frozen=True, extra="ignore", strict=False, populate_by_name=True)

    item_id: str = Field(alias="id")
    name: str
    quantity: int
    slot: int | None = None
    item_type: str = Field(alias="type")
    rarity: str
    value: int

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "StashItem":
        """Create a StashItem from API response data."""
        return cls.model_validate(data)


@dataclass(slots=True)
class StashData:
    """Complete stash data from API."""

    items: list[StashItem] = field(default_factory=list)
    total_slots: int = 0
    used_slots: int = 0
    api_error: str | None = None


class HideoutModule(BaseModel):
    """A hideout module with its upgrade progress."""

    model_config = ConfigDict(frozen=True, extra="ignore", strict=False, populate_by_name=True)

    module_id: str = Field(alias="id")
    name: str
    current_level: int = Field(alias="currentLevel")
    max_level: int = Field(alias="maxLevel")

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "HideoutModule":
        """Create a HideoutModule from API response data."""
        return cls.model_validate(data)


class ProjectPhase(BaseModel):
    """A single phase of a project."""

    model_config = ConfigDict(frozen=True, extra="ignore", strict=False, populate_by_name=True)

    phase_number: int = Field(alias="phase")
    name: str
    completed: bool

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "ProjectPhase":
        """Create a ProjectPhase from API response data."""
        return cls.model_validate(data)


class ProjectProgress(BaseModel):
    """A project with its completion progress."""

    model_config = ConfigDict(frozen=True, extra="ignore", strict=False, populate_by_name=True)

    project_id: str = Field(alias="id")
    name: str
    current_phase: int = Field(alias="currentPhase")
    max_phases: int = Field(alias="maxPhases")
    completed: bool
    phases: list[ProjectPhase]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "ProjectProgress":
        """Create a ProjectProgress from API response data."""
        return cls.model_validate(data)


@dataclass(slots=True)
class APIItemDecision:
    """Single item decision from API."""

    item_id: str
    decision: ItemDecision
    item_name: str | None = None


@dataclass(slots=True)
class APIInventoryResult:
    """Result from API inventory fetch."""

    decisions: list[APIItemDecision] = field(default_factory=list)
    from_cache: bool = False
    api_error: str | None = None


class UserProfile(BaseModel):
    """User profile information."""

    model_config = ConfigDict(frozen=True, extra="ignore", strict=False, populate_by_name=True)

    username: str
    level: int
    member_since: str = Field(alias="memberSince")

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "UserProfile":
        """Create a UserProfile from API response data."""
        return cls.model_validate(data)


class UserQuest(BaseModel):
    """A quest with user completion status."""

    model_config = ConfigDict(frozen=True, extra="ignore", strict=False, populate_by_name=True)

    quest_id: str = Field(alias="id")
    name: str
    completed: bool
    objectives: list[Any]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "UserQuest":
        return cls.model_validate(data)


class RoundEntry(BaseModel):
    """A single round from the user's round history."""

    model_config = ConfigDict(frozen=True, extra="ignore", strict=False, populate_by_name=True)

    round_id: str = Field(alias="id")
    outcome: str
    map_slug: str = Field(alias="map")
    kills: int
    damage: float
    season: int | None = None
    looted_items: list[Any] = Field(alias="lootedItems")

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "RoundEntry":
        return cls.model_validate(data)


class Blueprint(BaseModel):
    """A blueprint with learned status."""

    model_config = ConfigDict(frozen=True, extra="ignore", strict=False, populate_by_name=True)

    blueprint_id: str = Field(alias="id")
    name: str
    category: str
    learned: bool

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Blueprint":
        return cls.model_validate(data)
