#!/usr/bin/env python3
"""
Type Coverage Checker - Measures TypeScript/Python type coverage.
Identifies untyped functions, any usage, and type safety issues.
"""

import os
import sys
import re
import argparse
from pathlib import Path
from typing import Optional
from itertools import chain

from utils import fix_windows_console_encoding

# Pre-compiled regex patterns for performance
RE_TS_ANY = re.compile(r":\s*any\b")
RE_TS_UNTYPED_FUNC = re.compile(r"function\s+\w+\s*\([^)]*\)\s*{")
RE_TS_UNTYPED_ARROW = re.compile(r"=\s*\([^:)]*\)\s*=>")
RE_TS_TYPED_FUNC = re.compile(r"function\s+\w+\s*\([^)]*\)\s*:\s*\w+")
RE_TS_TYPED_ARROW = re.compile(r":\s*\([^)]*\)\s*=>\s*\w+")

RE_PY_ANY = re.compile(r"(?::\s*|->\s*)Any\b")
RE_PY_TYPED_FUNC_PARAMS = re.compile(r"def\s+\w+\s*\([^)]*:[^)]+\)")
RE_PY_TYPED_FUNC_RETURN = re.compile(r"def\s+\w+\s*\([^)]*\)\s*->")
RE_PY_ALL_FUNC = re.compile(r"def\s+\w+\s*\(")

EXCLUDE_DIRS = {"venv", ".venv", "__pycache__", ".git", "node_modules"}

# Fix Windows console encoding for Unicode output
fix_windows_console_encoding()


def find_project_files(project_path: Path) -> tuple[list[Path], list[Path]]:
    """Find all TypeScript and Python files in a single pass."""
    ts_files = []
    py_files = []
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            if file.endswith((".ts", ".tsx")) and not file.endswith(".d.ts"):
                ts_files.append(Path(root) / file)
            elif file.endswith(".py"):
                py_files.append(Path(root) / file)
    return ts_files, py_files


def _analyze_typescript_file(file_path: Path, stats: dict) -> None:
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        # Count 'any' usage
        stats["any_count"] += len(RE_TS_ANY.findall(content))

        # Find unique functions without return types by start position
        untyped_indices = {
            m.start()
            for m in chain(
                RE_TS_UNTYPED_FUNC.finditer(content),
                RE_TS_UNTYPED_ARROW.finditer(content),
            )
        }
        untyped_count = len(untyped_indices)
        stats["untyped_functions"] += untyped_count

        # Count unique typed functions by start position
        typed_indices = {
            m.start()
            for m in chain(
                RE_TS_TYPED_FUNC.finditer(content),
                RE_TS_TYPED_ARROW.finditer(content),
            )
        }
        typed_count = len(typed_indices)
        stats["total_functions"] += typed_count + untyped_count
    except OSError:
        pass


def _format_typescript_results(stats: dict, file_count: int) -> tuple[list[str], list[str]]:
    passed = []
    issues = []

    # Analyze results
    if stats["any_count"] == 0:
        passed.append("[OK] No 'any' types found")
    elif stats["any_count"] <= 5:
        issues.append(f"[!] {stats['any_count']} 'any' types found (acceptable)")
    else:
        issues.append(f"[X] {stats['any_count']} 'any' types found (too many)")

    if stats["total_functions"] > 0:
        typed_ratio = (stats["total_functions"] - stats["untyped_functions"]) / stats["total_functions"] * 100
        if typed_ratio >= 80:
            passed.append(f"[OK] Type coverage: {typed_ratio:.0f}%")
        elif typed_ratio >= 50:
            issues.append(f"[!] Type coverage: {typed_ratio:.0f}% (improve)")
        else:
            issues.append(f"[X] Type coverage: {typed_ratio:.0f}% (too low)")

    passed.append(f"[OK] Analyzed {file_count} TypeScript files")
    return passed, issues


def check_typescript_coverage(
    project_path: Path,
    max_files: Optional[int] = 30,
    files: Optional[list[Path]] = None,
) -> dict:
    """Check TypeScript type coverage."""
    stats = {"any_count": 0, "untyped_functions": 0, "total_functions": 0}

    if files is not None:
        ts_files = files
    else:
        ts_files, _ = find_project_files(project_path)

    if not ts_files:
        return {
            "type": "typescript",
            "files": 0,
            "passed": [],
            "issues": ["[!] No TypeScript files found"],
            "stats": stats,
        }

    for file_path in ts_files[:max_files] if max_files is not None else ts_files:
        _analyze_typescript_file(file_path, stats)

    passed, issues = _format_typescript_results(stats, len(ts_files))

    return {
        "type": "typescript",
        "files": len(ts_files),
        "passed": passed,
        "issues": issues,
        "stats": stats,
    }


