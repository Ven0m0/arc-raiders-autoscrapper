---
name: ai-tuning
description: Create repo-specific Copilot bootstrap assets: `.github/workflows/copilot-setup-steps.yml`, `.github/instructions/*.instructions.md`, and `.github/skills/*/SKILL.md`. Use when asked to tune a repository for Copilot, bootstrap repo guidance, add instructions or skills, or create or update `copilot-setup-steps`.
allowed-tools: "Read, Write, Edit, Glob, Grep, Bash"
---

# AI tuning

Create or refresh repository-specific Copilot bootstrap assets. Derive every file
from the current repository; do not paste generic templates without tailoring
them.

## Goal

Produce a minimal, repo-specific set of:

- `.github/workflows/copilot-setup-steps.yml`
- `.github/instructions/*.instructions.md`
- `.github/skills/*/SKILL.md`

Keep `.github/copilot-instructions.md` short and repo-wide. Put canonical
long-form guidance in `AGENTS.md`. Keep `CLAUDE.md` as a symlink to
`AGENTS.md`.

## Workflow

1. Audit the repository.
   - Identify languages, toolchains, package managers, and entry points.
   - Collect setup, lint, test, type-check, and build commands.
   - Inspect existing workflows, instructions, and skills before adding files.
   - Note OS or system packages required for setup.
2. Design the file split.
   - `.github/copilot-instructions.md`: short startup guidance only.
   - `AGENTS.md`: canonical repo-wide guidance.
   - `.github/instructions/`: path- or topic-specific rules.
   - `.github/skills/`: reusable repo workflows.
3. Create or update `.github/workflows/copilot-setup-steps.yml`.
   - Keep triggers minimal: `workflow_dispatch` plus `push` and
     `pull_request` scoped to the workflow file.
   - Set minimal `permissions:`.
   - Use pinned action versions.
   - Install only the repository's real system dependencies, toolchain, and
     project dependencies.
   - Match the repository's actual package manager, lockfiles, and version
     pins.
4. Create or update `.github/instructions/*.instructions.md`.
   - Add files only when the repository has a real language, workflow, or
     review need.
   - Keep each file focused and reusable.
   - Avoid duplicating large repo-wide rule blocks from `AGENTS.md`.
5. Create or update `.github/skills/*/SKILL.md`.
   - Add only reusable skills tied to real repo workflows.
   - Give each skill a clear trigger, narrow scope, and concrete steps.
   - Call out generated files, unsafe areas, and validation requirements.
6. Validate the result.
   - Verify every referenced file and command exists.
   - Run the repository's existing validation for changed workflow files.
   - Do not claim runtime or end-to-end validation you did not perform.

## Repo-specific requirements

- Tailor language versions to the repository's actual config files.
- Tailor setup steps to the repository's real system dependencies.
- Tailor validation commands to the repository's existing commands.
- Preserve conventions for generated files, lockfiles, setup scripts, and
  canonical guidance files.
- Prefer the smallest file set that gives high-signal guidance.

## Guardrails

- Never invent commands, paths, or dependencies.
- Do not hand-edit generated artifacts when the repository provides a script or
  generator.
- Keep guidance concise, actionable, and repository-specific.
- Update good existing files instead of creating duplicates.
- Use this split when deciding where guidance belongs:
  - Startup bootstrap: `.github/copilot-instructions.md`
  - Canonical repo-wide guidance: `AGENTS.md`
  - Path- or topic-specific rules: `.github/instructions/*.instructions.md`
  - Reusable task workflow: `.github/skills/*/SKILL.md`

## Deliverables checklist

- `copilot-setup-steps` matches the repository's real setup path.
- Instructions reflect the real stack, commands, and hotspots.
- Skills reflect recurring repository workflows.
- Large rule blocks are not duplicated across files.
- All changed files are internally consistent.
