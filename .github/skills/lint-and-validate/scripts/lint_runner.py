#!/usr/bin/env python3
"""
Lint Runner - Unified linting and type checking
Runs appropriate linters based on project type.

Usage:
    python lint_runner.py <project_path>

Supports:
    - Node.js: npm run lint, npx tsc --noEmit
    - Python: ruff check, mypy
"""

import subprocess
import concurrent.futures
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from utils import fix_windows_console_encoding

# Fix Windows console encoding
# Swallow any errors here to preserve previous behavior where reconfigure() failures were non-fatal.
try:
    fix_windows_console_encoding()
except Exception:
    # If console encoding cannot be fixed, continue with default behavior.
    pass


def detect_node_project(project_path: Path, result: dict[str, Any]) -> None:
    """Detect Node.js project and available linters."""
    package_json = project_path / "package.json"
    if package_json.exists():
        result["type"] = "node"
        try:
            pkg = json.loads(package_json.read_text(encoding="utf-8"))
            scripts = pkg.get("scripts", {})
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

            # Check for lint script
            if "lint" in scripts:
                result["linters"].append(
                    {"name": "npm lint", "cmd": ["npm", "run", "lint"]}
                )
            elif "eslint" in deps:
                result["linters"].append(
                    {"name": "eslint", "cmd": ["npx", "eslint", "."]}
                )

            # Check for TypeScript
            if "typescript" in deps or (project_path / "tsconfig.json").exists():
                result["linters"].append(
                    {"name": "tsc", "cmd": ["npx", "tsc", "--noEmit"]}
                )

        except IOError, json.JSONDecodeError:
            pass


def detect_python_project(project_path: Path, result: dict[str, Any]) -> None:
    """Detect Python project and available linters."""
    if (project_path / "pyproject.toml").exists() or (
        project_path / "requirements.txt"
    ).exists():
        result["type"] = "python"

        # Check for ruff
        result["linters"].append({"name": "ruff", "cmd": ["ruff", "check", "."]})

        # Check for mypy
        if (project_path / "mypy.ini").exists() or (
            project_path / "pyproject.toml"
        ).exists():
            result["linters"].append({"name": "mypy", "cmd": ["mypy", "."]})


def detect_project_type(project_path: Path) -> dict[str, Any]:
    """Detect project type and available linters."""
    result = {"type": "unknown", "linters": []}

    detect_node_project(project_path, result)

    detect_python_project(project_path, result)

    return result


def run_linter(linter: dict[str, Any], cwd: Path) -> dict[str, Any]:
    """Run a single linter and return results."""
    result = {"name": linter["name"], "passed": False, "output": "", "error": ""}

    try:
        proc = subprocess.run(
            linter["cmd"],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )

        result["output"] = proc.stdout[:2000] if proc.stdout else ""
        result["error"] = proc.stderr[:500] if proc.stderr else ""
        result["passed"] = proc.returncode == 0

    except FileNotFoundError:
        result["error"] = f"Command not found: {linter['cmd'][0]}"
    except subprocess.TimeoutExpired:
        result["error"] = "Timeout after 120s"
    except Exception as e:
        result["error"] = str(e)

    return result


def run_linters_parallel(
    linters: list[dict[str, Any]],
    project_path: Path,
) -> tuple[list[dict[str, Any]], bool]:
    """Run configured linters in parallel and collect results."""
    results = []
    all_passed = True

    print("\nRunning linters in parallel...")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_linter = {
            executor.submit(run_linter, linter, project_path): linter
            for linter in linters
        }

        for future in concurrent.futures.as_completed(future_to_linter):
            linter = future_to_linter[future]
            try:
                result = future.result()
                results.append(result)

                print(f"\nFinished: {linter['name']}")
                if result["passed"]:
                    print(f"  [PASS] {linter['name']}")
                else:
                    print(f"  [FAIL] {linter['name']}")
                    if result["error"]:
                        print(f"  Error: {result['error'][:200]}")
                    all_passed = False
            except Exception as exc:
                print(f"\nFinished: {linter['name']}")
                print(f"  [FAIL] {linter['name']} generated an exception: {exc}")
                results.append(
                    {
                        "name": linter["name"],
                        "passed": False,
                        "output": "",
                        "error": str(exc),
                    }
                )
                all_passed = False

    return results, all_passed


def main():
    try:
        project_path = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    except (OSError, RuntimeError) as e:
        print(f"Error: Invalid path: {e}")
        sys.exit(1)

    if not project_path.exists():
        print(f"Error: Path does not exist: {project_path}")
        sys.exit(1)

    if not project_path.is_dir():
        print(f"Error: Path is not a directory: {project_path}")
        sys.exit(1)

    print(f"\n{'=' * 60}")
    print("[LINT RUNNER] Unified Linting")
    print(f"{'=' * 60}")
    print(f"Project: {project_path}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Detect project type
    project_info = detect_project_type(project_path)
    print(f"Type: {project_info['type']}")
    print(f"Linters: {len(project_info['linters'])}")
    print("-" * 60)

    if not project_info["linters"]:
        print("No linters found for this project type.")
        output = {
            "script": "lint_runner",
            "project": str(project_path),
            "type": project_info["type"],
            "checks": [],
            "passed": True,
            "message": "No linters configured",
        }
        print(json.dumps(output, indent=2))
        sys.exit(0)

    # Run each linter in parallel
    results, all_passed = run_linters_parallel(project_info["linters"], project_path)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for r in results:
        icon = "[PASS]" if r["passed"] else "[FAIL]"
        print(f"{icon} {r['name']}")

    output = {
        "script": "lint_runner",
        "project": str(project_path),
        "type": project_info["type"],
        "checks": results,
        "passed": all_passed,
    }

    print("\n" + json.dumps(output, indent=2))

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
