from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import blake2b
from pathlib import Path
from typing import Literal

import cv2
import numpy as np

from ..core.item_actions import clean_ocr_text

REPO_ROOT = Path(__file__).resolve().parents[3]
OCR_ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "ocr"
CAPTURED_CORPUS_DIR = OCR_ARTIFACTS_DIR / "skip_unlisted"
CAPTURED_IMAGES_DIR = CAPTURED_CORPUS_DIR / "images"
CAPTURED_MANIFEST_PATH = CAPTURED_CORPUS_DIR / "samples.jsonl"
FIXED_FAILURE_CORPUS_PATH = OCR_ARTIFACTS_DIR / "failure_corpus.jsonl"
REPLAY_REPORTS_DIR = OCR_ARTIFACTS_DIR / "replay_reports"
BENCHMARK_REPORTS_DIR = OCR_ARTIFACTS_DIR / "benchmark_reports"


@dataclass(frozen=True)
class OcrFailureSample:
    sample_id: str
    captured_at: str
    outcome: str
    source: Literal["infobox", "context_menu"]
    raw_text: str
    cleaned_text: str
    chosen_name: str
    matched_name: str | None
    expected_name: str | None = None
    image_path: str | None = None


@dataclass(frozen=True)
class CorpusPaths:
    manifest_path: Path
    images_dir: Path


def default_capture_paths() -> CorpusPaths:
    return CorpusPaths(
        manifest_path=CAPTURED_MANIFEST_PATH,
        images_dir=CAPTURED_IMAGES_DIR,
    )


def _iso_now() -> str:
    return (
        datetime.now(UTC)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _sample_id(
    *,
    raw_text: str,
    chosen_name: str,
    source: Literal["infobox", "context_menu"],
    image: np.ndarray | None,
) -> str:
    payload = "\n".join((source, raw_text, chosen_name)).encode("utf-8")
    digest = blake2b(payload, digest_size=8)
    if image is not None and image.size > 0:
        digest.update(np.ascontiguousarray(image).tobytes())
    return digest.hexdigest()


def _coerce_sample(entry: object) -> OcrFailureSample | None:
    if not isinstance(entry, dict):
        return None

    sample_id = entry.get("sample_id")
    captured_at = entry.get("captured_at")
    outcome = entry.get("outcome")
    source = entry.get("source")
    raw_text = entry.get("raw_text")
    cleaned_text = entry.get("cleaned_text")
    chosen_name = entry.get("chosen_name")
    matched_name = entry.get("matched_name")
    expected_name = entry.get("expected_name")
    image_path = entry.get("image_path")

    if not all(
        isinstance(value, str) and value
        for value in (
            sample_id,
            captured_at,
            outcome,
            source,
            raw_text,
            cleaned_text,
            chosen_name,
        )
    ):
        return None
    if source not in {"infobox", "context_menu"}:
        return None
    if matched_name is not None and not isinstance(matched_name, str):
        return None
    if expected_name is not None and not isinstance(expected_name, str):
        return None
    if image_path is not None and not isinstance(image_path, str):
        return None

    return OcrFailureSample(
        sample_id=sample_id,
        captured_at=captured_at,
        outcome=outcome,
        source=source,
        raw_text=raw_text,
        cleaned_text=cleaned_text,
        chosen_name=chosen_name,
        matched_name=matched_name,
        expected_name=expected_name,
        image_path=image_path,
    )


def capture_skip_unlisted_sample(
    *,
    raw_text: str,
    chosen_name: str,
    matched_name: str | None,
    source_image: np.ndarray | None,
    from_context_menu: bool,
    paths: CorpusPaths | None = None,
) -> OcrFailureSample | None:
    cleaned_text = clean_ocr_text(raw_text)
    used_chosen_name_fallback = False
    if not cleaned_text:
        cleaned_text = clean_ocr_text(chosen_name)
        used_chosen_name_fallback = bool(cleaned_text)
    if not cleaned_text:
        return None

    source: Literal["infobox", "context_menu"] = (
        "context_menu" if from_context_menu else "infobox"
    )
    corpus_paths = paths or default_capture_paths()
    sample_id = _sample_id(
        raw_text=raw_text,
        chosen_name=chosen_name,
        source=source,
        image=source_image,
    )

    image_path: str | None = None
    if source_image is not None and source_image.size > 0:
        corpus_paths.images_dir.mkdir(parents=True, exist_ok=True)
        image_name = f"{sample_id}.png"
        absolute_image_path = corpus_paths.images_dir / image_name
        if cv2.imwrite(str(absolute_image_path), source_image):
            image_path = absolute_image_path.relative_to(REPO_ROOT).as_posix()

    sample_raw_text = raw_text.strip()
    # Preserve the original OCR string when available; otherwise store the
    # cleaned fallback so replay/benchmark tooling still has a usable corpus row.
    sample = OcrFailureSample(
        sample_id=sample_id,
        captured_at=_iso_now(),
        outcome="SKIP_UNLISTED",
        source=source,
        raw_text=sample_raw_text if sample_raw_text else cleaned_text,
        cleaned_text=cleaned_text,
        chosen_name=chosen_name,
        matched_name=matched_name,
        image_path=image_path,
    )

    corpus_paths.manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with corpus_paths.manifest_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(sample), ensure_ascii=False) + "\n")
    if used_chosen_name_fallback:
        print(
            "[ocr_corpus] captured sample without raw OCR text; used chosen name fallback",
            flush=True,
        )

    return sample


def load_failure_corpus(path: Path) -> list[OcrFailureSample]:
    if not path.exists():
        return []

    samples: list[OcrFailureSample] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            payload = line.strip()
            if not payload:
                continue
            sample = _coerce_sample(json.loads(payload))
            if sample is not None:
                samples.append(sample)
    return samples


def resolve_image_path(sample: OcrFailureSample, *, manifest_path: Path) -> Path | None:
    if not sample.image_path:
        return None
    image_path = Path(sample.image_path)
    if image_path.is_absolute():
        return image_path

    repo_candidate = REPO_ROOT / image_path
    if repo_candidate.exists():
        return repo_candidate
    return manifest_path.parent / image_path


def write_report(directory: Path, prefix: str, payload: object) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    path = directory / f"{prefix}_{stamp}.json"
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return path
