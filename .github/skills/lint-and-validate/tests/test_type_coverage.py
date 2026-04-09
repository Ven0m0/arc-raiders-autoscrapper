import importlib
import sys
from pathlib import Path

# Add scripts directory to path to import the module
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.append(str(scripts_dir))

type_coverage = importlib.import_module("type_coverage")
check_typescript_coverage = type_coverage.check_typescript_coverage
check_python_coverage = type_coverage.check_python_coverage


def test_check_typescript_coverage_no_files(tmp_path):
    """Test when no TypeScript files are present."""
    result = check_typescript_coverage(tmp_path)
    assert result["files"] == 0
    assert "[!] No TypeScript files found" in result["issues"]
    assert result["stats"]["any_count"] == 0


def test_check_typescript_coverage_any_detection(tmp_path):
    """Test detection of ': any' with various formats."""
    ts_file = tmp_path / "test.ts"
    ts_file.write_text(
        """
        let a: any;
        const b:any = 1;
        function foo(x:  any): any { return x; }
        let c:any;
        // False positives to avoid (no colon)
        let company = "any";
        let many = true;

        // Note: Current regex-based detection is simple and might match
        // these if they have a colon, even in comments/strings.
        // This test documents the current behavior.
    """,
        encoding="utf-8",
    )

    result = check_typescript_coverage(tmp_path)

    # Expected matches for ': any':
    # 1. let a: any; -> ': any'
    # 2. const b:any = 1; -> ':any'
    # 3. function foo(x:  any) -> ':  any'
    # 4. ): any { -> ': any'
    # 5. let c:any; -> ':any'

    assert result["stats"]["any_count"] == 5
    assert result["files"] == 1


def test_check_typescript_coverage_function_stats(tmp_path):
    """Test detection of typed and untyped functions."""
    ts_file = tmp_path / "test.ts"
    ts_file.write_text(
        """
        function typedFunc(a: number): number { return a; }
        function untypedFunc(a: number) { return a; }
        const untypedArrow = (x) => x;
    """,
        encoding="utf-8",
    )

    result = check_typescript_coverage(tmp_path)

    # typedFunc -> matches typed (1)
    # untypedFunc -> matches untyped (1)
    # untypedArrow -> matches untyped (2)

    assert result["stats"]["untyped_functions"] == 2
    assert result["stats"]["total_functions"] == 3


def test_check_typescript_coverage_multiple_files(tmp_path):
    """Test handling of multiple files."""
    (tmp_path / "file1.ts").write_text("let a: any;")
    (tmp_path / "file2.tsx").write_text("let b: any;")
    (tmp_path / "not_ts.js").write_text("let c: any;")

    result = check_typescript_coverage(tmp_path)
    assert result["files"] == 2
    assert result["stats"]["any_count"] == 2


def test_check_python_coverage_no_files(tmp_path):
    """Test when no Python files are present."""
    result = check_python_coverage(tmp_path)
    assert result["files"] == 0
    assert "[!] No Python files found" in result["issues"]
    assert result["stats"]["any_count"] == 0


def test_check_python_coverage_any_detection(tmp_path):
    """Test detection of 'Any' with various formats."""
    py_file = tmp_path / "test.py"
    py_file.write_text(
        """
        from typing import Any
        def foo(x: Any) -> Any:
            return x
        a: Any = 1
        # False positives
        def anybody(): pass
        any_var = True
    """,
        encoding="utf-8",
    )

    result = check_python_coverage(tmp_path)

    # Expected matches for Any usage (regex handles both ': Any' and '-> Any'):
    # 1. Parameter annotation: x: Any
    # 2. Return annotation: -> Any
    # 3. Variable annotation: a: Any

    assert result["stats"]["any_count"] == 3
    assert result["files"] == 1


def test_check_python_coverage_function_stats(tmp_path):
    """Test detection of typed and untyped functions."""
    py_file = tmp_path / "test.py"
    py_file.write_text(
        """
        def untyped_func(x):
            pass

        def params_typed(x: int):
            pass

        def return_typed(x) -> int:
            return 1

        def fully_typed(x: int) -> int:
            return x
    """,
        encoding="utf-8",
    )

    result = check_python_coverage(tmp_path)

    # Function typing summary:
    # - untyped_func: no type annotations (untyped)
    # - params_typed: typed parameters, untyped return
    # - return_typed: untyped parameters, typed return
    # - fully_typed: both parameters and return typed
    #
    # Expected aggregate stats:
    # - typed_functions: functions with any type annotations (params or return) -> 3
    # - untyped_functions: functions without any type annotations -> 1

    assert result["stats"]["typed_functions"] == 3
    assert result["stats"]["untyped_functions"] == 1


def test_check_python_coverage_multiple_files(tmp_path):
    """Test handling of multiple files."""
    (tmp_path / "file1.py").write_text("def foo(x: int): pass")
    (tmp_path / "file2.py").write_text("def bar(x: int): pass")
    (tmp_path / "not_py.txt").write_text("def baz(x: int): pass")

    result = check_python_coverage(tmp_path)
    assert result["files"] == 2
    assert result["stats"]["typed_functions"] == 2


def test_analyze_python_file():
    """Test analyze_python_file directly."""
    content = """
    from typing import Any

    def untyped_func(x):
        pass

    def typed_params(x: int):
        pass

    def typed_return(x) -> int:
        return 1

    def fully_typed(x: int) -> int:
        return x

    def any_typed(x: Any) -> Any:
        return x
    """

    stats = type_coverage.analyze_python_file(content)

    assert stats["untyped_functions"] == 1
    assert stats["typed_functions"] == 4
    assert stats["any_count"] == 2
