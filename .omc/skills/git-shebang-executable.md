---
name: git-shebang-executable
description: Fix pre-commit check-shebang-scripts-are-executable blocking commits for new shell scripts
triggers:
  - "has a shebang but is not marked executable"
  - "check-shebang-scripts-are-executable"
  - "shebang not executable"
  - "pre-commit shebang"
---

# Shell Script Shebang Executable Bit

## The Insight

On Windows/WSL filesystems, new `.sh` files created by tools or agents don't get the executable bit set automatically. Pre-commit's `check-shebang-scripts-are-executable` hook catches this and blocks the commit.

## Why This Matters

A normal `git add <file>` on WSL/Windows doesn't capture the filesystem executable bit because the NTFS mount ignores POSIX permissions. The bit must be set explicitly in git's index.

## Recognition Pattern

Pre-commit output:

```text
check that scripts with shebangs are executable — Failed
  <file>.sh has a shebang but is not marked executable!
```

## The Approach

Use git's built-in chmod flag to set the executable bit in the index directly — no need to chmod on the filesystem:

```bash
git add --chmod=+x <file>.sh
```

Then re-stage any other changed files and retry the commit. This is idempotent and safe to run even if the file is already staged.
