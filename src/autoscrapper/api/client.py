"""ArcTracker API client with rate limiting and OCR fallback support."""

from __future__ import annotations
import concurrent.futures
import math

import logging
import functools
from pathlib import Path
from types import MappingProxyType
import time
from typing import TYPE_CHECKING, Any

import httpx
from pydantic import ValidationError
import orjson

from .models import (
    Blueprint,
    HideoutModule,
    ItemDecision,
    ProjectProgress,
    RateLimitState,
    RoundEntry,
    StashData,
    StashItem,
    UserProfile,
    UserQuest,
)

if TYPE_CHECKING:
    from ..config import ApiSettings
    from ..core.item_actions import ActionMap

DATA_DIR = Path(__file__).resolve().parent.parent / "progress" / "data"

_log = logging.getLogger(__name__)

ARCTRACKER_BASE_URL = "https://arctracker.io"
DEFAULT_TIMEOUT = 30

# Rate limit: 500 req/hour = 1 req per 7.2 seconds max sustained
# We use a more conservative 8 seconds to stay well under the limit
MIN_REQUEST_INTERVAL_SECONDS = 8.0


@functools.cache
def _get_cached_item_mappings() -> tuple[MappingProxyType[str, str], MappingProxyType[str, str]]:
    """Load and cache item ID to display name mapping from items.json."""
    id_to_name: dict[str, str] = {}
    name_to_id: dict[str, str] = {}
    try:
        items_path = DATA_DIR / "items.json"
        raw = orjson.loads(items_path.read_bytes())
        if isinstance(raw, list):
            for item in raw:
                try:
                    item_id = item["id"]
                    item_name = item["name"]
                    if isinstance(item_id, str) and isinstance(item_name, str):
                        lower_name = item_name.lower()
                        id_to_name[item_id] = item_name
                        name_to_id[lower_name] = item_id
                except (KeyError, TypeError):
                    continue
    except Exception as exc:
        _log.warning("api: Failed to load item mapping: %s", exc)
    return MappingProxyType(id_to_name), MappingProxyType(name_to_id)


class ArcTrackerAuth(httpx.Auth):
    """Custom auth to securely inject keys without exposing them in default headers."""

    def __init__(self, app_key: str | None, user_key: str | None) -> None:
        self.app_key = app_key
        self.user_key = user_key

    def auth_flow(self, request: httpx.Request):
        if self.app_key:
            request.headers["X-App-Key"] = self.app_key
        if self.user_key:
            request.headers["Authorization"] = f"Bearer {self.user_key}"
        yield request


