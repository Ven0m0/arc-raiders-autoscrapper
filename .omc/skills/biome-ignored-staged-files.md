---
name: biome-ignored-staged-files
description: Fix biome pre-commit hook exiting 1 when all staged files are in biome's ignore list
triggers:
  - "no files were processed"
  - "biome check failed"
  - "biome exit code 1"
  - "pre-commit biome error"
  - "staged json ignored biome"
---

# Biome "No Files Processed" Pre-commit Failure

## The Insight

When pre-commit passes staged files to biome and ALL of them are in biome's `files.includes` exclude list (e.g. `!**/progress/data`), biome exits with code 1 and prints "No files were processed in the specified paths." The files aren't errors — they're intentionally ignored — but biome treats an empty workload as failure.

## Why This Matters

This silently blocks every commit that touches generated/excluded JSON files even though those files are correctly excluded by design. The error message is misleading: it looks like a config problem but is actually a benign mismatch between pre-commit's file filtering and biome's own ignore rules.

## Recognition Pattern

- Pre-commit output: `biome check — Failed` + `× No files were processed`
- The staged files listed under "These paths were provided but ignored:" are all in `biome.json`'s exclude patterns
- Happens specifically when the ONLY staged files matching `\.(?:[cm]?[jt]sx?|jsonc?)$` are excluded by biome config

## The Approach

Add `--no-errors-on-unmatched` to the biome hook entry. This tells biome to exit 0 when all provided paths are ignored rather than treating it as an error.

## Example

In `.pre-commit-config.yaml`, change:

```yaml
entry: biome check --write
```

to:

```yaml
entry: biome check --write --no-errors-on-unmatched
```

Then re-stage `.pre-commit-config.yaml` and retry the commit.
