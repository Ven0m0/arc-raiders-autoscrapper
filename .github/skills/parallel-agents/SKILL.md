---
name: parallel-agents
description: Coordinates built-in and custom agents when work can be parallelized or staged. Use when one agent is not enough for the task.
---

# Parallel agents

Use this skill to split independent workstreams, route tasks to the right agent, and synthesize one final answer. Keep the plan grounded in the agents that actually exist in this repository.

## Usage

Use this skill when the task naturally separates into discovery, research, implementation, or review streams.

## When to use

| Good fit                                         | Avoid                                              |
| ------------------------------------------------ | -------------------------------------------------- |
| Exploration plus implementation plus review      | Small single-file edits                            |
| Independent subproblems that can run in parallel | Tasks where one agent already has the full context |
| Domain handoffs: research -> code -> review      | Busywork that only adds coordination overhead      |

## Agent routing

| Need                            | Agent                              |
| ------------------------------- | ---------------------------------- |
| Broad repo discovery            | `explore` or custom `explorer`     |
| Architecture and task breakdown | `planner`                          |
| External best-practice research | `researcher`                       |
| Implementation                  | `coder`                            |
| Critical review                 | `reviewer`                         |
| Bug investigation               | `debug`                            |
| UI work                         | `frontend-specialist`              |
| Workflow/CI work                | `workflow-engineer`                |
| AI config or repo structure     | `repo-architect`                   |
| Cleanup and dead code removal   | `codebase-maintainer` or `janitor` |
| Git workflow help               | `git`                              |

## Workflow

1. Split the task into independent workstreams.
2. Route each workstream to the narrowest capable agent.
3. Run independent discovery or research in parallel when safe.
4. Pass concrete findings into downstream coding or review agents.
5. Synthesize one final answer instead of returning disconnected agent outputs.

## Recommended patterns

| Pattern         | Sequence                                                 |
| --------------- | -------------------------------------------------------- |
| Full feature    | `explorer -> planner -> researcher -> coder -> reviewer` |
| Focused bug fix | `debug -> coder/reviewer`                                |
| Repo cleanup    | `codebase-maintainer -> reviewer`                        |
| Workflow change | `workflow-engineer -> reviewer`                          |

## Guardrails

- Use only agents that are actually available in the current environment.
- Prefer one strong agent over many weakly related ones.
- Do not parallelize steps that depend on prior findings.
- Keep context handoff tight: paths, findings, constraints, expected output.

## Examples

### Example: multi-step feature

1. `explorer` maps affected files.
2. `planner` breaks work into waves.
3. `coder` implements the approved plan.
4. `reviewer` audits the result.

### Example: two independent checks

- `researcher` investigates an external library.
- `workflow-engineer` checks CI implications.
- Merge both findings before implementation.
