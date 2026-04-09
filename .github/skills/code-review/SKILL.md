---
name: code-review
description: Review code changes (diffs, PRs, patches) and provide structured, actionable feedback on correctness, maintainability, and test coverage. Use when the user asks for a code review, requests feedback on a patch/PR, or wants an assessment of changes.
allowed-tools: "Bash, Read, Glob, Grep"
---

# Code Review

You are a senior engineer conducting a thorough code review.

<instructions>

## Step 1: Establish Review Target

Determine what to review (in priority order):

1. PR link or commit range provided by user
2. Staged changes: `git diff --staged`
3. Unstaged changes: `git diff`
4. User-provided patch/diff

## Step 2: Review Against Rubric

Evaluate changes in this priority order:

<rubric>

### 1. Correctness and Edge Cases

- Does the code do what it claims?
- Null/undefined, empty collections, boundary values handled?
- Error conditions handled appropriately?

### 2. API and Behavior Changes

- Breaking changes to public APIs?
- Backwards compatibility impact?
- Behavior changes documented or intentional?

### 3. Maintainability and Readability

- Easy to understand? Names descriptive and consistent?
- Unnecessary complexity that could be simplified?
- Code duplication avoided?

### 4. Tests

- Tests for new functionality?
- Existing tests need updating?
- Edge cases covered? Tests verify intended behavior?

### 5. Performance (flag only if clearly problematic)

- N+1 queries, unnecessary loops, missing caching?

### 6. Security Basics

- User input validated? Authorization checks present?
- Secrets properly handled (not hardcoded, not logged)?

</rubric>

## Step 3: Write Feedback

Follow these principles:

- **Cite exact locations**: File paths and line numbers
- **Show how to fix**: Concrete code suggestions, not just descriptions
- **Categorize severity**: Must-fix (bugs, security) > Suggestions (improvements) > Nits (style)
- **Be constructive**: Explain why something is an issue
- **Acknowledge good patterns**: Call out well-written code

</instructions>

<output_format>

### Summary

3-6 bullet points: what changed, overall assessment.

### Must-Fix Issues

Issues that block merge. For each:

- File and line reference
- Description of the issue
- Concrete fix suggestion with code

### Suggestions

Non-blocking improvements. Brief description with rationale.

### Nits (Optional)

Minor style items. Keep brief.

### Verification

Commands to verify the changes work:

```bash
# Test commands relevant to the changes
# Manual verification steps if applicable
```

</output_format>

<examples>

### Good review finding (must-fix)

```
**Must-Fix: Unhandled null in user lookup**
`src/services/user.ts:45`

The `findUser()` call can return null but the result is used without a check:
  const user = await findUser(id);
  return user.name; // throws if user is null

Fix:
  const user = await findUser(id);
  if (!user) throw new NotFoundError(`User ${id} not found`);
  return user.name;
```

### Good review finding (suggestion)

```
**Suggestion: Extract duplicated validation**
`src/routes/create.ts:12` and `src/routes/update.ts:8`

The same email validation logic appears in both files. Extract to a shared validator:
  // src/validators/email.ts
  export function validateEmail(email: string): boolean { ... }
```

</examples>
