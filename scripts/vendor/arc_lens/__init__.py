"""Arc-Lens data scraping pipeline ported from JavaScript to Python.

This module provides scrapers for Arc Raiders game data from:
- arcraiders.wiki (items, quests, projects)
- metaforge.app API (quest markers)

Based on https://github.com/eetusa/arc-lens
"""

from __future__ import annotations

__all__ = [
    "WikiItemScraper",
    "WikiQuestScraper",
    "WikiProjectScraper",
    "MetaforgeScraper",
]
