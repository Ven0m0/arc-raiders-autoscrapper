# AI Tuning Validation Guide

## Table of Contents

- [Overview](#overview)
- [Workflows](#workflows)
- [Examples](#examples)

---

## Overview

The **ai-tuning** skill covers both optimization and validation of AI agent configuration files. Its validation workflow ensures configs are syntactically correct, follow best practices, and remain optimized for LLM triggering and performance. It leverages two core utilities:

- **claudelint**: A deep-validation tool specifically designed for the Claude Code ecosystem. It handles `CLAUDE.md`, skill structures, hooks, and MCP configurations with high precision.
- **agnix**: A broad-spectrum linter supporting multiple agent platforms including Cursor, Copilot, Kiro, Cline, and Gemini. It features a library of 342 rules to enforce consistency across diverse agentic environments.

Using these tools helps prevent common issues such as non-triggering skills due to naming violations or inefficient context usage in `CLAUDE.md` files.

---

## Workflows

### 1. Initializing and Validating a Claude Code Project

Use `claudelint` for projects primarily targeting Claude Code.

1.  **Installation**:

    **Recommended (uv tool)**

    Install the `claudelint` CLI as a uv tool:

    ```bash
    uv tool install claudelint
    ```

    **Alternative (Node-based CLI)**

    If you prefer a Node-based global CLI, you can install the `claude-code-lint` package, which exposes the same `claudelint` commands used below:

    ```bash
    npm install -g claude-code-lint
    # or
    bun install -g claude-code-lint
    ```

2.  **Initialization**:
    ```bash
    claudelint init
    ```
    This creates `.claudelintrc.json` and `.claudelintignore` in your root.
3.  **Full Validation**:
    ```bash
    claudelint check-all
    ```
4.  **Auto-fix Issues**:
    ```bash
    claudelint check-all --fix
    ```

### 2. Multi-Platform Agent Validation

Use `agnix` for cross-tool compatibility or non-Claude environments.

1.  **Installation**:
    ```bash
    bun install -g agnix
    ```
2.  **Basic Linting**:
    ```bash
    agnix .
    ```
3.  **Targeted Linting (e.g., Kiro)**:
    ```bash
    agnix --target kiro .
    ```
4.  **Safe Auto-fixing**:
    ```bash
    agnix --fix-safe .
    ```

---

## Examples

### Example 1: Invalid SKILL.md (agnix)

**Input (`skills/my-skill/SKILL.md`):**

```markdown
---
name: MySpecialSkill
description: I help with coding.
---

# MySpecialSkill
```

**Execution:**

```bash
agnix skills/my-skill/SKILL.md
```

**Output:**

```text
✖ [AS-001] name 'MySpecialSkill' must be lowercase-kebab (e.g., 'my-special-skill')
✖ [AS-003] description must be in third-person (e.g., 'Helps with coding' instead of 'I help...')
⚠ [AS-005] description is too short (current: 19 chars, recommended: 30+)
```

### Example 2: Invalid Hook Configuration (claudelint)

> Note: This example targets Claude Code’s standalone `hooks.json` schema (as used in generic Claude Code projects), not this repository’s `hooks/hooks.json` file. The main difference is the file format/schema (for example, top-level `version` plus arrays of `{ "type": "command", "bash": "..." }`), not the hook event names themselves.

**Input (`hooks.json`):**

```json
{
  "hooks": {
    "InvalidEvent": {
      "type": "bash",
      "bash": "./non-existent.sh"
    }
  }
}
```

**Execution:**

```bash
claudelint validate-hooks
```

**Output:**

```text
hooks.json:
  2:5   error  'InvalidEvent' is not a valid hook event. Supported: sessionStart, sessionEnd, preToolUse, postToolUse
  3:12  error  script path './non-existent.sh' does not exist
```

### Example 3: CLAUDE.md Optimization (claudelint)

**Command:**

```bash
claudelint optimize-cc-md --dry-run
```

**Output:**

```text
[claudelint] Suggestion: The section 'Old Instructions' is rarely triggered and takes 400 tokens.
[claudelint] Suggestion: Move '@path/to/large_file.md' to a dedicated skill to improve context window efficiency.
```
