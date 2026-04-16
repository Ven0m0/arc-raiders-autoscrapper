---
name: verify
description: Run the full validation suite (lint + types + tests) before marking any code change done.
---

Run these three commands in sequence from the project root. Stop and report on the first failure.

```bash
python3 -m uv run ruff check src/ tests/
python3 -m uv run basedpyright src/
python3 -m uv run pytest
```

Report: pass/fail per step, any errors inline. Do not claim the change is done until all three pass.
