"""Arc-Lens data scrapers ported from JavaScript to Python.

Provides scrapers for MetaForge API and Arc Raiders Wiki.
"""

from __future__ import annotations

import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import httpx
from bs4 import BeautifulSoup

RATE_LIMIT_MS = 500
METAFORGE_GAME_DATA_URL = "https://metaforge.app/api/game-map-data"
WIKI_BASE = "https://arcraiders.wiki/wiki"
MAP_IDS = ["dam", "spaceport", "buried-city", "blue-gate", "stella-montis"]


class ScrapingError(Exception):
    """Raised when scraping fails."""

    pass


@dataclass
class ScrapedItem:
    """Represents a scraped item from the wiki."""

    id: str
    name: str
    rarity: str = ""
    item_type: str = ""
    value: int = 0
    description: str = ""
    breaks_into: list[dict] = field(default_factory=list)
    found_in: list[str] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)
    raw_data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "rarity": self.rarity,
            "type": self.item_type,
            "value": self.value,
            "description": self.description,
            "breaksInto": self.breaks_into,
            "foundIn": self.found_in,
            "stats": self.stats,
            **self.raw_data,
        }


@dataclass
class ScrapedQuest:
    """Represents a scraped quest from the wiki."""

    id: str
    name: str
    giver: str = ""
    description: str = ""
    objectives: list[dict] = field(default_factory=list)
    rewards: dict[str, Any] = field(default_factory=dict)
    prerequisites: list[str] = field(default_factory=list)
    raw_data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "giver": self.giver,
            "description": self.description,
            "objectives": self.objectives,
            "rewards": self.rewards,
            "prerequisites": self.prerequisites,
            **self.raw_data,
        }


@dataclass
class ScrapedProject:
    """Represents a scraped hideout project from the wiki."""

    id: str
    name: str
    description: str = ""
    phases: list[dict] = field(default_factory=list)
    total_costs: dict[str, int] = field(default_factory=dict)
    raw_data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "phases": self.phases,
            "totalCosts": self.total_costs,
            **self.raw_data,
        }


@dataclass
class MapMarker:
    """Represents a map marker from MetaForge."""

    lat: float
    lng: float
    category: str
    subcategory: str
    instance_name: str
    raw_data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "lat": self.lat,
            "lng": self.lng,
            "category": self.category,
            "subcategory": self.subcategory,
            "instanceName": self.instance_name,
            **self.raw_data,
        }


