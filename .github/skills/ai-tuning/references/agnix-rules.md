# agnix Rules Reference

## Rule Sets by Tool

```toon
rulesets[9]{prefix,tool,count,key_files}:
  AS-* / CC-SK-*,Agent Skills,31,SKILL.md
  CC-*,Claude Code,53,CLAUDE.md + hooks + settings + agents + plugins
  COP-*,GitHub Copilot,6,.github/copilot-instructions.md
  CUR-*,Cursor,16,.cursor/rules/*.mdc + .cursorrules + hooks.json
  KIRO-* / KR-*,Kiro,51,.kiro/steering + skills + agents + hooks + mcp
  MCP-*,MCP servers,12,*.mcp.json
  AGM-* / XP-*,AGENTS.md,13,AGENTS.md + AGENTS.local.md
  CLN-*,Cline,4,.clinerules
  GM-*,Gemini CLI,9,GEMINI.md + .gemini/settings.json

```

## Critical SKILL.md Rules (AS-\*)

- Name: lowercase letters and hyphens only, e.g. `code-review` not `Review-Code`
- Description: max 1024 chars, non-empty, third-person
- Required frontmatter: `name`, `description`
- Wrong name/description → skill invokes at 0%

## Fix Confidence Levels

`--fix` = HIGH + MEDIUM | `--fix-safe` = HIGH only | `--fix-unsafe` = all including LOW

## agnix.config.json

```json
{
  "rules": {
    "AS-001": "error",
    "CC-001": "warn",
    "COP-001": "off"
  },
  "ignore": ["**/node_modules/**", "**/.git/**"],
  "target": "claude-code"
}
```

## MCP Server

agnix ships an MCP server (`agnix-mcp`) for editor/agent integration.

## Playground

Paste any config → instant diagnostics: https://agent-sh.github.io/agnix/playground

## Full Rules Docs

https://agent-sh.github.io/agnix/docs/rules
