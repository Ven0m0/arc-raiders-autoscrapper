---
name: linting-llm-configs
description: Validates AI guidance files with claudelint and agnix. Use when checking SKILL.md, CLAUDE.md, prompts, hooks, or MCP config for structural issues.
---

# Linting LLM Configs

Validation-only companion to `ai-tuning`. Keep remediation focused on lint findings; use `ai-tuning` when the task is about condensing, deduplication, or instruction design.

## Usage

Use this skill after editing AI config files or when CI reports config-lint failures.

## When to use

| Situation                                         | Validator    |
| ------------------------------------------------- | ------------ |
| Claude Code structure, hooks, MCP, `CLAUDE.md`    | `claudelint` |
| `SKILL.md`, `AGENTS.md`, cross-tool config checks | `agnix`      |
| Mixed repo or release gate                        | Run both     |

## Workflow

1. Identify the changed files and choose `claudelint`, `agnix`, or both.
2. Run the narrowest command that covers the edited surface.
3. Fix structure, naming, or duplication issues in the source files.
4. Re-run the same validators until they pass.
5. If the content is verbose but lint-clean, switch to `ai-tuning` for condensation work.

## Commands

| Scope                               | Command                                     |
| ----------------------------------- | ------------------------------------------- |
| Full Claude Code lint               | `claudelint check-all`                      |
| Strict repo validation (matches CI) | `uv tool run "claudelint@0.3.3" --strict .` |
| Validate skill files                | `claudelint validate-skills --path .`       |
| Validate hooks                      | `claudelint validate-hooks`                 |
| Validate MCP config                 | `claudelint validate-mcp`                   |
| Cross-tool lint                     | `agnix .`                                   |
| Safe autofix pass                   | `agnix --fix-safe .`                        |
| Claude Code target                  | `agnix --target claude-code .`              |
| Cursor target                       | `agnix --target cursor .`                   |

## Guardrails

- Keep `SKILL.md` files short, trigger-driven, and repo-relevant.
- Remove duplicated rules instead of copying the same guidance into multiple skills.
- Preserve valid frontmatter and kebab-case skill names.
- Do not invent local commands; prefer repo or tool-native commands already in use.

## Examples

- "Lint this SKILL.md after edits" -> run `agnix .` plus targeted `claudelint validate-skills --path .`
- "Why did config lint CI fail?" -> reproduce with `uv tool run "claudelint@0.3.3" --strict .`
- "Make these skill files shorter" -> switch to `ai-tuning` after validators are green

## References

- [Validation guide](references/guide.md)
