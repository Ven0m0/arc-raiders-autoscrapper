---
name: nodejs-best-practices
description: Guides Node.js, Next.js, and NestJS work with stack-aware architecture and verification checkpoints. Use when building, reviewing, or refactoring TypeScript services and web apps.
---

# Node.js, Next.js, and NestJS Best Practices

Keep this skill focused on choices an agent still needs to make: fit the change to the existing stack, keep boundaries clean, and verify the repo-native lifecycle commands. Do not turn it into a framework textbook.

## Usage

Use this skill when the task needs stack selection or architecture judgment, not when repo-wide TypeScript rules already answer the question.

## When to use

| Situation                 | Focus                                                                      |
| ------------------------- | -------------------------------------------------------------------------- |
| Existing Node.js service  | Preserve the current framework and package manager first                   |
| Next.js change            | Server/client boundaries, route conventions, data fetching, cache behavior |
| NestJS change             | Feature modules, provider boundaries, DTO validation, controller thinness  |
| Greenfield TypeScript app | Choose the smallest stack that fits the requirements and deployment target |

## Workflow

1. Identify the current stack, runtime, package manager, and deployment target.
2. Extend the existing framework unless the user explicitly wants a migration.
3. Keep business rules outside routes, controllers, and framework glue.
4. Validate inputs, environment, and external data at boundaries.
5. Re-run the stack's lint, typecheck, test, and build commands before finishing.

## Architecture defaults

| Concern          | Default                                                                                  |
| ---------------- | ---------------------------------------------------------------------------------------- |
| Type safety      | Strict TypeScript, explicit boundary types, minimal `any`                                |
| Request handling | Thin route/controller layer -> service/domain layer -> data layer                        |
| Validation       | Request params, bodies, env, and external responses validated early                      |
| Errors           | Central formatting/logging; do not leak internals to clients                             |
| Async work       | No sync I/O on hot paths; parallelize only independent work                              |
| Security         | Secrets in env, parameterized DB access, verified auth tokens, rate limits where exposed |

## Framework-specific reminders

| Stack            | High-signal checks                                                                |
| ---------------- | --------------------------------------------------------------------------------- |
| Next.js          | Server components by default; opt into client components only for interactivity   |
| Next.js          | Use route handlers or server actions with validation and explicit caching choices |
| NestJS           | Group by feature, keep controllers thin, validate DTOs at the edge                |
| Shared contracts | Centralize schemas/types when UI and API evolve together                          |

## Related skills

- Use `premium-frontend-ui` for UI/UX and component polish.
- Use `workflow-development` for CI/CD and deployment wiring.
- Use `docker-expert` when containerization or image hygiene is part of the task.

## Examples

### Good uses

- Deciding whether a change belongs in a Next.js route handler, a server action, or a shared service.
- Pulling validation out of a NestJS service and moving it to DTO/controller boundaries.
- Reviewing a Node.js API for sync I/O, weak typing, or controller-heavy business logic.

### Out of scope

- Copying full framework tutorials into the skill.
- Encoding version-by-version release notes or tool marketing.
- Repeating generic TypeScript advice that already exists in repo-wide instructions.