class ArcTrackerClient:
    """Client for arctracker.io API with rate limiting and fallback support."""

    def __init__(
        self,
        app_key: str | None = None,
        user_key: str | None = None,
        base_url: str = ARCTRACKER_BASE_URL,
    ) -> None:
        self.app_key = app_key
        self.user_key = user_key
        self.base_url = base_url.rstrip("/")
        self.rate_limit = RateLimitState()
        self._session = httpx.Client(
            headers={
                "Accept": "application/json",
                "User-Agent": "ArcRaiders-AutoScrapper/0.2.0",
            },
            verify=True,
        )
        self._item_id_to_name, self._item_name_to_id = _get_cached_item_mappings()

    def _wait_for_rate_limit(self) -> None:
        """Pre-emptively throttle requests to respect rate limits."""
        wait_time = self.rate_limit.time_until_next_request(MIN_REQUEST_INTERVAL_SECONDS)
        if wait_time > 0:
            _log.debug("api: Rate limit cooldown: %.2fs", wait_time)
            time.sleep(wait_time)

    def _update_rate_limit(self, headers: dict[str, str]) -> None:
        """Update rate limit state from response headers."""
        try:
            if "X-RateLimit-Limit" in headers:
                self.rate_limit.limit = int(headers["X-RateLimit-Limit"])
            if "X-RateLimit-Remaining" in headers:
                self.rate_limit.remaining = int(headers["X-RateLimit-Remaining"])
            if "X-RateLimit-Reset" in headers:
                # Reset is usually a Unix timestamp
                reset_val = int(headers["X-RateLimit-Reset"])
                # Handle both absolute timestamp and relative seconds
                if reset_val > 1_000_000_000:  # Unix timestamp
                    self.rate_limit.reset_timestamp = float(reset_val)
                else:  # Relative seconds
                    self.rate_limit.reset_timestamp = time.time() + reset_val
        except (ValueError, TypeError) as exc:
            _log.debug("api: Failed to parse rate limit headers: %s", exc)

        self.rate_limit.last_request_timestamp = time.time()

    def _get_headers(self) -> dict[str, str]:
        """Build request headers."""
        return {}

    def _make_request(
        self,
        method: str,
        endpoint: str,
        *,
        require_auth: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any] | None:
        """Make an HTTP request with rate limiting and error handling."""
        if require_auth and (not self.app_key or not self.user_key):
            _log.debug("api: Auth required but keys not configured")
            return None

        self._wait_for_rate_limit()

        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        auth = ArcTrackerAuth(self.app_key, self.user_key) if require_auth else None

        try:
            response = self._session.request(
                method,
                url,
                headers=headers,
                auth=auth,
                timeout=DEFAULT_TIMEOUT,
                **kwargs,
            )
            self._update_rate_limit(dict(response.headers))

            if response.status_code == 429:
                _log.warning("api: Rate limited (429)")
                return None
            if response.status_code == 401:
                _log.warning("api: Unauthorized (401) - check your app/user keys")
                return None
            if response.status_code == 403:
                _log.warning("api: Forbidden (403) - insufficient scope or app suspended")
                return None

            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            _log.warning("api: Request timeout to %s", endpoint)
        except httpx.RequestError as exc:
            _log.warning("api: Request failed: %s", exc)
        except Exception as exc:
            _log.warning("api: Unexpected error: %s", exc)

        return None

    def get_public_items(self, locale: str = "en") -> dict[str, Any] | None:
        """Fetch public item data from /api/items (no auth required)."""
        return self._make_request("GET", "/api/items", require_auth=False, params={"locale": locale})

    def get_public_hideout(self, locale: str = "en") -> dict[str, Any] | None:
        """Fetch public hideout data from /api/hideout (no auth required)."""
        return self._make_request("GET", "/api/hideout", require_auth=False, params={"locale": locale})

    def get_public_projects(self, locale: str = "en", season: int | None = None) -> dict[str, Any] | None:
        """Fetch public projects data from /api/projects (no auth required)."""
        params: dict[str, Any] = {"locale": locale}
        if season is not None:
            params["season"] = season
        return self._make_request("GET", "/api/projects", require_auth=False, params=params)

    def get_user_stash(
        self,
        locale: str = "en",
        page: int = 1,
        per_page: int = 500,
        sort: str = "slot",
    ) -> StashData:
        """Fetch user's stash from /api/v2/user/stash (auth required)."""
        result = StashData()

        if not self.is_configured():
            result.api_error = "API not configured (missing app_key or user_key)"
            return result

        data = self._make_request(
            "GET",
            "/api/v2/user/stash",
            require_auth=True,
            params={
                "locale": locale,
                "page": page,
                "per_page": min(per_page, 500),
                "sort": sort,
            },
        )

        if data is None:
            result.api_error = "Failed to fetch stash from API"
            return result

        return self._parse_stash_response(data)

    def get_all_stash_items(self, locale: str = "en") -> StashData:
        """Fetch all stash items across all pages concurrently."""
        all_items: list[StashItem] = []
        per_page = 500

        # Fetch first page sequentially to get total used slots
        first_page = self.get_user_stash(locale=locale, page=1, per_page=per_page)

        if first_page.api_error:
            return StashData(
                items=[],
                total_slots=0,
                used_slots=0,
                api_error=first_page.api_error,
            )

        all_items.extend(first_page.items)
        total_slots = first_page.total_slots
        used_slots = first_page.used_slots

        # If first page has fewer items than per_page, we're done
        if len(first_page.items) < per_page or not first_page.items:
            return StashData(
                items=all_items,
                total_slots=total_slots,
                used_slots=used_slots,
                api_error=None,
            )

        # Calculate remaining pages based on used_slots
        # used_slots tells us the total number of items to fetch
        # total pages is ceil(used_slots / per_page)
        total_pages = math.ceil(used_slots / per_page)

        # Limit to 100 pages to prevent runaway requests
        if total_pages > 100:
            _log.warning("api: Stash pagination calculated >100 pages, limiting to 100")
            total_pages = 100

        if total_pages > 1:

            def fetch_page(p: int) -> StashData:
                return self.get_user_stash(locale=locale, page=p, per_page=per_page)

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                pages_to_fetch = range(2, total_pages + 1)
                # Map preserves order
                results = executor.map(fetch_page, pages_to_fetch)

                for page_data in results:
                    if page_data.api_error:
                        return StashData(
                            items=all_items,
                            total_slots=total_slots,
                            used_slots=used_slots,
                            api_error=page_data.api_error,
                        )

                    all_items.extend(page_data.items)

                    # If a page returns empty, stop processing further pages
                    if not page_data.items:
                        break

        return StashData(
            items=all_items,
            total_slots=total_slots,
            used_slots=used_slots,
            api_error=None,
        )

    def _parse_stash_response(self, data: dict[str, Any]) -> StashData:
        """Parse API stash response into structured result."""
        result = StashData()
        stash_data = data.get("data", data)
        if not isinstance(stash_data, dict):
            _log.warning("api: Unexpected stash response format")
            return result

        result.total_slots = int(stash_data.get("totalSlots", 0))
        result.used_slots = int(stash_data.get("usedSlots", 0))

        items_data = stash_data.get("items", [])
        if not isinstance(items_data, list):
            _log.warning("api: Unexpected stash items format")
            return result

        for item_data in items_data:
            if isinstance(item_data, dict):
                result.items.append(StashItem.from_api(item_data))

        return result

    def get_user_hideout(self, locale: str = "en") -> list[HideoutModule]:
        """Fetch user's hideout progress from /api/v2/user/hideout (auth required)."""
        if not self.is_configured():
            _log.warning("api: Cannot fetch hideout - API not configured")
            return []

        data = self._make_request(
            "GET",
            "/api/v2/user/hideout",
            require_auth=True,
            params={"locale": locale},
        )

        if data is None:
            return []

        modules_data = data.get("data", [])
        if not isinstance(modules_data, list):
            _log.warning("api: Unexpected hideout response format")
            return []

        return [HideoutModule.from_api(m) for m in modules_data if isinstance(m, dict)]

    def get_user_projects(
        self,
        locale: str = "en",
        season: int | None = None,
    ) -> list[ProjectProgress]:
        """Fetch user's project progress from /api/v2/user/projects (auth required)."""
        if not self.is_configured():
            _log.warning("api: Cannot fetch projects - API not configured")
            return []

        params: dict[str, Any] = {"locale": locale}
        if season is not None:
            params["season"] = season

        data = self._make_request(
            "GET",
            "/api/v2/user/projects",
            require_auth=True,
            params=params,
        )

        if data is None:
            return []

        projects_data = data.get("data", [])
        if not isinstance(projects_data, list):
            _log.warning("api: Unexpected projects response format")
            return []

        return [ProjectProgress.from_api(p) for p in projects_data if isinstance(p, dict)]

    def get_user_profile(self) -> UserProfile | None:
        """Fetch user profile from /api/v2/user/profile (auth required)."""
        if not self.is_configured():
            return None
        data = self._make_request("GET", "/api/v2/user/profile", require_auth=True)
        if data is None:
            return None
        profile_data = data.get("data", data)
        if not isinstance(profile_data, dict):
            return None
        try:
            return UserProfile.from_api(profile_data)
        except ValidationError as e:
            _log.warning(f"api: Failed to validate user profile response: {e}")
            return None

    def get_user_quests(
        self,
        locale: str = "en",
        filter: str | None = None,
    ) -> list[UserQuest]:
        """Fetch user quest progress from /api/v2/user/quests (auth required)."""
        if not self.is_configured():
            return []
        params: dict[str, Any] = {"locale": locale}
        if filter is not None:
            params["filter"] = filter
        data = self._make_request("GET", "/api/v2/user/quests", require_auth=True, params=params)
        if data is None:
            return []
        quests_data = data.get("data", [])
        if not isinstance(quests_data, list):
            _log.warning("api: Unexpected quests response format")
            return []
        return [UserQuest.from_api(q) for q in quests_data if isinstance(q, dict)]

    def get_user_rounds(
        self,
        locale: str = "en",
        limit: int = 50,
        offset: int = 0,
        outcome: str | None = None,
        map_slug: str | None = None,
        season: int | None = None,
    ) -> list[RoundEntry]:
        """Fetch user round history from /api/v2/user/rounds (auth required)."""
        if not self.is_configured():
            return []
        params: dict[str, Any] = {
            "locale": locale,
            "limit": min(limit, 200),
            "offset": offset,
        }
        if outcome is not None:
            params["outcome"] = outcome
        if map_slug is not None:
            params["map"] = map_slug
        if season is not None:
            params["season"] = season
        data = self._make_request("GET", "/api/v2/user/rounds", require_auth=True, params=params)
        if data is None:
            return []
        rounds_data = data.get("data", [])
        if not isinstance(rounds_data, list):
            _log.warning("api: Unexpected rounds response format")
            return []
        return [RoundEntry.from_api(r) for r in rounds_data if isinstance(r, dict)]

    def get_user_loadout(self, locale: str = "en") -> dict[str, Any] | None:
        """Fetch user loadout from /api/v2/user/loadout (auth required)."""
        if not self.is_configured():
            return None
        data = self._make_request("GET", "/api/v2/user/loadout", require_auth=True, params={"locale": locale})
        if data is None:
            return None
        return data.get("data", data)

    def get_user_blueprints(
        self,
        locale: str = "en",
        filter: str | None = None,
    ) -> list[Blueprint]:
        """Fetch user blueprints from /api/v2/user/blueprints (auth required)."""
        if not self.is_configured():
            return []
        params: dict[str, Any] = {"locale": locale}
        if filter is not None:
            params["filter"] = filter
        data = self._make_request("GET", "/api/v2/user/blueprints", require_auth=True, params=params)
        if data is None:
            return []
        blueprints_data = data.get("data", [])
        if not isinstance(blueprints_data, list):
            _log.warning("api: Unexpected blueprints response format")
            return []
        return [Blueprint.from_api(b) for b in blueprints_data if isinstance(b, dict)]

    def test_connection(self) -> dict[str, Any] | None:
        """Test API connection and authentication."""
        if not self.is_configured():
            _log.warning("api: Cannot test connection - API not configured")
            return None

        return self._make_request("GET", "/api/v2/user/profile", require_auth=True)

    def is_configured(self) -> bool:
        """Check if API client has necessary configuration."""
        return bool(self.app_key and self.user_key)

    def is_public_available(self) -> bool:
        """Check if public API endpoints are reachable."""
        return True


