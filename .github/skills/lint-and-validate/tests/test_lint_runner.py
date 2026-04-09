import json
import subprocess
import sys
from pathlib import Path
from scripts.lint_runner import (
    detect_node_project,
    detect_python_project,
    detect_project_type,
)


def test_detect_node_project_with_lint_script(tmp_path: Path):
    result = {"type": "unknown", "linters": []}
    package_json = tmp_path / "package.json"
    package_json.write_text(
        json.dumps(
            {"scripts": {"lint": "eslint ."}, "dependencies": {"typescript": "^4.0.0"}}
        )
    )

    detect_node_project(tmp_path, result)

    assert result["type"] == "node"
    assert len(result["linters"]) == 2
    assert result["linters"][0]["name"] == "npm lint"
    assert result["linters"][1]["name"] == "tsc"


def test_detect_node_project_with_eslint_dep(tmp_path: Path):
    result = {"type": "unknown", "linters": []}
    package_json = tmp_path / "package.json"
    package_json.write_text(json.dumps({"devDependencies": {"eslint": "^8.0.0"}}))

    detect_node_project(tmp_path, result)

    assert result["type"] == "node"
    assert len(result["linters"]) == 1
    assert result["linters"][0]["name"] == "eslint"


def test_detect_node_project_with_tsconfig(tmp_path: Path):
    result = {"type": "unknown", "linters": []}
    package_json = tmp_path / "package.json"
    package_json.write_text(json.dumps({}))
    (tmp_path / "tsconfig.json").touch()

    detect_node_project(tmp_path, result)

    assert result["type"] == "node"
    assert len(result["linters"]) == 1
    assert result["linters"][0]["name"] == "tsc"


def test_detect_node_project_invalid_json(tmp_path: Path):
    result = {"type": "unknown", "linters": []}
    package_json = tmp_path / "package.json"
    package_json.write_text("{ invalid json }")

    detect_node_project(tmp_path, result)

    assert result["type"] == "node"
    assert len(result["linters"]) == 0


def test_detect_python_project_pyproject(tmp_path: Path):
    result = {"type": "unknown", "linters": []}
    (tmp_path / "pyproject.toml").touch()

    detect_python_project(tmp_path, result)

    assert result["type"] == "python"
    assert len(result["linters"]) == 2
    assert result["linters"][0]["name"] == "ruff"
    assert result["linters"][1]["name"] == "mypy"


def test_detect_python_project_requirements(tmp_path: Path):
    result = {"type": "unknown", "linters": []}
    (tmp_path / "requirements.txt").touch()

    detect_python_project(tmp_path, result)

    assert result["type"] == "python"
    assert len(result["linters"]) == 1
    assert result["linters"][0]["name"] == "ruff"


def test_detect_project_type_node(tmp_path: Path):
    package_json = tmp_path / "package.json"
    package_json.write_text(
        json.dumps(
            {"scripts": {"lint": "eslint ."}, "dependencies": {"typescript": "^4.0.0"}}
        )
    )

    result = detect_project_type(tmp_path)

    assert result["type"] == "node"
    assert len(result["linters"]) == 2


def test_detect_project_type_python(tmp_path: Path):
    (tmp_path / "pyproject.toml").touch()

    result = detect_project_type(tmp_path)

    assert result["type"] == "python"
    assert len(result["linters"]) == 2


def test_detect_project_type_unknown(tmp_path: Path):
    result = detect_project_type(tmp_path)

    assert result["type"] == "unknown"
    assert len(result["linters"]) == 0


def test_main_with_nonexistent_path():
    result = subprocess.run(
        [sys.executable, "skills/lint-and-validate/scripts/lint_runner.py", "/nonexistent/path"],
        capture_output=True,
        text=True
    )
    assert result.returncode != 0
    assert "Error: Path does not exist" in result.stdout


def test_main_with_file_instead_of_dir(tmp_path: Path):
    test_file = tmp_path / "test.txt"
    test_file.touch()

    result = subprocess.run(
        [sys.executable, "skills/lint-and-validate/scripts/lint_runner.py", str(test_file)],
        capture_output=True,
        text=True
    )
    assert result.returncode != 0
    assert "Error: Path is not a directory" in result.stdout
