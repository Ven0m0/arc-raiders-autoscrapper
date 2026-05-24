"""Tests for ArcTracker API client and orchestrator."""

import pytest
from unittest.mock import patch
from autoscrapper.api.client import ArcTrackerClient, APIOrchestrator
from autoscrapper.api.models import StashData, StashItem


@pytest.fixture
def mock_actions():
    return {"matriarch reactor": ["KEEP"], "fabric": ["SELL"]}


@pytest.fixture
def api_client():
    return ArcTrackerClient(app_key="test_app", user_key="test_user")


class TestArcTrackerClient:
    def test_make_request_injects_keys(self, api_client):
        from unittest.mock import patch, MagicMock
        with patch.object(api_client._session, 'request') as mock_req:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {}
            mock_response.json.return_value = {}
            mock_req.return_value = mock_response

            api_client._make_request("GET", "/test", require_auth=True)

            mock_req.assert_called_once()
            headers = mock_req.call_args[1].get("headers", {})
            assert headers.get("X-App-Key") == "test_app"
            assert headers.get("Authorization") == "Bearer test_user"

    def test_rate_limit_tracking(self, api_client):
        headers = {
            "X-RateLimit-Limit": "500",
            "X-RateLimit-Remaining": "499",
            "X-RateLimit-Reset": "10",  # relative
        }
        api_client._update_rate_limit(headers)
        assert api_client.rate_limit.remaining == 499
        assert api_client.rate_limit.reset_timestamp > 0

    def test_rate_limit_parsing_handles_invalid_values(self, api_client, caplog):
        import logging

        headers = {
            "X-RateLimit-Limit": "not-an-int",
            "X-RateLimit-Remaining": "also-not-an-int",
            "X-RateLimit-Reset": "definitely-not-an-int",
        }
        with caplog.at_level(logging.DEBUG):
            api_client._update_rate_limit(headers)

        assert "Failed to parse rate limit headers" in caplog.text
        # Values should remain at their defaults
        assert api_client.rate_limit.limit == 500
        assert api_client.rate_limit.remaining == 500


class TestAPIOrchestrator:
    def test_get_item_decisions_maps_correctly(self, api_client, mock_actions):
        orchestrator = APIOrchestrator(api_client, mock_actions)

        mock_stash = StashData(
            items=[
                StashItem(
                    item_id="1",
                    name="Matriarch Reactor",
                    quantity=1,
                    slot=0,
                    item_type="Refined",
                    rarity="Common",
                    value=100,
                ),
                StashItem(
                    item_id="2", name="Fabric", quantity=5, slot=1, item_type="Material", rarity="Common", value=10
                ),
                StashItem(
                    item_id="3", name="Unknown Item", quantity=1, slot=2, item_type="Other", rarity="Common", value=0
                ),
            ]
        )

        with patch.object(api_client, "get_all_stash_items", return_value=mock_stash):
            decisions = orchestrator.get_item_decisions(prefer_api=True)

            assert decisions["Matriarch Reactor"] == "KEEP"
            assert decisions["Fabric"] == "SELL"
            assert "Unknown Item" not in decisions

    def test_get_item_decisions_handles_api_error(self, api_client, mock_actions):
        orchestrator = APIOrchestrator(api_client, mock_actions)

        mock_stash = StashData(api_error="Connection failed")

        with patch.object(api_client, "get_all_stash_items", return_value=mock_stash):
            decisions = orchestrator.get_item_decisions(prefer_api=True)
            assert decisions == {}


def test_get_cached_item_mappings_handles_error(caplog):
    import logging
    from autoscrapper.api.client import _get_cached_item_mappings

    _get_cached_item_mappings.cache_clear()

    with caplog.at_level(logging.WARNING):
        with patch("pathlib.Path.read_bytes", side_effect=Exception("Test file read error")):
            id_to_name, name_to_id = _get_cached_item_mappings()

    assert len(id_to_name) == 0
    assert len(name_to_id) == 0
    assert "api: Failed to load item mapping: Test file read error" in caplog.text
