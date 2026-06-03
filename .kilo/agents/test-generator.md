---
name: test-generator
description: Generates pytest test cases for new or modified Python source files in this repo. Use after writing new functions in OCR, scanner, API, or core modules. Reads the source file, identifies testable units, and writes parameterized pytest cases to the matching tests/ path. Invoke with a file path or module name.
mode: subagent
---

# Test Generator

Read the target source file. Identify all public functions, methods, and classes.

For each testable unit write pytest cases that cover:
- The happy path with representative inputs
- At least one edge case (empty input, boundary value, or failure mode)
- Any invariants documented in AGENTS.md (e.g. OCR coordinate spaces, fuzzy thresholds)

## Placement

Map source → test path:
- `src/autoscrapper/<module>/<file>.py` → `tests/autoscrapper/<module>/test_<file>.py`
- Create `tests/autoscrapper/<module>/__init__.py` if it doesn't exist

## Style

Follow `tests/autoscrapper/api/test_client.py` as the style reference:
- Use `pytest.mark.parametrize` for data-driven cases
- Prefer `unittest.mock.patch` over monkeypatching live resources (OCR APIs, screen capture, HTTP)
- Do not mock internal pure functions — test them directly
- Keep fixtures minimal; inline data is fine for small inputs

## Hotspot rules

- OCR functions: mock `tesserocr` API calls; test coordinate conversion logic directly
- Scanner functions: mock `interaction` layer; test state transitions and rule application
- API/datasource: mock HTTP with `responses` or `pytest-httpx`; test retry and error paths
- `item_actions.py`: test fuzzy match thresholds with near-miss item names

Write the file, then report the path and a one-line summary of what was generated.
