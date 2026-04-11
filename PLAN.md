# Plan: Merge Remote Updates + Fix Qlty Technical Debt

**Date:** 2026-04-11  
**Scope:** Pull upstream/remote changes with autostash, then resolve all issues reported by `qlty check -a`, `qlty metrics -a`, and `qlty smells -a`.

---

## Requirements Summary

1. Sync local branch with remote without losing uncommitted work (autostash pull).
2. Resolve every actionable issue from the three qlty commands:
   - `qlty check -a` — linting, security, type errors (ruff, bandit, mypy, trufflehog, zizmor, actionlint, biome, yamllint)
   - `qlty metrics -a` — complexity and maintainability metrics (flag files over threshold)
   - `qlty smells -a` — code smells reported as comments

---

## Acceptance Criteria

- [ ] `git pull --autostash` completes with no merge conflicts left unresolved.
- [ ] `qlty check -a` exits 0 (or all remaining issues are explicitly suppressed with a comment justification).
- [ ] `qlty metrics -a` produces no files above the project's complexity threshold (or all exceptions documented).
- [ ] `qlty smells -a` produces no actionable smells (or each smell is triaged: fixed or suppressed with rationale).
- [ ] `python3 -m uv run ruff check src/ tests/` exits 0.
- [ ] `python3 -m uv run pytest` passes.

---

## Implementation Steps

### Phase 1 — Sync with Remote

1. **Pull with autostash** from the upstream canonical repo:
   ```bash
   git pull --autostash upstream main
   ```
   - `--autostash` stashes local changes before pull and pops them after.
   - If upstream main diverges from origin main, also pull origin:
     ```bash
     git pull --autostash origin main
     ```

2. **Resolve any merge conflicts** introduced by the pull.
   - Focus areas: `src/autoscrapper/`, `pyproject.toml`, `.qlty/qlty.toml`.
   - After conflict resolution: `git add <file>` then `git merge --continue`.

3. **Verify stash was re-applied cleanly** (`git status` should show the same working-tree state as before pull). If the autostash pop left conflicts, resolve them manually.

### Phase 2 — Baseline Qlty Run

4. **Run all three qlty commands** and capture output:
   ```bash
   qlty check -a 2>&1 | tee /tmp/qlty-check.txt
   qlty metrics -a 2>&1 | tee /tmp/qlty-metrics.txt
   qlty smells -a 2>&1 | tee /tmp/qlty-smells.txt
   ```

5. **Triage the output** into three buckets:
   - **Fix** — genuine bugs, security issues, type errors, hard complexity violations
   - **Suppress** — false positives or intentional patterns (add inline `# noqa`, `# type: ignore`, or qlty-specific ignore with a comment)
   - **Defer** — out-of-scope refactors (document in a follow-up issue, not suppressed silently)

### Phase 3 — Fix Issues by Plugin

Work plugin-by-plugin in this priority order:

#### 3a. `ruff` (linting/formatting) — highest signal
- Run: `python3 -m uv run ruff check --fix src/ tests/`
- Run: `python3 -m uv run ruff format src/ tests/`
- Review unfixed rules; add `# noqa: <RULE>` with rationale only where auto-fix is wrong.

#### 3b. `mypy` (type errors)
- Run: `python3 -m uv run mypy src/ tests/`
- Fix type annotations in `src/autoscrapper/` as reported.
- Use `# type: ignore[<code>]` with comment only for unavoidable third-party gaps.

#### 3c. `bandit` (security)
- Review each finding; fix genuine issues (hardcoded secrets, subprocess shell=True, etc.).
- Mark false positives with `# nosec B<code> -- <reason>`.

#### 3d. `trufflehog` (secret scanning)
- If any secrets found: rotate immediately, then remove from history or add to `.qltyignore`.
- No suppressions for real secrets — fix or remove.

#### 3e. `actionlint` / `zizmor` (GitHub Actions)
- Fix workflow YAML issues in `.github/workflows/`.
- Common fixes: pin action versions, add explicit permissions, fix expression syntax.

#### 3f. `yamllint`
- Fix YAML formatting issues (trailing spaces, missing newlines, indentation).

#### 3g. `biome` (JS/TS — likely minimal in this Python project)
- Fix any JS/TS files if present; likely no findings.

#### 3h. Metrics (complexity)
- Files flagged by `qlty metrics -a` over complexity threshold:
  - Primary hotspot: `src/autoscrapper/ocr/inventory_vision.py` (229 edits — highest churn).
  - Break large functions into focused helpers where complexity > threshold.
  - Do NOT refactor beyond what the metric requires.

#### 3i. Smells
- `qlty smells -a` output is in "comment" mode — each smell is a code comment suggestion.
- Review each smell: apply if it improves clarity, skip if it changes behavior.

### Phase 4 — Validate

6. **Re-run qlty** to confirm zero remaining actionable issues:
   ```bash
   qlty check -a
   qlty metrics -a
   qlty smells -a
   ```

7. **Run project validation**:
   ```bash
   python3 -m uv run ruff check src/ tests/
   python3 -m uv run pytest
   ```

8. **Optional dry-run scan** (only if OCR/scanner files were modified):
   ```bash
   python3 -m uv run autoscrapper scan --dry-run
   ```

---

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Merge conflict in `inventory_vision.py` (hottest file) | Resolve conflict by keeping the upstream logic unless local fix is known-good; re-run OCR dry-run after |
| Autostash pop conflict | Resolve manually; check `git stash show` to identify what was stashed |
| mypy findings require large type annotation work | Fix only what qlty flags; defer full mypy clean-up to a separate PR |
| Complexity refactor breaks OCR calibration | Make minimal extractions; do not move calibration constants or pixel math |
| trufflehog false positive on test fixtures | Confirm with `--only-verified` flag; suppress confirmed false positives |

---

## Verification Steps

1. `qlty check -a` → exit 0 or all suppressions documented
2. `qlty metrics -a` → no files above threshold
3. `qlty smells -a` → no actionable smells
4. `python3 -m uv run ruff check src/ tests/` → exit 0
5. `python3 -m uv run pytest` → all tests pass
6. `git log --oneline -3` → clean commit history showing merge + fix commits

---

## Commit Strategy

- **Commit 1**: `chore: merge upstream main` (after phase 1)
- **Commit 2**: `fix: resolve qlty check issues (ruff, mypy, bandit)` (after phase 3a–3c)
- **Commit 3**: `fix: resolve qlty security and CI issues (trufflehog, actionlint)` (after phase 3d–3f)
- **Commit 4**: `refactor: reduce complexity per qlty metrics` (after phase 3h, if needed)

Keep commits atomic; do not batch unrelated changes.
