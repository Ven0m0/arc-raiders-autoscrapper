"""Tests for ArcTracker API models."""

import time
from unittest.mock import patch
from autoscrapper.api.models import RateLimitState


def test_is_rate_limited():
    """Test is_rate_limited property logic."""
    # Scenario 1: Remaining > 0
    state = RateLimitState(remaining=10, reset_timestamp=time.time() + 100)
    assert state.is_rate_limited is False

    # Scenario 2: Remaining <= 0, but reset_timestamp has passed
    with patch("time.time", return_value=1000.0):
        state = RateLimitState(remaining=0, reset_timestamp=900.0)
        assert state.is_rate_limited is False

    # Scenario 3: Remaining <= 0, and reset_timestamp is in the future
    with patch("time.time", return_value=1000.0):
        state = RateLimitState(remaining=0, reset_timestamp=1100.0)
        assert state.is_rate_limited is True


def test_seconds_until_reset():
    """Test seconds_until_reset property logic."""
    # Scenario 1: reset_timestamp is in the future
    with patch("time.time", return_value=1000.0):
        state = RateLimitState(reset_timestamp=1010.5)
        assert state.seconds_until_reset == 10.5

    # Scenario 2: reset_timestamp is in the past
    with patch("time.time", return_value=1000.0):
        state = RateLimitState(reset_timestamp=990.0)
        assert state.seconds_until_reset == 0.0


def test_time_until_next_request():
    """Test time_until_next_request calculation logic."""
    # Scenario 1: Not rate limited, cooldown still active
    # last_request = 995, now = 1000, min_interval = 8.0 -> cooldown = 3.0
    with patch("time.time", return_value=1000.0):
        state = RateLimitState(remaining=10, last_request_timestamp=995.0)
        assert state.time_until_next_request(min_interval=8.0) == 3.0

    # Scenario 2: Not rate limited, cooldown passed
    # last_request = 990, now = 1000, min_interval = 8.0 -> cooldown = 0.0
    with patch("time.time", return_value=1000.0):
        state = RateLimitState(remaining=10, last_request_timestamp=990.0)
        assert state.time_until_next_request(min_interval=8.0) == 0.0

    # Scenario 3: Rate limited, cooldown < reset_time
    # last_request = 995, now = 1000, min_interval = 8.0 -> cooldown = 3.0
    # reset_timestamp = 1010 -> seconds_until_reset = 10.0
    # Expected: max(3.0, 10.0) = 10.0
    with patch("time.time", return_value=1000.0):
        state = RateLimitState(remaining=0, last_request_timestamp=995.0, reset_timestamp=1010.0)
        assert state.time_until_next_request(min_interval=8.0) == 10.0

    # Scenario 4: Rate limited, cooldown > reset_time
    # last_request = 995, now = 1000, min_interval = 8.0 -> cooldown = 3.0
    # reset_timestamp = 1001 -> seconds_until_reset = 1.0
    # Expected: max(3.0, 1.0) = 3.0
    with patch("time.time", return_value=1000.0):
        state = RateLimitState(remaining=0, last_request_timestamp=995.0, reset_timestamp=1001.0)
        assert state.time_until_next_request(min_interval=8.0) == 3.0
