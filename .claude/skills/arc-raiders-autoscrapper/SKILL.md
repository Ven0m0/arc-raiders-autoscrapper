```markdown
# arc-raiders-autoscrapper Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill introduces the core development patterns and conventions used in the `arc-raiders-autoscrapper` TypeScript codebase. It covers file organization, code style, commit message standards, and testing approaches. By following these guidelines, contributors can ensure consistency and maintainability across the project.

## Coding Conventions

### File Naming
- **Style:** Snake case
- **Example:**  
  ```plaintext
  data_parser.ts
  utils_helper.ts
  ```

### Import Style
- **Relative imports are used throughout the codebase.**
- **Example:**
  ```typescript
  import { parseData } from './data_parser';
  ```

### Export Style
- **Named exports are preferred.**
- **Example:**
  ```typescript
  // In data_parser.ts
  export function parseData(input: string): ParsedData { ... }
  ```

### Commit Messages
- **Conventional commit format is used.**
- **Prefix:** `chore`
- **Example:**
  ```
  chore: update dependencies to latest versions
  ```

## Workflows

### Code Update
**Trigger:** When making changes or adding features to the codebase  
**Command:** `/code-update`

1. Create a new branch for your changes.
2. Make code changes following the coding conventions.
3. Write or update tests as needed.
4. Commit your changes using the conventional commit format (e.g., `chore: ...`).
5. Push your branch and open a pull request.

### Testing
**Trigger:** Before pushing changes or opening a pull request  
**Command:** `/run-tests`

1. Identify all test files matching the `*.test.*` pattern.
2. Run the test suite using the project's test runner (framework not specified; check project scripts or documentation).
3. Review test results and fix any failing tests.

## Testing Patterns

- **Test File Naming:**  
  Test files follow the `*.test.*` pattern, e.g., `data_parser.test.ts`.
- **Testing Framework:**  
  Not explicitly specified; refer to project documentation or package.json for details.
- **Test Placement:**  
  Tests are placed alongside or near the modules they cover.

**Example:**
```typescript
// data_parser.test.ts
import { parseData } from './data_parser';

describe('parseData', () => {
  it('should parse valid input', () => {
    const result = parseData('example input');
    expect(result).toBeDefined();
  });
});
```

## Commands
| Command        | Purpose                                      |
|----------------|----------------------------------------------|
| /code-update   | Start the process for making code changes    |
| /run-tests     | Run the test suite before pushing changes    |
```
