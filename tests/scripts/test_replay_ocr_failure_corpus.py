from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

sys.modules.setdefault("pywinctl", MagicMock())
sys.modules.setdefault("pymonctl", MagicMock())
sys.modules.setdefault("pynput", MagicMock())
sys.modules.setdefault("pynput.keyboard", MagicMock())
sys.modules.setdefault("pynput.mouse", MagicMock())

from autoscrapper.ocr.failure_corpus import OcrFailureLabelStatus, OcrFailureSample  # noqa: E402
from autoscrapper.ocr.inventory_vision import ItemNameMatchResult  # noqa: E402

_REPLAY_SCRIPT_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "replay_ocr_failure_corpus.py"
)


def _load_replay_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("test_replay_ocr_failure_corpus_script", _REPLAY_SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sample(
    *,
    sample_id: str,
    raw_text: str,
    label_status: OcrFailureLabelStatus,
    expected_name: str | None = None,
) -> OcrFailureSample:
    return OcrFailureSample(
        schema_version=2,
        sample_id=sample_id,
        captured_at="2026-01-01T00:00:00Z",
        outcome="SKIP_UNLISTED",
        source="infobox",
        raw_text=raw_text,
        cleaned_text=raw_text,
        chosen_name=raw_text,
        matched_name=None,
        label_status=label_status,
        expected_name=expected_name,
        image_path=None,
        threshold=75,
    )


def test_authoritative_samples_exclude_pending_and_ambiguous() -> None:
    replay = _load_replay_module()
    samples = [
        _sample(sample_id="pending", raw_text="raw", label_status="pending"),
        _sample(sample_id="ambiguous", raw_text="raw", label_status="ambiguous", expected_name="Arc Alloy"),
        _sample(sample_id="match", raw_text="Arc Alloy", label_status="match", expected_name="Arc Alloy"),
        _sample(sample_id="no_match", raw_text="Unavailable", label_status="no_match"),
    ]

    authoritative = replay._authoritative_samples(samples)

    assert [sample.sample_id for sample in authoritative] == ["match", "no_match"]


def test_evaluate_threshold_records_expected_status_and_correctness(monkeypatch) -> None:
    replay = _load_replay_module()
    samples = [
        _sample(sample_id="match", raw_text="Arc Alloy", label_status="match", expected_name="Arc Alloy"),
        _sample(sample_id="no_match", raw_text="Unavailable", label_status="no_match"),
    ]

    def _fake_match(raw_text: str, threshold: int) -> ItemNameMatchResult:
        if raw_text == "Arc Alloy":
            matched_name = "Arc Alloy" if threshold <= 75 else None
            chosen_name = matched_name or raw_text
            return ItemNameMatchResult(
                cleaned_text=raw_text,
                chosen_name=chosen_name,
                matched_name=matched_name,
                threshold=threshold,
            )
        return ItemNameMatchResult(
            cleaned_text=raw_text,
            chosen_name=raw_text,
            matched_name=None,
            threshold=threshold,
        )

    monkeypatch.setattr(replay, "match_item_name_result", _fake_match)

    report = replay._evaluate_threshold(samples, 75)

    assert report["passes"] is True
    assert report["correct_count"] == 2
    assert report["sample_count"] == 2
    assert report["samples"] == [
        {
            "sample_id": "match",
            "source": "infobox",
            "raw_text": "Arc Alloy",
            "cleaned_text": "Arc Alloy",
            "label_status": "match",
            "expected_status": "match",
            "expected": "Arc Alloy",
            "match_status": "matched",
            "chosen_name": "Arc Alloy",
            "matched_name": "Arc Alloy",
            "correct": True,
        },
        {
            "sample_id": "no_match",
            "source": "infobox",
            "raw_text": "Unavailable",
            "cleaned_text": "Unavailable",
            "label_status": "no_match",
            "expected_status": "no_match",
            "expected": "<no-match>",
            "match_status": "no_match",
            "chosen_name": "Unavailable",
            "matched_name": None,
            "correct": True,
        },
    ]


def test_select_threshold_prefers_current_default() -> None:
    replay = _load_replay_module()

    assert replay._select_threshold([65, 75, 80]) == 75
    assert replay._select_threshold([65, 70, 80]) == 65
    assert replay._select_threshold([]) is None
