# Custom Tools

All tools are registered in `.kilo/kilo.json` and loaded via `.kilo/plugins/custom-tools.ts`.

## Available Tools

| Tool | Source | When to use |
|------|--------|-------------|
| `json_repair` | `tools/json_repair.ts` | Fix malformed JSON from LLM streams; modes: `repair`, `extract`, `extract_all`, `strip` |
| `hl_edit` | `tools/hashline_edit.ts` | Edit files — quick mode via `start_line`/`end_line`/`new_code`, or concurrent-safe mode via `LINE#HASH\|` anchors |
| `hl_read` | `tools/hashline_rg.ts` | Read file with `LINE#HASH\|` annotations |
| `hl_grep` | `tools/hashline_rg.ts` | Grep returning `LINE#HASH\|` annotated matches |
| `sg` | `tools/ast_grep.ts` | AST-aware structural code search via `sg` CLI (25 languages) |
| `sgr` | `tools/ast_grep.ts` | AST-aware in-place code rewrite; dry-run by default |
| `cshield_toggle` | `plugins/context-shield.ts` | Toggle output compaction on/off |
| `gitingest` | `plugins/gitingest.ts` | Fetch full GitHub repo via gitingest.com |

## Tool Routing (follow these rules)

**`sg` / `sgr` before `grep`** — When searching for code structure (function definitions, call expressions, class declarations, import statements, variable patterns), ALWAYS use `sg` instead of `grep`. Reserve `grep` for plain-text, comment, or string-literal searches where AST structure does not matter.

**`json_repair` for broken JSON** — When `read` returns a JSON file that fails to parse, or you receive a malformed JSON string, call `json_repair` with the file path or string BEFORE attempting any manual edits. Use `mode=extract` to pull the first JSON block out of mixed prose/markdown output.

## Usage Notes

**hl_edit quick mode** — pass `start_line`, `end_line`, `new_code` for fast line-range edits without needing hash anchors. Use `start_line > end_line` to insert without deleting.

**hl_edit hash mode** — use `edits[]` with `LINE#HASH|` anchors when multiple agents may edit the same file concurrently; prevents stale-read collisions.

**hl_read / hl_grep output** — output contains `LINE#HASH|content` annotations. Do NOT summarize or truncate these results — the hash anchors are consumed verbatim by `hl_edit`. Context-shield is configured to skip compaction for these tools.

**sg / sgr** — patterns use meta-variables: `$VAR` (single node), `$$$` (multiple nodes). Example: `console.log($MSG)`. Use `sgr` with `dryRun=false` to apply rewrites.

**json_repair** — no subprocess, no temp files; repair runs inline via `IncrementalJsonRepair`. Safe to call on large inputs. Also used by the `json-healer` plugin for automatic response healing.

## Plugin Architecture

| Plugin | Purpose |
|--------|---------|
| `context-shield` | Compacts large tool outputs; applies slim descriptions to all built-in and custom tools; expands line-range `oldString` for native `edit`; suppresses verbose edit/read confirmation messages. **Also absorbs all openslimedit functionality** — there is no separate openslimedit plugin. |
| `json-healer` | Transparent response healing: auto-repairs malformed JSON in string-valued tool arguments and string tool outputs before/after each tool call. Falls through silently if repair fails or result isn't valid JSON. |
| `custom-tools` | Registers `json_repair`, `hl_edit`, `hl_read`, `hl_grep`, `sg`, `sgr`. |

### SKIP_COMPACTION_FOR (context-shield)

Context-shield never compacts output from: `write`, `apply_patch`, `multiedit`, `lsp`, `hl_read`, `hl_grep`, `hl_edit`, `json_repair`, `sg`, `sgr`, `cshield_toggle`.

## Naming

Custom tool names use `snake_case` to avoid collisions with built-ins (`edit`, `grep`, `read`, `write`).
