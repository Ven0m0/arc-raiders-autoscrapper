---
name: app-builder
description: Coordinates greenfield app scaffolding and rapid prototyping with official starters and focused sub-agents. Use when creating a new application or shaping a fast prototype.
---

# App builder

Use this skill for new-project work. Keep it centered on discovery, stack selection, official scaffolding tools, and the smallest viable workflow needed to ship a working prototype.

## Usage

Use this skill for greenfield scaffolding first; for follow-up feature work, read only the narrow modules that match the request.

## Selective reading rule

Read only the modules that match the request:

- `project-detection.md` for project type and platform clues
- `tech-stack.md` for stack selection
- `agent-coordination.md` for multi-agent execution
- `scaffolding.md` for project structure
- `feature-building.md` for follow-on feature work
- [templates/REFERENCE.md](templates/REFERENCE.md) for starter templates

## When to use

| Situation                 | Apply this skill                                     |
| ------------------------- | ---------------------------------------------------- |
| New app from a prompt     | Choose stack, scaffold, and hand off implementation  |
| Local-first prototype     | Optimize for fastest path to a working demo          |
| Existing app feature work | Use only the relevant feature or scaffolding modules |

## Workflow

1. Clarify product goal, target users, core flows, platform, and deployment target.
2. Reuse the repo's existing stack when extending an app; for new apps, choose the smallest viable starter.
3. Scaffold with the framework's official generator or the closest maintained template.
4. Hand off specialized work to the right agent (`planner`, `coder`, `frontend-specialist`, `workflow-engineer`, `reviewer`).
5. Verify the starter runs with the stack-native install, lint, test, build, and dev commands.

## Guardrails

- Prefer official starters and generators over hand-written scaffolds.
- Keep the first iteration narrow: one clear happy path beats a half-finished platform.
- Add polish only after the prototype runs end to end.
- Route domain-specific follow-up work to dedicated skills instead of embedding full framework manuals here.

## Examples

### Example: greenfield web app

1. Detect app type from the prompt.
2. Read the matching template or stack module.
3. Scaffold with the official starter.
4. Delegate implementation details to `coder` or `frontend-specialist`.
5. Verify the generated app builds and runs locally.

### Example: existing app enhancement

1. Skip the greenfield templates.
2. Read only `feature-building.md` plus the relevant stack module.
3. Plan the smallest change that extends the current app cleanly.
