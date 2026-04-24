# Custom Tools

All tools are registered in `.kilo/kilo.json` and loaded via `.kilo/plugins/custom-tools.ts`.

## Available Tools

| Tool | Source | When to use |
|------|--------|-------------|
| `json_repair` | `tools/json_repair.ts` | Fix malformed JSON from LLM streams; modes: `repair`, `extract`, `extract_all`, `strip` |
| `hashline_edit` | `tools/hashline_edit.ts` | Edit files — quick mode via `start_line`/`end_line`/`new_code`, or concurrent-safe mode via `LINE#HASH\|` anchors |
| `hashline_read` | `tools/hashline_rg.ts` | Read file with `LINE#HASH\|` annotations |
| `hashline_grep` | `tools/hashline_rg.ts` | Grep returning `LINE#HASH\|` annotated matches |
| `ast_grep` | `tools/ast_grep.ts` | AST-aware structural code search via `sg` CLI (25 languages) |
| `cshield_toggle` | `plugins/context-shield.ts` | Toggle output compaction on/off |
| `gitingest` | `plugins/gitingest.ts` | Fetch full GitHub repo via gitingest.com |
| `codemogger_index` | `plugins/codemogger.ts` | Build/update local semantic code index |
| `codemogger_search` | `plugins/codemogger.ts` | Semantic/keyword/hybrid search over indexed code |

## Usage Notes

**hashline_edit quick mode** — pass `start_line`, `end_line`, `new_code` for fast line-range edits without needing hash anchors. Use `start_line > end_line` to insert without deleting.

**hashline_edit hash mode** — use `edits[]` with `LINE#HASH|` anchors when multiple agents may edit the same file concurrently; prevents stale-read collisions.

**hashline_read / hashline_grep output** — output contains `LINE#HASH|content` annotations. Do NOT summarize or truncate these results — the hash anchors are consumed verbatim by `hashline_edit`. Context-shield is configured to skip compaction for these tools.

**ast_grep** — patterns use meta-variables: `$VAR` (single node), `$$$` (multiple nodes). Example: `console.log($MSG)`.

**codemogger** — project root is auto-indexed on every session start (only changed files re-processed). Call `codemogger_index` to force a full refresh. Use `codemogger_search` for semantic or keyword lookup before reaching for `grep`.

**json_repair** — no subprocess, no temp files; repair runs inline via `IncrementalJsonRepair`. Safe to call on large inputs. Also used by the `json-healer` plugin for automatic response healing.

## Plugin Architecture

| Plugin | Purpose |
|--------|---------|
| `context-shield` | Compacts large tool outputs; applies slim descriptions to all built-in and custom tools; expands line-range `oldString` for native `edit`; suppresses verbose edit/read confirmation messages. **Also absorbs all openslimedit functionality** — there is no separate openslimedit plugin. |
| `json-healer` | Transparent response healing: auto-repairs malformed JSON in string-valued tool arguments and string tool outputs before/after each tool call. Falls through silently if repair fails or result isn't valid JSON. |
| `codemogger` | Semantic code search; indexes worktree in background on session start. Re-indexes on `file.edited` events. |
| `custom-tools` | Registers `json_repair`, `hashline_edit`, `hashline_read`, `hashline_grep`, `ast_grep`. |

### SKIP_COMPACTION_FOR (context-shield)

Context-shield never compacts output from: `write`, `apply_patch`, `multiedit`, `lsp`, `hashline_read`, `hashline_grep`, `hashline_edit`, `json_repair`, `ast_grep`, `codemogger_index`, `codemogger_search`, `cshield_toggle`.

## Naming

Custom tool names use `snake_case` to avoid collisions with built-ins (`edit`, `grep`, `read`, `write`).
