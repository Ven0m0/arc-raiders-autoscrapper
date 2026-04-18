"""One-off helper to migrate `biome.json` from `files.ignores` to `files.ignore`.

Usage:
    python fix_biome.py [path/to/biome.json]

This is intended for manual maintainer use and does not run on import.
"""

import json
import sys
from pathlib import Path


def migrate_biome_config(config_path: Path) -> None:
    with config_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    files = data.get("files")
    if isinstance(files, dict) and "ignores" in files:
        files["ignore"] = files.pop("ignores")

    with config_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def main() -> None:
    config_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("biome.json")
    migrate_biome_config(config_path)


if __name__ == "__main__":
    main()
