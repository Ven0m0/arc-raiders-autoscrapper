#!/usr/bin/env python3
"""Capture an OCR fixture from an ocr_debug image for use in regression tests.

Usage:
    uv run python scripts/capture_ocr_fixture.py <image_path> <expected_item_name>

Arguments:
    image_path          Path to the source image (e.g. ocr_debug/infobox_0.png)
    expected_item_name  The correct item name this image should produce (e.g. "Rusty Gear")

Output:
    tests/fixtures/ocr/<slug>.png   — copy of the source image
    tests/fixtures/ocr/<slug>.json  — sidecar with expected_name, source, captured_at

Example:
    uv run python scripts/capture_ocr_fixture.py ocr_debug/infobox_0.png "Rusty Gear"
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "ocr"


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Capture an OCR fixture from an ocr_debug image.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("image_path", type=Path, help="Source image path")
    parser.add_argument("expected_item_name", help="Correct item name this image should produce")
    args = parser.parse_args(argv)

    src: Path = args.image_path
    if not src.is_absolute():
        src = Path.cwd() / src
    if not src.exists():
        print(f"error: image not found: {src}", file=sys.stderr)
        return 1
    if src.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
        print(f"error: unsupported image format: {src.suffix}", file=sys.stderr)
        return 1

    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    slug = _slug(args.expected_item_name)
    dest_image = FIXTURES_DIR / f"{slug}.png"
    dest_sidecar = FIXTURES_DIR / f"{slug}.json"

    if dest_image.exists() or dest_sidecar.exists():
        print(f"fixture already exists for '{args.expected_item_name}' (slug: {slug})")
        print(f"  image:   {dest_image.relative_to(REPO_ROOT)}")
        print(f"  sidecar: {dest_sidecar.relative_to(REPO_ROOT)}")
        overwrite = input("Overwrite? [y/N] ").strip().lower()
        if overwrite != "y":
            print("aborted.")
            return 0

    shutil.copy2(src, dest_image)

    sidecar = {
        "expected_name": args.expected_item_name,
        "source": "ocr_debug",
        "captured_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_image": src.name,
    }
    dest_sidecar.write_text(json.dumps(sidecar, indent=2) + "\n", encoding="utf-8")

    print(f"captured fixture for '{args.expected_item_name}'")
    print(f"  image:   {dest_image.relative_to(REPO_ROOT)}")
    print(f"  sidecar: {dest_sidecar.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