def analyze_python_file(content: str) -> dict[str, int]:
    """Collect type coverage stats for a single Python file."""
    typed_indices = {
        match.start()
        for match in chain(
            RE_PY_TYPED_FUNC_PARAMS.finditer(content),
            RE_PY_TYPED_FUNC_RETURN.finditer(content),
        )
    }
    all_indices = {match.start() for match in RE_PY_ALL_FUNC.finditer(content)}

    return {
        "any_count": len(RE_PY_ANY.findall(content)),
        "typed_functions": len(typed_indices),
        "untyped_functions": len(all_indices - typed_indices),
    }


def check_python_coverage(
    project_path: Path,
    max_files: Optional[int] = 30,
    files: Optional[list[Path]] = None,
) -> dict:
    """Check Python type hints coverage."""
    issues = []
    passed = []
    stats = {"untyped_functions": 0, "typed_functions": 0, "any_count": 0}

    if files is not None:
        py_files = files
    else:
        _, py_files = find_project_files(project_path)

    if not py_files:
        return {
            "type": "python",
            "files": 0,
            "passed": [],
            "issues": ["[!] No Python files found"],
            "stats": stats,
        }

    for file_path in py_files[:max_files] if max_files is not None else py_files:
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            file_stats = analyze_python_file(content)
            stats["any_count"] += file_stats["any_count"]
            stats["typed_functions"] += file_stats["typed_functions"]
            stats["untyped_functions"] += file_stats["untyped_functions"]
        except OSError:
            continue

    total = stats["typed_functions"] + stats["untyped_functions"]

    if total > 0:
        typed_ratio = stats["typed_functions"] / total * 100
        if typed_ratio >= 70:
            passed.append(f"[OK] Type hints coverage: {typed_ratio:.0f}%")
        elif typed_ratio >= 40:
            issues.append(f"[!] Type hints coverage: {typed_ratio:.0f}%")
        else:
            issues.append(f"[X] Type hints coverage: {typed_ratio:.0f}% (add type hints)")

    if stats["any_count"] == 0:
        passed.append("[OK] No 'Any' types found")
    elif stats["any_count"] <= 3:
        issues.append(f"[!] {stats['any_count']} 'Any' types found")
    else:
        issues.append(f"[X] {stats['any_count']} 'Any' types found")

    passed.append(f"[OK] Analyzed {len(py_files)} Python files")

    return {
        "type": "python",
        "files": len(py_files),
        "passed": passed,
        "issues": issues,
        "stats": stats,
    }


def main():
    parser = argparse.ArgumentParser(description="Type Coverage Checker")
    parser.add_argument("target", nargs="?", default=".", help="Target directory to check")
    parser.add_argument(
        "--max-files",
        type=int,
        default=30,
        help="Maximum number of files to check per language (default: 30, set to 0 for unlimited)",
    )

    args = parser.parse_args()

    project_path = Path(args.target)
    max_files = None if args.max_files == 0 else args.max_files

    print("\n" + "=" * 60)
    print("  TYPE COVERAGE CHECKER")
    print("=" * 60 + "\n")

    results = []

    # Pre-discover files for both languages in a single pass
    ts_files, py_files = find_project_files(project_path)

    # Check TypeScript
    ts_result = check_typescript_coverage(project_path, max_files, files=ts_files)
    if ts_result["files"] > 0:
        results.append(ts_result)

    # Check Python
    py_result = check_python_coverage(project_path, max_files, files=py_files)
    if py_result["files"] > 0:
        results.append(py_result)

    if not results:
        print("[!] No TypeScript or Python files found.")
        sys.exit(0)

    # Print results
    critical_issues = 0
    for result in results:
        print(f"\n[{result['type'].upper()}]")
        print("-" * 40)
        for item in result["passed"]:
            print(f"  {item}")
        for item in result["issues"]:
            print(f"  {item}")
            if item.startswith("[X]"):
                critical_issues += 1

    print("\n" + "=" * 60)
    if critical_issues == 0:
        print("[OK] TYPE COVERAGE: ACCEPTABLE")
        sys.exit(0)
    else:
        print(f"[X] TYPE COVERAGE: {critical_issues} critical issues")
        sys.exit(1)


if __name__ == "__main__":
    main()
