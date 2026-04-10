import pytest
import orjson
from pathlib import Path
from autoscrapper.progress.data_loader import _read_json

def test_read_json_valid(tmp_path: Path):
    file_path = tmp_path / "valid.json"
    data = {"key": "value"}
    file_path.write_bytes(orjson.dumps(data))

    result = _read_json(file_path)
    assert result == data

def test_read_json_invalid(tmp_path: Path):
    file_path = tmp_path / "invalid.json"
    file_path.write_bytes(b"{invalid json")

    with pytest.raises(orjson.JSONDecodeError):
        _read_json(file_path)

def test_read_json_not_found(tmp_path: Path):
    file_path = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        _read_json(file_path)
