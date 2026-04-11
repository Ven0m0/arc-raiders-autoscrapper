import os
import importlib
import importlib

import autoscrapper.progress.data_update as data_update


def test_config_defaults():
    # Reload module to ensure we're testing with fresh state if env vars were set
    importlib.reload(data_update)
    assert data_update.METAFORGE_API_BASE == "https://metaforge.app/api/arc-raiders"
    assert data_update.SUPABASE_URL == "https://unhbvkszwhczbjxgetgk.supabase.co/rest/v1"
def test_config_env_vars(monkeypatch):
    monkeypatch.setenv("METAFORGE_API_BASE", "https://example.com/api")
    monkeypatch.setenv("METAFORGE_SUPABASE_URL", "https://supabase.example.com")

    # Reload the module to pick up the new environment variables
    importlib.reload(data_update)

    assert data_update.METAFORGE_API_BASE == "https://example.com/api"
    assert data_update.SUPABASE_URL == "https://supabase.example.com"

    # Clean up after test by reloading again without env vars
    monkeypatch.delenv("METAFORGE_API_BASE")
    monkeypatch.delenv("METAFORGE_SUPABASE_URL")
    importlib.reload(data_update)
