---
name: playwright-cli
description: Runs repeatable browser flows with playwright-cli. Use when a task needs navigation, form entry, snapshots, debugging, or artifact capture in a real browser.
---

# Browser automation with playwright-cli

Use this skill for the workflow and decision points, not as a command encyclopedia. Prefer snapshots over screenshots for interaction, keep sessions short-lived unless persistence is required, and store artifacts only when the task asks for them.

## Usage

Reach for this skill when real browser state matters and command-line HTTP calls or static HTML inspection are not enough.

## When to use

| Situation                      | Primary commands                                      |
| ------------------------------ | ----------------------------------------------------- |
| Start or resume a browser flow | `open`, `goto`, `snapshot`, `close`                   |
| Interact with page elements    | `click`, `fill`, `type`, `select`, `press`            |
| Inspect state                  | `snapshot`, `eval`, `console`, `network`              |
| Capture artifacts              | `screenshot`, `pdf`, `tracing-start`, `tracing-stop`  |
| Manage state or tabs           | `state-save`, `state-load`, `tab-*`, storage commands |

## Workflow

1. Open a session and navigate to the target URL.
2. Take or inspect a snapshot to get stable element refs.
3. Interact with the page using those refs.
4. Re-snapshot after meaningful state changes.
5. Capture screenshots, PDFs, traces, or video only when the task needs artifacts.
6. Close the session and clean up persistent data if it was created just for the task.

## Guardrails

- Prefer `snapshot` for navigation and verification; screenshots are for deliverables.
- Use named sessions only when the flow spans multiple steps or needs persisted auth/state.
- Mock routes, tracing, and storage commands are opt-in; do not enable them without a task reason.
- If the global binary is missing, fall back to `npx playwright-cli ...`.

## Examples

### Basic interaction loop

```bash
playwright-cli open https://example.com
playwright-cli snapshot
playwright-cli click e3
playwright-cli fill e5 "user@example.com"
playwright-cli snapshot
playwright-cli close
```

### Capture a trace for debugging

```bash
playwright-cli open https://example.com
playwright-cli tracing-start
playwright-cli snapshot
playwright-cli tracing-stop
playwright-cli close
```

## Specific tasks

- **Request mocking** [references/request-mocking.md](references/request-mocking.md)
- **Running Playwright code** [references/running-code.md](references/running-code.md)
- **Browser session management** [references/session-management.md](references/session-management.md)
- **Storage state (cookies, localStorage)** [references/storage-state.md](references/storage-state.md)
- **Test generation** [references/test-generation.md](references/test-generation.md)
- **Tracing** [references/tracing.md](references/tracing.md)
- **Video recording** [references/video-recording.md](references/video-recording.md)