class BaseScraper(ABC):
    """Base class for all scrapers."""

    def __init__(self, client: httpx.Client | None = None, delay_ms: int = RATE_LIMIT_MS) -> None:
        self._client = client if client else httpx.Client()
        self.delay_ms = delay_ms
        self._last_request_time: float = 0.0

    def _rate_limit(self) -> None:
        """Apply rate limiting between requests."""
        elapsed = (time.perf_counter() - self._last_request_time) * 1000
        if elapsed < self.delay_ms:
            time.sleep((self.delay_ms - elapsed) / 1000)
        self._last_request_time = time.perf_counter()

    def _get(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make a GET request with rate limiting and error handling."""
        self._rate_limit()
        response = self._client.get(url, timeout=30, **kwargs)
        response.raise_for_status()
        return response

    @abstractmethod
    def scrape(self) -> dict[str, Any]:
        """Scrape data and return as dictionary."""
        pass


class MetaforgeScraper(BaseScraper):
    """Scraper for MetaForge game map data API."""

    def scrape(self) -> dict[str, Any]:
        """Scrape all map data from MetaForge."""
        result: dict[str, Any] = {"questMarkers": {}, "locationMarkers": {}, "rawData": {}}
        for map_id in MAP_IDS:
            try:
                params = {"mapID": map_id, "tableID": "arc_map_data"}
                data = self._get(METAFORGE_GAME_DATA_URL, params=params).json()
                markers = data.get("markers", [])
                result["questMarkers"][map_id] = [
                    MapMarker(
                        lat=m.get("lat", 0),
                        lng=m.get("lng", 0),
                        category=m.get("category", ""),
                        subcategory=m.get("subcategory", ""),
                        instance_name=m.get("instanceName", ""),
                    ).to_dict()
                    for m in markers
                    if m.get("category") == "quest"
                ]
                result["locationMarkers"][map_id] = [
                    MapMarker(
                        lat=m.get("lat", 0),
                        lng=m.get("lng", 0),
                        category=m.get("category", ""),
                        subcategory=m.get("subcategory", ""),
                        instance_name=m.get("instanceName", ""),
                    ).to_dict()
                    for m in markers
                    if m.get("category") in ("location", "poi", "extract", "spawn")
                ]
                result["rawData"][map_id] = data
            except Exception:  # noqa: BLE001
                result["questMarkers"][map_id] = []
                result["locationMarkers"][map_id] = []
                result["rawData"][map_id] = {}
        return result


class WikiItemScraper(BaseScraper):
    """Scraper for Arc Raiders Wiki item pages."""

    def _extract_recycle_info(self, soup: BeautifulSoup) -> list[dict]:
        """Extract recycling information from the page."""
        breaks_into: list[dict] = []
        for heading in soup.find_all(["h2", "h3"]):
            text = heading.get_text(strip=True).lower()
            if "recycle" in text or "break" in text:
                next_elem = heading.find_next_sibling()
                while next_elem and next_elem.name not in ("ul", "ol", "table"):
                    next_elem = next_elem.find_next_sibling()
                if next_elem and next_elem.name in ("ul", "ol"):
                    for li in next_elem.find_all("li"):
                        item_text = li.get_text(strip=True)
                        match = re.match(r"(.+?)\s*\((\d+)\)", item_text)
                        if match:
                            breaks_into.append({"item": match.group(1).strip(), "amount": int(match.group(2))})
                        else:
                            breaks_into.append({"item": item_text, "amount": 1})
        return breaks_into

    def _parse_item_page(self, url: str) -> ScrapedItem | None:
        """Parse a single item page."""
        try:
            response = self._get(url)
            soup = BeautifulSoup(response.content, "html.parser")

            title_elem = soup.find("h1", {"id": "firstHeading"})
            name = title_elem.get_text(strip=True) if title_elem else ""

            item_id = name.lower().replace(" ", "-").replace("'", "").replace("(", "").replace(")", "")

            infobox: dict[str, Any] = {}
            infobox_elem = soup.find("table", {"class": "infobox"})
            if infobox_elem:
                for row in infobox_elem.find_all("tr"):
                    header = row.find("th")
                    cell = row.find("td")
                    if header and cell:
                        key = header.get_text(strip=True).lower().replace(" ", "_")
                        value = cell.get_text(strip=True)
                        infobox[key] = value

            rarity = infobox.get("rarity", "").capitalize()
            if not rarity:
                for elem in soup.find_all(text=re.compile(r"Common|Uncommon|Rare|Epic|Legendary", re.I)):
                    rarity = elem.strip()
                    break

            value = 0
            value_text = infobox.get("value", infobox.get("price", infobox.get("sell_price", "")))
            if value_text:
                match = re.search(r"(\d+)", str(value_text).replace(",", ""))
                if match:
                    value = int(match.group(1))

            item_type = infobox.get("type", "").capitalize()

            return ScrapedItem(
                id=item_id,
                name=name,
                rarity=rarity,
                item_type=item_type,
                value=value,
                description=infobox.get("description", ""),
                breaks_into=self._extract_recycle_info(soup),
                stats={k: v for k, v in infobox.items() if k not in ("rarity", "type", "value", "description")},
                raw_data={"url": url},
            )

        except Exception:  # noqa: BLE001
            return None

    def scrape(self) -> dict[str, Any]:
        """Scrape all items from the wiki."""
        items: list[dict] = []

        categories = ["Items", "Weapons", "Mods", "Augments", "Shields", "Healing", "Quick_Use", "Grenades"]

        for category in categories:
            url = f"{WIKI_BASE}/{category}"
            try:
                response = self._get(url)
                soup = BeautifulSoup(response.content, "html.parser")

                content = soup.find("div", {"id": "mw-content-text"})
                if content:
                    for link in content.find_all("a", href=True):
                        href = link["href"]
                        if href.startswith("/wiki/") and not href.startswith("/wiki/Category"):
                            full_url = f"{WIKI_BASE}{href[5:]}"
                            item = self._parse_item_page(full_url)
                            if item:
                                items.append(item.to_dict())
            except Exception:  # noqa: BLE001
                continue

        return {
            "items": items,
            "metadata": {"source": "arc-raiders-wiki", "totalItems": len(items)},
        }


class WikiQuestScraper(BaseScraper):
    """Scraper for Arc Raiders Wiki quest pages."""

    def _parse_objectives(self, soup: BeautifulSoup) -> list[dict]:
        """Extract quest objectives."""
        objectives: list[dict] = []
        for heading in soup.find_all(["h2", "h3"]):
            text = heading.get_text(strip=True).lower()
            if "objective" in text:
                next_elem = heading.find_next_sibling()
                while next_elem and next_elem.name not in ("ul", "ol"):
                    next_elem = next_elem.find_next_sibling()
                if next_elem and next_elem.name in ("ul", "ol"):
                    for i, li in enumerate(next_elem.find_all("li"), 1):
                        objectives.append({"order": i, "description": li.get_text(strip=True), "completed": False})
        return objectives

    def _parse_rewards(self, soup: BeautifulSoup) -> dict[str, Any]:
        """Extract quest rewards."""
        rewards: dict[str, Any] = {"items": [], "credits": 0, "xp": 0, "other": []}
        for heading in soup.find_all(["h2", "h3"]):
            text = heading.get_text(strip=True).lower()
            if "reward" in text:
                next_elem = heading.find_next_sibling()
                while next_elem and next_elem.name not in ("ul", "ol", "table"):
                    next_elem = next_elem.find_next_sibling()
                if next_elem and next_elem.name in ("ul", "ol"):
                    for li in next_elem.find_all("li"):
                        item_text = li.get_text(strip=True)
                        if "credit" in item_text.lower():
                            match = re.search(r"(\d+)", item_text.replace(",", ""))
                            if match:
                                rewards["credits"] = int(match.group(1))
                        elif "xp" in item_text.lower():
                            match = re.search(r"(\d+)", item_text.replace(",", ""))
                            if match:
                                rewards["xp"] = int(match.group(1))
                        else:
                            rewards["other"].append(item_text)
        return rewards

    def _parse_quest_page(self, quest_name: str) -> ScrapedQuest | None:
        """Parse a single quest page."""
        url = f"{WIKI_BASE}/{quest_name.replace(' ', '_')}"
        try:
            response = self._get(url)
            soup = BeautifulSoup(response.content, "html.parser")

            title_elem = soup.find("h1", {"id": "firstHeading"})
            name = title_elem.get_text(strip=True) if title_elem else quest_name

            quest_id = name.lower().replace(" ", "-").replace("'", "").replace("(", "").replace(")", "")

            infobox: dict[str, Any] = {}
            infobox_elem = soup.find("table", {"class": "infobox"})
            if infobox_elem:
                for row in infobox_elem.find_all("tr"):
                    header = row.find("th")
                    cell = row.find("td")
                    if header and cell:
                        key = header.get_text(strip=True).lower().replace(" ", "_")
                        value = cell.get_text(strip=True)
                        infobox[key] = value

            return ScrapedQuest(
                id=quest_id,
                name=name,
                giver=infobox.get("given_by", infobox.get("giver", "")),
                description=infobox.get("description", ""),
                objectives=self._parse_objectives(soup),
                rewards=self._parse_rewards(soup),
                raw_data={"url": url},
            )

        except Exception:  # noqa: BLE001
            return None

    def scrape(self) -> dict[str, Any]:
        """Scrape all quests from the wiki."""
        quests: list[dict] = []

        url = f"{WIKI_BASE}/Quests"
        try:
            response = self._get(url)
            soup = BeautifulSoup(response.content, "html.parser")

            quest_names: list[str] = []
            content = soup.find("div", {"id": "mw-content-text"})
            if content:
                for link in content.find_all("a", href=True):
                    href = link["href"]
                    if href.startswith("/wiki/") and "Quest" in link.get_text():
                        quest_names.append(link.get_text(strip=True))

            for quest_name in set(quest_names):
                quest = self._parse_quest_page(quest_name)
                if quest:
                    quests.append(quest.to_dict())

        except Exception:  # noqa: BLE001
            pass

        return {
            "quests": quests,
            "metadata": {"source": "arc-raiders-wiki", "totalQuests": len(quests)},
        }


class WikiProjectScraper(BaseScraper):
    """Scraper for Arc Raiders Wiki hideout project pages."""

    def _parse_phase_requirements(self, soup: BeautifulSoup) -> list[dict]:
        """Extract project phase requirements."""
        phases: list[dict] = []
        for heading in soup.find_all(["h2", "h3"]):
            text = heading.get_text(strip=True).lower()
            if "phase" in text or "level" in text or "upgrade" in text:
                phase_data: dict[str, Any] = {
                    "phase": len(phases) + 1,
                    "name": heading.get_text(strip=True),
                    "requirements": [],
                    "unlocks": [],
                }
                next_elem = heading.find_next_sibling()
                while next_elem and next_elem.name not in ("ul", "ol", "table"):
                    next_elem = next_elem.find_next_sibling()
                if next_elem and next_elem.name in ("ul", "ol"):
                    for li in next_elem.find_all("li"):
                        item_text = li.get_text(strip=True)
                        match = re.match(r"(.+?)\s*x?\s*(\d+)", item_text)
                        if match:
                            phase_data["requirements"].append(
                                {
                                    "item": match.group(1).strip(),
                                    "amount": int(match.group(2)),
                                }
                            )
                phases.append(phase_data)
        return phases

    def _parse_project_page(self, url: str) -> ScrapedProject | None:
        """Parse a single project page."""
        try:
            response = self._get(url)
            soup = BeautifulSoup(response.content, "html.parser")

            title_elem = soup.find("h1", {"id": "firstHeading"})
            name = title_elem.get_text(strip=True) if title_elem else ""

            project_id = name.lower().replace(" ", "-").replace("'", "").replace("(", "").replace(")", "")

            phases = self._parse_phase_requirements(soup)

            total_costs: dict[str, int] = {}
            for phase in phases:
                for req in phase.get("requirements", []):
                    item = req.get("item", "")
                    amount = req.get("amount", 0)
                    total_costs[item] = total_costs.get(item, 0) + amount

            return ScrapedProject(
                id=project_id,
                name=name,
                description="",
                phases=phases,
                total_costs=total_costs,
                raw_data={"url": url},
            )

        except Exception:  # noqa: BLE001
            return None

    def scrape(self) -> dict[str, Any]:
        """Scrape all hideout projects from the wiki."""
        projects: list[dict] = []

        url = f"{WIKI_BASE}/Projects"
        try:
            response = self._get(url)
            soup = BeautifulSoup(response.content, "html.parser")

            expedition_urls: list[str] = []
            content = soup.find("div", {"id": "mw-content-text"})
            if content:
                for link in content.find_all("a", href=True):
                    href = link["href"]
                    text = link.get_text(strip=True).lower()
                    if href.startswith("/wiki/") and ("expedition" in text or "project" in text):
                        full_url = f"{WIKI_BASE}{href[5:]}"
                        expedition_urls.append(full_url)

            for proj_url in set(expedition_urls):
                project = self._parse_project_page(proj_url)
                if project:
                    projects.append(project.to_dict())

        except Exception:  # noqa: BLE001
            pass

        return {
            "projects": projects,
            "metadata": {"source": "arc-raiders-wiki", "totalProjects": len(projects)},
        }


__all__ = [
    "BaseScraper",
    "MetaforgeScraper",
    "WikiItemScraper",
    "WikiQuestScraper",
    "WikiProjectScraper",
    "ScrapedItem",
    "ScrapedQuest",
    "ScrapedProject",
    "MapMarker",
    "ScrapingError",
]
