---
name: fix-issue
description: Fix a GitHub issue end-to-end - from reading the issue, understanding requirements, implementing the fix, writing tests, and creating a commit. Use when given a GitHub issue number or URL to resolve.
user-invocable: true
disable-model-invocation: true
allowed-tools: "Bash, Read, Write, Edit, Glob, Grep"
---

# Fix GitHub Issue

Resolve GitHub issue `$ARGUMENTS` following repository coding standards.

<instructions>

## Workflow

Think step-by-step through the issue resolution:

1. **Read the issue**: Fetch issue details with `gh issue view $ARGUMENTS`
   - Extract: title, description, acceptance criteria, labels, linked PRs
   - If the issue references other issues or PRs, read those too

2. **Understand scope**: Before writing code, determine:
   - What files are affected? Search the codebase for relevant code
   - What is the root cause (for bugs) or desired behavior (for features)?
   - Are there existing tests that cover this area?
   - What is the minimal change needed?

3. **Implement the fix**:
   - Create a feature branch: `git checkout -b fix/issue-$ARGUMENTS`
   - Make focused, minimal changes that address the issue
   - Follow existing code patterns and conventions in the repository
   - Reference `instructions/` files for language-specific standards

4. **Write or update tests**:
   - Add tests that verify the fix works
   - Ensure existing tests still pass
   - Cover edge cases mentioned in the issue

5. **Verify**:
   - Run the project's test suite
   - Run linters if configured
   - Confirm the fix matches acceptance criteria from the issue

6. **Commit and document**:
   - Stage changes: `git add -A`
   - Commit with conventional format: `git commit -m "fix: <description> (#$ARGUMENTS)"`
   - Include `Closes #$ARGUMENTS` in the commit body if appropriate

</instructions>

<constraints>
- Never modify unrelated code
- Preserve existing behavior outside the fix scope
- If the issue is unclear, document assumptions in the commit message
- If the fix requires breaking changes, note them explicitly
</constraints>

<examples>

### Bug fix

```
Input: fix-issue 42
Steps:
  1. gh issue view 42 -> "Login button unresponsive on mobile"
  2. Search: rg "login" src/components/ -> LoginButton.tsx
  3. Root cause: click handler missing touch event
  4. Fix: add onTouchEnd handler alongside onClick
  5. Test: add mobile viewport test
  6. git commit -m "fix: add touch event to login button (#42)"
```

### Feature request

```
Input: fix-issue 87
Steps:
  1. gh issue view 87 -> "Add dark mode toggle to settings"
  2. Search: rg "theme" src/ -> ThemeProvider.tsx, settings.tsx
  3. Implement: add toggle component using existing ThemeProvider
  4. Test: verify toggle switches theme, persists preference
  5. git commit -m "feat: add dark mode toggle to settings (#87)"
```

</examples>
