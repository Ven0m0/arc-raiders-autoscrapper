"""Tests for ArcTracker API models."""

from unittest.mock import patch

from autoscrapper.api.models import RateLimitState


@patch("time.time", return_value=1000.0)
def test_is_rate_limited_when_exhausted(mock_time):
    state = RateLimitState(remaining=0, reset_timestamp=1010.0)
    assert state.is_rate_limited is True


@patch("time.time", return_value=1000.0)
def test_is_not_rate_limited_when_remaining(mock_time):
    state = RateLimitState(remaining=5, reset_timestamp=1010.0)
    assert state.is_rate_limited is False


@patch("time.time", return_value=1000.0)
def test_is_not_rate_limited_after_reset(mock_time):
    state = RateLimitState(remaining=0, reset_timestamp=990.0)
    assert state.is_rate_limited is False


@patch("time.time", return_value=1000.0)
def test_seconds_until_reset(mock_time):
    state = RateLimitState(reset_timestamp=1010.0)
    assert state.seconds_until_reset == 10.0


@patch("time.time", return_value=1000.0)
def test_seconds_until_reset_already_passed(mock_time):
    state = RateLimitState(reset_timestamp=990.0)
    assert state.seconds_until_reset == 0.0


@patch("time.time", return_value=1000.0)
def test_time_until_next_request_when_limited(mock_time):
    state = RateLimitState(remaining=0, reset_timestamp=1010.0)
    wait = state.time_until_next_request(0.0)
    assert wait == 10.0


@patch("time.time", return_value=1000.0)
def test_time_until_next_request_when_not_limited(mock_time):
    state = RateLimitState(remaining=10, reset_timestamp=1010.0, last_request_timestamp=1000.0)
    wait = state.time_until_next_request(0.0)
    assert wait == 0.0
