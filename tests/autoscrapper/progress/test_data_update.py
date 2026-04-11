import io
import pytest
import unittest.mock as mock
import zipfile

import orjson
from autoscrapper.progress.data_update import (
    DownloadError,
    _fetch_supabase_all,
    _load_raidtheory_fallback_data,
    update_data_snapshot,
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
        mock.patch("autoscrapper.progress.data_update._fetch_all_items", return_value=[]),
        mock.patch("autoscrapper.progress.data_update._fetch_all_quests", return_value=[]),
        mock.patch(
            "autoscrapper.progress.data_update._load_raidtheory_fallback_data",
            return_value=([], []),
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
        error_msg = str(args[1])
        second_args, _ = mock_log.warning.call_args_list[1]
        assert "Skipping crafting component data" in args[0]
        assert "METAFORGE_SUPABASE_ANON_KEY environment variable is not set" in error_msg
        assert "Skipping recycle component data" in second_args[0]


def test_load_raidtheory_fallback_data_maps_archive_entries():
    archive_buffer = io.BytesIO()
    with zipfile.ZipFile(archive_buffer, "w") as archive:
        archive.writestr(
            "arcraiders-data-main/items/metal_parts.json",
            orjson.dumps(
                {
                    "id": "metal_parts",
                    "name": {"en": "Metal Parts"},
                    "type": "Basic Material",
                    "rarity": "Common",
                    "value": 100,
                    "weightKg": 0.25,
                    "stackSize": 5,
                    "recyclesInto": {"wires": 2},
                }
            ),
        )
        archive.writestr(
            "arcraiders-data-main/quests/a_bad_feeling.json",
            orjson.dumps(
                {
                    "id": "a_bad_feeling",
                    "name": {"en": "A Bad Feeling"},
                    "trader": "Celeste",
                    "objectives": [{"en": "Search an ARC Probe"}],
                    "rewardItemIds": [{"itemId": "metal_parts", "quantity": 3}],
                    "xp": 500,
                }
            ),
        )

    with mock.patch(
        "autoscrapper.progress.data_update._fetch_bytes",
        return_value=archive_buffer.getvalue(),
    ):
        items, quests = _load_raidtheory_fallback_data()

    assert items == [
        {
            "id": "metal-parts",
            "name": "Metal Parts",
            "type": "Basic Material",
            "rarity": "common",
            "value": 100,
            "weightKg": 0.25,
            "stackSize": 5,
            "craftBench": None,
            "updatedAt": mock.ANY,
            "recipe": None,
            "recyclesInto": {"wires": 2},
        }
    ]
    assert quests == [
        {
            "id": "a-bad-feeling",
            "name": "A Bad Feeling",
            "objectives": ["Search an ARC Probe"],
            "requirements": [],
            "rewardItemIds": ["metal-parts"],
            "rewards": [
                {
                    "item_id": "metal-parts",
                    "quantity": "3",
                    "item": {"id": "metal-parts", "name": "Metal Parts"},
                }
            ],
            "trader": "Celeste",
            "xp": 500,
            "sortOrder": 0,
        }
    ]


def test_update_data_snapshot_uses_raidtheory_fallback_and_tracks_sources(tmp_path):
    fallback_items = [
        {
            "id": "metal-parts",
            "name": "Metal Parts",
            "type": "Basic Material",
            "rarity": "common",
            "value": 100,
            "weightKg": 0.25,
            "stackSize": 5,
            "craftBench": None,
            "updatedAt": "2026-04-10T00:00:00Z",
            "recipe": None,
            "recyclesInto": {"wires": 2},
        }
    ]
    fallback_quests = [
        {
            "id": "a-bad-feeling",
            "name": "A Bad Feeling",
            "objectives": ["Search an ARC Probe"],
            "requirements": [],
            "rewardItemIds": ["metal-parts"],
            "rewards": [
                {
                    "item_id": "metal-parts",
                    "quantity": "3",
                    "item": {"id": "metal-parts", "name": "Metal Parts"},
                }
            ],
            "trader": "Celeste",
            "xp": 500,
            "sortOrder": 0,
        }
    ]

    with (
        mock.patch(
            "autoscrapper.progress.data_update._fetch_all_items",
            side_effect=DownloadError("MetaForge unavailable"),
        ),
        mock.patch(
            "autoscrapper.progress.data_update._fetch_all_quests",
            side_effect=DownloadError("MetaForge unavailable"),
        ),
        mock.patch(
            "autoscrapper.progress.data_update._load_raidtheory_fallback_data",
            return_value=(fallback_items, fallback_quests),
        ),
        mock.patch("autoscrapper.progress.data_update.SUPABASE_ANON_KEY", None),
    ):
        metadata = update_data_snapshot(tmp_path)

    assert metadata["itemCount"] == 1
    assert metadata["questCount"] == 1
    assert metadata["source"] == "https://metaforge.app/arc-raiders/api"
    assert metadata["dataSources"]["items"]["provider"] == "raidtheory-fallback"
    assert metadata["dataSources"]["quests"]["provider"] == "raidtheory-fallback"
    assert metadata["dataSources"]["items"]["primary"]["error"] == "MetaForge unavailable"
    assert metadata["dataSources"]["items"]["fallback"]["repository"] == (
        "https://github.com/fgrzesiak/arcraiders-data"
    )
    assert metadata["dataSources"]["quests"]["primary"]["error"] == "MetaForge unavailable"
