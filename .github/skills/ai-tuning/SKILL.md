---
name: ai-tuning
description: Optimize and validate AI assistant configurations (CLAUDE.md, copilot-instructions.md, AGENTS.md, MCP, hooks, settings). Use when asked to tune guidance, deduplicate overlapping rules, or lint agent config files with claudelint or agnix.
allowed-tools: "Read, Write, Edit, Glob, Grep"
---

# AI Tuning

Optimize and validate AI assistant configurations. Standards: `instructions/ai-tuning.instructions.md`

<overview>
Use this skill for project-wide AI guidance files (`copilot-instructions.md`, `AGENTS.md`, `CLAUDE.md`, prompts, MCP config) and for agent-config linting with claudelint or agnix.
</overview>

<instructions>

## Triggers

| User says                     | Target                              |
| ----------------------------- | ----------------------------------- |
| "improve CLAUDE.md"           | CLAUDE.md / AGENTS.md               |
| "better copilot instructions" | copilot-instructions.md             |
| "condense/deduplicate"        | Cross-file guidance hierarchy       |
| "tune AI"                     | All AI config files                 |
| "optimize prompts"            | Prompts, AGENTS.md, instruction set |
| "add MCP servers"             | `.vscode/mcp.json`                  |
| "lint/validate SKILL.md"      | Skills, agents, hooks, MCP, config  |

## Workflow

1. **Analyze**
   - Read foundation files: `copilot-instructions.md`, `AGENTS.md`, `CLAUDE.md`
   - Read scoped guidance: `.claude/rules/*.md`, `.github/instructions/**`, prompts, skills
   - Read tool config: `.vscode/mcp.json`, hooks/settings, related agent files

2. **Identify gaps**
   - Missing stack, commands, conventions, or constraints
   - Vague instructions instead of exact rules
   - Outdated commands/tool names
   - Cross-file duplication
   - Project-wide rules misplaced in narrow-scope files

3. **Optimize**

   <optimization_rules>
   - Dense over verbose: `Python 3.12 | ruff | pytest`
   - Examples over descriptions: short snippets or tables over generic prose
   - Tables over prose: `| Action | Command |` for build/test/lint
   - Specific over general: exact commands, exact tool names, exact paths
   - Hierarchy over flat: root guidance > topic rules > subdirectory rules
     </optimization_rules>

4. **Validate**
   - Every command must be exact and executable in the project
   - Run claudelint or agnix when available for config-heavy changes
   - Re-check that consolidated files do not lose essential context

## Validation Tools

### Which tool to use?

| File / config                        | Prefer                 | Why                                    |
| ------------------------------------ | ---------------------- | -------------------------------------- |
| `CLAUDE.md`, Claude Code skills      | `claudelint`           | Deep Claude Code validation/formatting |
| `SKILL.md`, `AGENTS.md`, Copilot/MCP | `agnix`                | Cross-tool rule coverage               |
| Mixed Claude Code repo               | `claudelint` + `agnix` | Structure + ecosystem coverage         |

### claudelint workflow

```bash
claudelint init
claudelint check-all
claudelint check-all --fix
claudelint validate-skills --path .
claudelint validate-hooks
claudelint validate-mcp
claudelint validate-settings
claudelint validate-cc-md
claudelint format --check
```

### agnix workflow

```bash
agnix .
agnix --fix .
agnix --fix-safe .
agnix --dry-run --show-fixes .
agnix --strict .
agnix --target claude-code .
```

### High-signal rules

| Area         | What to check                                                             |
| ------------ | ------------------------------------------------------------------------- |
| `SKILL.md`   | lowercase-kebab name, valid frontmatter, concise third-person description |
| `CLAUDE.md`  | valid imports, no circular references, focused size                       |
| `hooks.json` | valid event names and command entries                                     |
| MCP config   | valid transport, URL/env fields, no placeholder secrets                   |

## Condensation (CLAUDE.md / AGENTS.md Deduplication)

| Phase     | Action                                                                 |
| --------- | ---------------------------------------------------------------------- |
| Discovery | Find all overlapping AI guidance files and repeated rules              |
| Analysis  | Identify misplaced content and decide the canonical file               |
| Present   | Show duplicates, affected files, and proposed consolidation            |
| Implement | Remove duplicates, move guidance to the correct layer, keep references |

**Hierarchy**: `./CLAUDE.md` or `./AGENTS.md` (project) > topic rules > subdirectory guidance

## Install

```bash
npm install -g claude-code-lint
npx claudelint init
npm install -g agnix
```

</instructions>

<examples>

### Before optimization (verbose, vague)

```markdown
# Project Guidelines

We use Python for our backend. Please make sure to use type hints
when writing Python code. For testing, we prefer pytest. Please run
the linter before committing any code.
```

### After optimization (dense, actionable)

```markdown
# Stack

Python 3.12 | FastAPI | PostgreSQL | Redis

# Dev Commands

| Task   | Command                |
| ------ | ---------------------- |
| Lint   | `ruff check --fix .`   |
| Format | `ruff format .`        |
| Test   | `pytest -x --tb=short` |
| Types  | `mypy src/`            |

# Conventions

- Type hints on all public functions
- `result: T | None` not `Optional[T]`
- Pydantic models for API schemas
```

### Deduplication example

```text
Found duplication:
  ./CLAUDE.md line 15: "Use ruff for linting"
  ./backend/CLAUDE.md line 3: "Always run ruff before committing"
  ./.claude/rules/python.md line 8: "Lint with ruff check"

Action: Keep in ./CLAUDE.md only (project-wide rule).
Remove from backend/CLAUDE.md and .claude/rules/python.md.
```

</examples>

## References

- [Validation guide](references/guide.md)
- [claudelint rules + config](references/claudelint-rules.md)
- [agnix rules reference](references/agnix-rules.md)
