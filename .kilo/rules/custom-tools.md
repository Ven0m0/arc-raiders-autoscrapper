# Custom Tools

All tools are registered in `.kilo/kilo.json` and loaded via `.kilo/plugins/custom-tools.ts`.

## Available Tools

| Tool | Source | When to use |
|------|--------|-------------|
| `fastedit` | `tools/fastedit.ts` | Simple line-range replacement/insertion by line number |
| `json_repair` | `tools/json_repair.ts` | Fix malformed JSON from LLM streams; modes: `repair`, `extract`, `extract_all`, `strip` |
| `hashline_edit` | `tools/hashline_edit.ts` | Concurrent-safe multi-file edits using `LINE#HASH\|` anchors |
| `hashline_read` | `tools/hashline_rg.ts` | Read file with `LINE#HASH\|` annotations |
| `hashline_grep` | `tools/hashline_rg.ts` | Grep returning `LINE#HASH\|` annotated matches |
| `ast_grep` | `tools/ast_grep.ts` | AST-aware code search/replace via `sg` CLI (25 languages) |
| `cshield_toggle` | `plugins/context-shield.ts` | Toggle output compaction on/off |
| `cshield_stats` | `plugins/context-shield.ts` | Show token savings stats |
| `gitingest` | `plugins/gitingest.ts` | Fetch full GitHub repo via gitingest.com |
| `codemogger_index` | `plugins/codemogger.ts` | Build/update local semantic code index |
| `codemogger_search` | `plugins/codemogger.ts` | Semantic/keyword/hybrid search over indexed code |
| `codemogger_status` | `plugins/codemogger.ts` | List indexed codebases |

## Usage Notes

**hashline tools** — use only when multiple agents may edit the same file concurrently. For single-agent edits prefer `fastedit` or `edit`.

**ast_grep** — patterns use meta-variables: `$VAR` (single node), `$$$` (multiple nodes). Example: `console.log($MSG)`.

**codemogger** — project root is auto-indexed on session start if `.codemogger/` is absent. Call `codemogger_index` to force a refresh.

## Naming

Custom tool names use `snake_case` to avoid collisions with built-ins (`edit`, `grep`, `read`, `write`).
