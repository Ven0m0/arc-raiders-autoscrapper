# Custom Tools

All tools are registered in `.kilo/kilo.json` and loaded via `.kilo/plugins/custom-tools.ts`.

## Available Tools

| Tool | Source | When to use |
|------|--------|-------------|
| `json_repair` | `tools/json_repair.ts` | Fix malformed JSON from LLM streams; modes: `repair`, `extract`, `extract_all`, `strip` |
| `hashline_edit` | `tools/hashline_edit.ts` | Edit files — quick mode via `start_line`/`end_line`/`new_code`, or concurrent-safe mode via `LINE#HASH\|` anchors |
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

**hashline_edit quick mode** — pass `start_line`, `end_line`, `new_code` for fast line-range edits without needing hash anchors. Use `start_line > end_line` to insert without deleting.

**hashline_edit hash mode** — use `edits[]` with `LINE#HASH|` anchors when multiple agents may edit the same file concurrently; prevents stale-read collisions.

**ast_grep** — patterns use meta-variables: `$VAR` (single node), `$$$` (multiple nodes). Example: `console.log($MSG)`.

**codemogger** — project root is auto-indexed on session start if `.codemogger/` is absent. Call `codemogger_index` to force a refresh.

## Naming

Custom tool names use `snake_case` to avoid collisions with built-ins (`edit`, `grep`, `read`, `write`).
