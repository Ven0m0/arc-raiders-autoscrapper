"""Arc-Lens data scraping pipeline ported from JavaScript to Python.

This module provides scrapers for Arc Raiders game data from:
- arcraiders.wiki (items, quests, projects)
- metaforge.app API (quest markers)

Based on https://github.com/eetusa/arc-lens
"""

from __future__ import annotations

from .scrapers import (
    BaseScraper,
    MapMarker,
    MetaforgeScraper,
    ScrapedItem,
    ScrapedProject,
    ScrapedQuest,
    ScrapingError,
    WikiItemScraper,
    WikiProjectScraper,
    WikiQuestScraper,
)

__all__ = [
    "BaseScraper",
    "WikiItemScraper",
    "WikiQuestScraper",
    "WikiProjectScraper",
    "MetaforgeScraper",
    "ScrapedItem",
    "ScrapedQuest",
    "ScrapedProject",
    "MapMarker",
    "ScrapingError",
]
