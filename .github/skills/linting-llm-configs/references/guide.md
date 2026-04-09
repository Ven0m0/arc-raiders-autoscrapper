# Linting LLM Configs Guide

## Table of Contents

- [Overview](#overview)
- [Workflows](#workflows)
- [Examples](#examples)

---

## Overview

This **linting-llm-configs** reference covers both optimization and validation of AI agent configuration files. Its validation workflow ensures configs are syntactically correct, follow best practices, and remain optimized for LLM triggering and performance. It leverages two core utilities:

- **claudelint**: A deep-validation tool specifically designed for the Claude Code ecosystem. It handles `CLAUDE.md`, skill structures, hooks, and MCP configurations with high precision.
- **agnix**: A broad-spectrum linter supporting multiple agent platforms including Cursor, Copilot, Kiro, Cline, and Gemini. It features a library of hundreds of rules to enforce consistency across diverse agentic environments.

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
