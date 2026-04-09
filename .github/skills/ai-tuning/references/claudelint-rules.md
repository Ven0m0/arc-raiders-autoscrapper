# claudelint Rules & Config

## .claudelintrc.json

```json
{
  "extends": "claudelint:recommended",
  "rules": {
    "claude-md-size": "warn",
    "skill-body-too-long": "error"
  },
  "overrides": [
    {
      "files": [".claude/skills/**/SKILL.md"],
      "rules": { "claude-md-size": "off" }
    }
  ],
  "ignorePatterns": ["**/*.generated.*"],
  "output": { "format": "stylish" }
}
```

Presets: `claudelint:recommended` (default), `claudelint:strict`, `claudelint:all`

Severity: `"off"` | `"warn"` | `"error"`

## Rule Categories

| Category    | CLI command                |
| ----------- | -------------------------- |
| CLAUDE.md   | `validate-cc-md`           |
| Skills      | `validate-skills --path .` |
| Settings    | `validate-settings`        |
| Hooks       | `validate-hooks`           |
| MCP servers | `validate-mcp`             |
| Plugins     | `validate-plugin`          |

Browse all: `claudelint list-rules`

## Inline Disables

```html
<!-- claudelint-disable claude-md-size -->
...large content...
<!-- claudelint-enable claude-md-size -->
```

## Claude Code Plugin

```text
/plugin marketplace add pdugan20/claudelint
/plugin install claudelint@pdugan20-plugins
```

Then use `/validate-all`, `/validate-skills`, `/optimize-cc-md`, etc.

## Programmatic API

```js
import { lint } from "claude-code-lint";
const results = await lint({ paths: ["."], fix: false });
```

Full API: https://claudelint.com/api/overview
Custom rules: https://claudelint.com/development/custom-rules
