---
name: workflow-development
description: Create, debug, and optimize GitHub Actions workflows with security best practices. Use when asked to "create workflow", "fix workflow", "add CI", or needs help with GitHub Actions.
allowed-tools: "Bash, Read, Write, Edit, Glob, Grep"
---

# Workflow Development

Create, debug, and optimize GitHub Actions workflows.

Standards: `instructions/cicd-standards.instructions.md`

<instructions>

## Workflow

Think through the requirements step-by-step:

1. **Understand the goal**: What should the workflow do? (CI, CD, scheduled task, etc.)
2. **Choose triggers**: `push`, `pull_request`, `workflow_dispatch`, `schedule`, `workflow_call`?
3. **Design jobs**: What steps are needed? Can anything run in parallel?
4. **Apply security**: Minimal permissions, pinned action versions, no exposed secrets
5. **Optimize**: Caching, concurrency controls, matrix strategies where beneficial
6. **Test**: Validate YAML syntax, verify triggers, check permissions

</instructions>

<security>

Non-negotiable security requirements:

```yaml
permissions:
  contents: read

steps:
  - uses: actions/checkout@v4 # Always pin to major version tag
```

- Pin all actions to version tags (never `@main` or `@master`)
- Set minimal `permissions:` at workflow or job level
- Use `secrets: inherit` or explicit secret passing for reusable workflows
- Never echo secrets in logs

</security>

<patterns>

## Reusable Workflow

```yaml
# Caller
jobs:
  ci:
    uses: Ven0m0/.github/.github/workflows/reusable-ci-python.yml@main
    with:
      python-version: "3.12"
    secrets: inherit

# Definition (on: workflow_call)
on:
  workflow_call:
    inputs:
      python-version:
        type: string
        default: "3.12"
```

## Caching

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/uv
    key: ${{ runner.os }}-uv-${{ hashFiles('uv.lock') }}
```

## Concurrency

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

## Matrix Strategy

```yaml
strategy:
  fail-fast: false
  matrix:
    os: [ubuntu-latest, macos-latest]
    python-version: ["3.11", "3.12"]
```

</patterns>

<debugging>

| Symptom                                  | Likely Cause            | Fix                                               |
| ---------------------------------------- | ----------------------- | ------------------------------------------------- |
| "Resource not accessible by integration" | Missing permissions     | Add to `permissions:` block                       |
| Cache never hits                         | Wrong hash path         | Check `hashFiles()` glob matches actual lock file |
| Secrets unavailable in reusable workflow | Not passed through      | Add `secrets: inherit` or pass explicitly         |
| Workflow not triggered                   | Wrong event config      | Verify `on:` triggers, check branch filters       |
| "Path does not exist"                    | Wrong working-directory | Verify path relative to repo root                 |
| Matrix job fails inconsistently          | OS-specific issue       | Add OS conditionals or separate jobs              |

</debugging>

<examples>

### Python CI workflow

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync
      - run: uv run ruff check .
      - run: uv run pytest -x
```

### Release workflow with tag trigger

```yaml
name: Release
on:
  push:
  tags: "'v*'"
permissions:
  contents: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: gh release create ${{ github.ref_name }} --generate-notes
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

</examples>
