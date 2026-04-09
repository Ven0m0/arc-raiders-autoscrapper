---
name: clean-code
description: Simplifies noisy implementations and improves maintainability during code changes. Use when refactoring, trimming duplication, or tightening readability.
---

# Clean code

Use this skill to remove unnecessary complexity around the task in front of you. Favor small, behavior-preserving cleanups over broad style rewrites.

## Usage

Reach for this skill when the work is already in scope and the code can be made clearer without redesigning the subsystem.

## When to use

| Situation                      | Apply this skill                                       |
| ------------------------------ | ------------------------------------------------------ |
| Refactoring noisy code         | Remove dead abstractions, duplication, and indirection |
| Reviewing maintainability      | Tighten names, control flow, and file boundaries       |
| Finishing a feature or bug fix | Trim opportunistic complexity in touched code only     |

## Workflow

1. Map the impact surface: callers, imports, tests, and shared interfaces.
2. Simplify only what is coupled to the task; avoid unrelated rewrites.
3. Prefer clearer names, flatter control flow, and colocated logic over extra layers.
4. Delete redundant comments, one-off helpers, and unused branches when safe.
5. Re-run the relevant validation commands before finishing.

## High-signal checks

| Keep                                      | Remove                                  |
| ----------------------------------------- | --------------------------------------- |
| Names that explain intent                 | Placeholder names and abbreviations     |
| Guard clauses and straight-line flow      | Deep nesting and branching noise        |
| Shared abstractions with multiple callers | Helpers used once with no reuse value   |
| Comments that explain non-obvious intent  | Comments that restate the code          |
| Small focused edits                       | Cleanup that changes unrelated behavior |

## Guardrails

- Preserve behavior first; cleanup is not a license to redesign the module.
- Update dependent files in the same task when signatures or shared types move.
- Prefer the repository's existing lint/test commands over inventing new checks.

## Examples

### Good cleanup targets

- Inline a helper that only wraps a single expression.
- Replace nested `if` trees with early returns.
- Rename `data`/`item`/`temp` variables to domain-specific names.
- Remove dead branches or stale debug logging in touched code.

### Out of scope

- Rewriting an entire subsystem without a product requirement.
- Introducing new patterns only because they are fashionable.
- Splitting files or creating helpers when the current file is already clear.