class APIOrchestrator:
    """Orchestrates API and OCR data sources with automatic fallback."""

    def __init__(self, client: ArcTrackerClient, actions: ActionMap) -> None:
        self.client = client
        self.actions = actions
        self._log = logging.getLogger(__name__)

    def get_item_decisions(
        self,
        *,
        prefer_api: bool = True,
    ) -> dict[str, ItemDecision]:
        """
        Get decisions for items from the API.

        Returns a mapping of item names to decisions.
        Falls back to empty dict if API fails or is not preferred.
        """
        decisions: dict[str, ItemDecision] = {}

        if not prefer_api or not self.client.is_configured():
            return decisions

        try:
            stash_data = self.client.get_all_stash_items()
            if stash_data.api_error:
                self._log.warning("api: Stash fetch failed: %s", stash_data.api_error)
                return decisions

            from ..core.item_actions import normalize_item_name
            from ..ocr.inventory_vision import match_item_name

            for item in stash_data.items:
                normalized_name = normalize_item_name(item.name)
                decision_list = self.actions.get(normalized_name)
                if decision_list:
                    decisions[item.name] = decision_list[0]
                else:
                    # Fallback to fuzzy match if exact match fails
                    matched_name = match_item_name(item.name)
                    if matched_name:
                        decision_list = self.actions.get(matched_name)
                        if decision_list:
                            decisions[item.name] = decision_list[0]

            self._log.info(
                "api: Retrieved %d decisions from API stash",
                len(decisions),
            )
        except Exception as exc:
            self._log.error("api: Unexpected error during decision orchestration: %s", exc)

        return decisions


def create_client_from_config(
    config: dict[str, Any] | ApiSettings | None = None,
) -> ArcTrackerClient:
    """Create API client from config dict or ApiSettings (loaded from settings)."""
    if config is None:
        from ..config import load_api_settings

        settings = load_api_settings()
        return ArcTrackerClient(
            app_key=settings.app_key or None,
            user_key=settings.user_key or None,
            base_url=settings.base_url,
        )

    if isinstance(config, dict):
        return ArcTrackerClient(
            app_key=config.get("app_key") or None,
            user_key=config.get("user_key") or None,
            base_url=config.get("base_url", ARCTRACKER_BASE_URL),
        )

    # It's an ApiSettings object
    return ArcTrackerClient(
        app_key=config.app_key or None,
        user_key=config.user_key or None,
        base_url=config.base_url,
    )
