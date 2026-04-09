---
name: code-maintenance
description: Refactoring and cleanup - improving code structure, removing dead code, eliminating duplication, or pre-merge cleanup. Use when code is hard to maintain, has dead code or debug artifacts, or needs pre-merge polishing.
allowed-tools: "Bash, Read, Write, Edit, Glob, Grep"
---

# Code Maintenance

Refactoring (structure) and cleanup (removal). Behavior preserved. Gradual evolution.

<instructions>

## Step 1: Determine Mode

| Scenario                   | Mode     | Focus                                     |
| -------------------------- | -------- | ----------------------------------------- |
| Code hard to maintain      | Refactor | Extract, simplify, apply SOLID principles |
| Dead code, debug artifacts | Cleanup  | Remove dead code, flag uncertain items    |
| Pre-merge, production prep | Cleanup  | Lint pass, verify tests, remove TODOs     |

## Step 2: Identify Candidates

Search for code smells and cleanup targets:

<code_smells>

| Smell                           | Detection                  | Fix                          |
| ------------------------------- | -------------------------- | ---------------------------- |
| Long method (>50 lines)         | Line count                 | Extract method               |
| Duplicated code                 | Search for similar blocks  | Extract shared function      |
| Dead code                       | No references, unreachable | Delete (git has history)     |
| Magic numbers                   | Literal values in logic    | Named constants              |
| Nested conditionals (>3 levels) | Indentation depth          | Guard clauses, early returns |
| God class/function              | Too many responsibilities  | Split by concern             |

</code_smells>

<cleanup_targets>

| Category        | Remove                                 | Flag (don't auto-remove) |
| --------------- | -------------------------------------- | ------------------------ |
| Dead code       | No refs, commented-out, unreachable    | Reflection/dynamic calls |
| Debug artifacts | `print()`, `console.log()`, `debugger` | Structured logging calls |
| Imports         | Unused imports                         | Wildcard imports         |
| Comments        | Obvious, outdated comments             | "Why" explanations       |

</cleanup_targets>

## Step 3: Execute

1. Present plan to user before starting (what changes, why, risk level)
2. Apply changes file-by-file, one refactoring at a time
3. Run linters after each file: `ruff check --fix`, `eslint --fix`, etc.
4. Verify: tests pass, no regressions

## Step 4: Security Check

Verify absent: hardcoded credentials, API keys, PII in test fixtures
Verify present: env vars for secrets, `.gitignore` entries for sensitive files

</instructions>

<constraints>
- **Behavior preserved**: Change how the code works, not what it does
- **Small steps**: One change, test, commit - never batch large refactors
- **Tests essential**: No refactoring without passing tests first
- **Confirm first**: Always present the plan before executing
</constraints>

<examples>

### Refactoring: Extract method

```
Before:
  def process_order(order):
      # 50 lines of validation
      # 30 lines of pricing
      # 20 lines of notification

After:
  def process_order(order):
      validate_order(order)
      total = calculate_pricing(order)
      notify_customer(order, total)
```

### Cleanup: Remove dead code

```
Search: rg "def legacy_handler" --files-with-matches
Check: rg "legacy_handler" src/ -> 0 references outside definition
Action: Delete function and its tests (git preserves history)
```

### Cleanup: Debug artifact removal

```
Search: rg "console\.log|debugger" src/ --count
Found: 12 console.log statements across 5 files
Action: Remove all, replace with structured logger where appropriate
```

</examples>
