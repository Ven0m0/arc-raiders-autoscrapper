---
name: pr-review
description: Summarize changes in a pull request with structured analysis of what changed, why, and potential concerns. Use when asked to review a PR, summarize PR changes, or understand what a PR does.
allowed-tools: "Bash(gh *), Read, Glob, Grep"
---

# Pull Request Summary

Summarize and analyze the current pull request.

<instructions>

## Gather Context

Collect PR data before analysis:

- PR metadata: `gh pr view`
- Full diff: `gh pr diff`
- Changed files: `gh pr diff --name-only`
- PR comments and reviews: `gh pr view --comments`
- CI status: `gh pr checks`

## Analysis Steps

Think through the PR systematically:

1. **Categorize changes**: Group modified files by purpose (feature code, tests, config, docs)
2. **Identify the intent**: What problem does this PR solve? Reference issue links if present
3. **Assess scope**: Is this a focused change or does it touch many unrelated areas?
4. **Check completeness**: Are there tests? Are docs updated? Are migrations included?
5. **Flag concerns**: Breaking changes, security implications, performance impact, missing tests

## Output Format

Structure the summary as:

### Overview

One paragraph describing what the PR does and why.

### Changes by Area

Group changes into logical categories with brief descriptions.

| Area    | Files          | Summary               |
| ------- | -------------- | --------------------- |
| Feature | `src/auth/`    | Added OAuth2 flow     |
| Tests   | `tests/auth/`  | Coverage for new auth |
| Config  | `.env.example` | New OAuth env vars    |

### Key Decisions

Notable implementation choices, trade-offs, or patterns used.

### Potential Concerns

- Breaking changes
- Missing test coverage
- Security considerations
- Performance implications

### Verdict

Overall assessment: ready to merge, needs changes, or needs discussion.

</instructions>

<examples>

### Simple bugfix PR

```
Overview: Fixes null pointer in UserService.getProfile() when user has no avatar set.
Changes: 1 file (src/services/user.ts), 1 test file
Key Decision: Returns default avatar URL instead of null
Concerns: None
Verdict: Ready to merge
```

### Complex feature PR

```
Overview: Adds real-time notifications via WebSocket with Redis pub/sub backend.
Changes: 12 files across services, middleware, frontend, tests, and config
Key Decision: Chose Redis pub/sub over polling for scalability
Concerns: No load testing results, missing reconnection logic, new Redis dependency
Verdict: Needs changes - address reconnection handling before merge
```

</examples>
