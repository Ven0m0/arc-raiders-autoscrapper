## Custom Tools and Plugins Usage

This document registers custom Kilo tools and plugins located in the repository's `.kilo/plugins/` and `.kilo/tools/` directories.

## Overview

| Directory | Purpose |
|-----------|---------|
| `.kilo/plugins/` | OpenCode plugins — export full Plugin objects with tools and hooks |
| `.kilo/tools/` | Standalone tool modules — individual tool definitions (require a plugin wrapper) |
| `.kilo/rules/custom-tools.md` | This file — instructs the agent on when and how to use these tools |

---

## Loading Custom Plugins and Tools

To make these tools and plugins available to Kilo, they must be registered in `.kilo/kilo.json`.

### Loading OpenCode Plugins

The `.kilo/plugins/` directory contains OpenCode plugin modules written in TypeScript. Bun can execute `.ts` files directly, so they can be referenced via relative paths in the `plugin` array.

**Update `plugin` array in `.kilo/kilo.json`:**

```json
{
  "plugin": [
    // ... existing plugins ...,
    "./plugins/context-shield",
    "./plugins/gitingest",
    "./plugins/codemogger",
    "./plugins/openslimedit",
    "./plugins/trim-tool-name"
  ]
}
```

Reference paths are relative to the `.kilo/` directory. OpenCode/Bun resolves `.ts` extensions automatically.

### Loading Standalone Tools

The `.kilo/tools/` directory contains standalone tool modules that export tool definitions (either as `export default tool({...})` or named exports). They must be wrapped in a plugin to be loaded.

**Option A — Create a single aggregator plugin** (recommended)

Create `.kilo/plugins/custom-tools.ts`:

```typescript
import type { Plugin } from '@opencode-ai/plugin';
import fastedit from '../tools/fastedit';
import jsonRepair from '../tools/json_repair';
import hashlineEdit from '../tools/hashline_edit';
import { read as hashline_read, grep as hashline_grep } from '../tools/hashline_rg';
import interactiveBash from '../tools/interactive_bash';
import astGrep from '../tools/ast_grep';

const CustomToolsPlugin: Plugin = async () => ({
  tool: {
    fastedit,
    json_repair: jsonRepair,
    hashline_edit: hashlineEdit,
    hashline_read,
    hashline_grep,
    interactive_bash: interactiveBash,
    ast_grep: astGrep,
  },
});

export default CustomToolsPlugin;
```

Then add `"./plugins/custom-tools"` to the `plugin` array in `.kilo/kilo.json`.

**Option B — Convert each tool to its own plugin wrapper** (more granular)

Create individual wrapper files in `.kilo/plugins/` that re-export each tool as a plugin, e.g. `.kilo/plugins/fastedit.ts`:

```typescript
import { tool } from '@opencode-ai/plugin';
import fastedit from '../tools/fastedit';

export default {
  tool: { fastedit }
};
```

Repeat for each tool.

---

## Available Custom Tools and Plugins

### OpenCode Plugins (`.kilo/plugins/`)

| Plugin | Tools Provided | Description |
|--------|---------------|-------------|
| `context-shield.ts` | `cshield_toggle`, `cshield_stats` | Compacts large tool outputs to reduce token usage; configurable per-worktree |
| `gitingest.ts` | `gitingest` | Fetch full repository contents from GitHub via gitingest.com — summary + tree + code |
| `codemogger.ts` | `codemogger_index`, `codemogger_search`, `codemogger_status` | Local code indexing + semantic search using codemogger (tree-sitter + embeddings) |
| `openslimedit.ts` | (no tools) | "Slim" edit tool descriptions & output compaction for OpenCode's default edit tools |
| `trim-tool-name.js` | (no tools) | Before-hook that trims whitespace from tool names (helps with LLM formatting errors) |

### Standalone Tools (`.kilo/tools/`) — Status: Need Wrapper

