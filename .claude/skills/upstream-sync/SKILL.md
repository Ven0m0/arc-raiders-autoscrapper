---
name: upstream-sync
description: Sync local branch with upstream canonical repo using autostash merge. Resolves generated-file conflicts by accepting upstream versions.
---

# upstream-sync — Merge from Upstream

## When to use
Before starting any feature work or debt-reduction session, to ensure local branch is up to date with the canonical upstream repo.

## Remotes
- `upstream` → `https://github.com/zappybiby/ArcRaiders-AutoScrapper.git` (canonical)
- `origin` → your fork

## Steps

### 1. Check for pre-existing conflicts
```bash
git status --short
```
If any file shows `UD` (unmerged): resolve it first.
- For `.opencode/` or tooling configs deleted by us: `git rm <file>`
- For source files: inspect and resolve manually

### 2. Stash and merge
```bash
git stash
git merge upstream/main -X theirs
git stash pop
```
`-X theirs` is safe here because all conflicts in this repo are in auto-generated data files (`progress/data/`, `items_rules.default.json`) where upstream is authoritative.

> **Why not `git pull --autostash --rebase`?** The repo has many daily data-snapshot commits. Rebasing 200+ commits causes cascading conflicts in generated files. A single merge commit is cleaner.

### 3. Verify
```bash
git log --oneline -5
git status --short
```
Working tree should show only your local tooling changes, no conflict markers.

### 4. If merge conflicts appear in source files
Generated files (accept upstream):
```bash
git checkout --theirs src/autoscrapper/progress/data/<file>
git checkout --theirs src/autoscrapper/items/items_rules.default.json
git add <resolved-files>
git merge --continue
```

Source code conflicts: resolve manually, keeping whichever version is correct, then `git add` and `git merge --continue`.
