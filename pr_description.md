🧪 Add missing error path test for `load_item_actions`

🎯 **What:** This PR addresses a testing gap in `src/autoscrapper/core/item_actions.py:77` by explicitly verifying that `load_item_actions` returns an empty dictionary `{}` when the items rules file does not exist (`FileNotFoundError`).

📊 **Coverage:** Adds coverage for the missing file scenario. We use `unittest.mock.patch` to simulate `pathlib.Path.read_bytes` raising a `FileNotFoundError`, effectively testing the `try/except` block and error handling logic directly.

✨ **Result:** Increased testing confidence around the error-handling fallback logic, preventing future regressions in configuration file processing.
