import pytest
import unittest.mock as mock
from autoscrapper.progress.data_update import (
    _fetch_supabase_all,
    update_data_snapshot,
    DownloadError,
)


def test_fetch_supabase_all_missing_key():
    with mock.patch("autoscrapper.progress.data_update.SUPABASE_ANON_KEY", None):
        with pytest.raises(
            DownloadError,
            match="METAFORGE_SUPABASE_ANON_KEY environment variable is not set",
        ):
            _fetch_supabase_all("some_table")


def test_update_data_snapshot_handles_missing_key(tmp_path):
    # Mock _fetch_all_items and _fetch_all_quests to avoid network calls
    with (
        mock.patch(
            "autoscrapper.progress.data_update._fetch_all_items", return_value=[]
        ),
        mock.patch(
            "autoscrapper.progress.data_update._fetch_all_quests", return_value=[]
        ),
        mock.patch("autoscrapper.progress.data_update.SUPABASE_ANON_KEY", None),
        mock.patch("autoscrapper.progress.data_update._log") as mock_log,
    ):
        metadata = update_data_snapshot(tmp_path)

        # Verify it continued despite the missing key
        assert metadata["itemCount"] == 0
        assert metadata["questCount"] == 0

        # Verify it logged warnings for both attempts to fetch from Supabase
        assert mock_log.warning.call_count == 2
        args, _ = mock_log.warning.call_args_list[0]
        assert "Skipping crafting component data" in args[0]
        assert "METAFORGE_SUPABASE_ANON_KEY environment variable is not set" in str(
            args[1]
        )