| Tool | Module | Description |
|------|--------|-------------|
| `fastedit` | `fastedit.ts` | Fast line-range file replacement/deletion/insertion by line numbers |
| `json_repair` | `json_repair.ts` | Repair malformed/incomplete JSON from LLM streams; supports multiple modes |
| `hashline_edit` | `hashline_edit.ts` | Hash-anchored, lock-free multi-file editing with LINE#HASH| references |
| `hashline_read` | `hashline_rg.ts` | Read file with LINE#HASH| annotations |
| `hashline_grep` | `hashline_rg.ts` | Grep-like search returning LINE#HASH| annotated matches |
| `interactive_bash` | `interactive_bash.ts` | Run interactive tmux subcommands (TUI apps: vim, htop, etc.) |
| `ast_grep` | `ast_grep.ts` | AST-based code search using the `sg` CLI (pattern matching across languages) |

> **Note:** `hashline_utils.ts` is a shared utility module — not a tool.

---

## Usage Guidelines

### When to Use Hashline Tools

The hashline tools (`hashline_edit`, `hashline_read`, `hashline_grep`) are designed for **collaborative editing with concurrent agents**. They use content-addressed line hashes to detect edit conflicts.

**Use when:**
- Multiple agents might edit the same file concurrently
- You need to ensure edits remain valid even if the file changes between read and edit
- Working with teammate agents on the same codebase

**Avoid for simple single-agent edits** — use `fastedit` or the standard `edit` tool instead.

### When to Use `fastedit`

`fastedit` is a simpler, faster line-range editor. Use for straightforward text replacements, insertions, or deletions by line number.

### When to Use `json_repair`

Use `json_repair` when an LLM returns incomplete or malformed JSON (common in streaming responses). Modes:
- `repair` — fix structural JSON issues
- `extract` — extract first JSON block from prose/markdown/thinking tags
- `extract_all` — extract all JSON blocks as array
- `strip` — strip LLM wrapper tags then repair

### When to Use `interactive_bash`

Use `interactive_bash` for commands that require a pseudo-TTY (e.g., running `vim`, `htop`, `top`, or any interactive tool). Do not use for regular non-interactive shell commands — use `bash` instead.

### When to Use `ast_grep`

Use `ast_grep` for language-aware pattern matching across code. Supports JS/TS, Python, Rust, Go, and many other languages via the `sg` CLI. More precise than text-based grep for code structures.

### When to Use `cshield_toggle` / `cshield_stats`

`context_shield` automatically compacts large tool outputs. Use `cshield_toggle` to temporarily disable/enable compaction for a task. Use `cshield_stats` to review token savings.

### When to Use `gitingest`

Use `gitingest` to fetch an entire GitHub repository's contents with one call — ideal for quickly reviewing external projects without cloning.

### When to Use `codemogger`

Use `codemogger_index` to build a local code index, then `codemogger_search` for semantic or keyword search. Supports hybrid search (vector + FTS) across multiple languages. The project root auto-indexes on session start if `.codemogger/` is absent.

---

## Practical Examples

```text
# Compact output for a large grep result
cshield_toggle

# Get full repo from GitHub
gitingest url="https://github.com/owner/repo"

# Semantic search for "error handling pattern"
codemogger_search query="error handling pattern" mode="semantic"

# Repair broken JSON from an LLM output file
json_repair input="/path/to/broken.json" mode="repair" pretty=true

# Replace lines 10-20 in a file
fastedit file_path="/path/to/file.ts" start_line=10 end_line=20 new_code="new content"

# Edit a file using hash anchors (concurrent-safe)
hashline_edit file_path="src/foo.ts" edits=["10#AB|old line", ">>> 12#CD|updated"]

# Search for a pattern with hash-annotated matches
hashline_grep pattern="TODO" path="src/" glob="*.ts"
```

---

## Tool Naming Convention

All standalone tools from `.kilo/tools/` use underscore-separated names (`fastedit`, `json_repair`, `hashline_edit`) to avoid collisions with built-in OpenCode tools (`edit`, `grep`, `read`, `write`).

---

## Maintenance

When updating tools in `.kilo/tools/` or plugins in `.kilo/plugins/`, ensure they're re-exported by an aggregator plugin or individually registered in `.kilo/kilo.json`.

After adding new tools:
1. Build/type-check (if using TypeScript, run `bun build` or similar)
2. Test the tool works via `kilo` CLI
3. Update this rule file with the new tool's documentation
