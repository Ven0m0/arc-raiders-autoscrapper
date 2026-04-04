from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from autoscrapper.ocr.failure_corpus import (  # noqa: E402
    CAPTURED_MANIFEST_PATH,
    REPLAY_REPORTS_DIR,
    load_failure_corpus,
    write_report,
)
from autoscrapper.ocr.inventory_vision import (  # noqa: E402
    DEFAULT_ITEM_NAME_MATCH_THRESHOLD,
    match_item_name_result,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Replay captured SKIP_UNLISTED OCR samples against candidate fuzzy thresholds."
        )
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=CAPTURED_MANIFEST_PATH,
        help="JSONL corpus to replay (default: %(default)s)",
    )
    parser.add_argument(
        "--threshold",
        dest="thresholds",
        action="append",
        type=int,
        help="Candidate threshold to evaluate; repeat to test multiple values.",
    )
    return parser


def _default_thresholds() -> list[int]:
    current = DEFAULT_ITEM_NAME_MATCH_THRESHOLD
    return [
        value
        for value in {current - 10, current - 5, current, current + 5, current + 10}
        if value > 0
    ]


def _format_expected_name_or_default(sample_expected_name: str | None) -> str:
    return sample_expected_name.strip() if sample_expected_name else "<no-match>"


def main() -> int:
    args = _build_parser().parse_args()
    manifest_path = args.manifest.resolve()
    thresholds = sorted(set(args.thresholds or _default_thresholds()))
    samples = load_failure_corpus(manifest_path)

    threshold_reports: list[dict[str, object]] = []
    passing_thresholds: list[int] = []
    for threshold in thresholds:
        sample_reports: list[dict[str, object]] = []
        correct_count = 0
        for sample in samples:
            result = match_item_name_result(sample.raw_text, threshold)
            expects_no_match = sample.expected_name is None
            is_correct = (
                expects_no_match and result.matched_name is None
            ) or result.matched_name == sample.expected_name
            if is_correct:
                correct_count += 1
            sample_reports.append(
                {
                    "sample_id": sample.sample_id,
                    "raw_text": sample.raw_text,
                    "expected": _format_expected_name_or_default(sample.expected_name),
                    "match_status": "matched"
                    if result.matched_name is not None
                    else "no_match",
                    "chosen_name": result.chosen_name,
                    "matched_name": result.matched_name,
                    "correct": is_correct,
                }
            )

        passes = correct_count == len(samples)
        if passes:
            passing_thresholds.append(threshold)
        threshold_reports.append(
            {
                "threshold": threshold,
                "passes": passes,
                "correct_count": correct_count,
                "sample_count": len(samples),
                "samples": sample_reports,
            }
        )

    selected_threshold = (
        DEFAULT_ITEM_NAME_MATCH_THRESHOLD
        if DEFAULT_ITEM_NAME_MATCH_THRESHOLD in passing_thresholds
        else (passing_thresholds[0] if passing_thresholds else None)
    )
    report = {
        "manifest_path": manifest_path.as_posix(),
        "sample_count": len(samples),
        "current_threshold": DEFAULT_ITEM_NAME_MATCH_THRESHOLD,
        "candidate_thresholds": thresholds,
        "passing_thresholds": passing_thresholds,
        "selected_threshold": selected_threshold,
        "threshold_reports": threshold_reports,
    }
    report_path = write_report(REPLAY_REPORTS_DIR, "ocr_threshold_replay", report)

    print(f"samples={len(samples)} manifest={manifest_path}")
    for threshold_report in threshold_reports:
        print(
            "threshold={threshold} passes={passes} correct={correct_count}/{sample_count}".format(
                **threshold_report
            )
        )
    print(f"report={report_path}")
    if not samples:
        print(
            "No samples found; capture live SKIP_UNLISTED data before calibrating the threshold."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
