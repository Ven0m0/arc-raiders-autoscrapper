---
name: planning
description: Clarify requirements, ask high-leverage questions, and produce scoped PRDs with measurable acceptance criteria. Use for vague requests, new features, or explicit planning/PRD tasks.
allowed-tools: "Read, Write, Edit, Glob, Grep"
---

# Planning

Unify discovery, requirements clarification, and PRD drafting before implementation begins.

> **MANDATORY:** For ambiguous or high-impact work, clarify first and write down scope before coding.

<when_to_use>

## Use This Skill When

| Scenario                            | Action                                         |
| ----------------------------------- | ---------------------------------------------- |
| Vague or underspecified request     | Ask clarifying questions before implementation |
| New feature or architectural change | Capture goals, constraints, and non-goals      |
| User asks for a PRD or feature plan | Draft a structured requirements document       |
| Scope changes mid-task              | Reconfirm assumptions and update the plan      |

</when_to_use>

<workflow>

## Phase 1: Discovery

Never skip discovery for unclear or architectural requests.

### Minimum Clarification Gate

Ask at least 2-3 high-leverage questions before drafting or implementing:

- **Problem**: What problem are we solving now?
- **Users**: Who is this for?
- **Scope**: What is required for v1 vs. later?
- **Success Metrics**: How will we measure success?
- **Constraints**: Stack, deadline, budget, compliance, team size?

### Dynamic Questioning Rules

- Ask questions that remove implementation forks
- Prefer trade-off framing over open-ended prompts
- Focus on blocking decisions first, then high-leverage decisions
- If a question will not change implementation, do not ask it

For the full questioning framework, read [`./dynamic-questioning.md`](./dynamic-questioning.md).

## Phase 2: Analysis

Synthesize the answers before drafting:

1. Map user flows from trigger to outcome
2. Separate goals from non-goals
3. Identify technical unknowns and risks
4. Research existing codebase patterns when applicable
5. Convert assumptions into explicit decisions or TBDs

## Phase 3: Draft

Produce a concise PRD or planning artifact with concrete, testable requirements.

- Use measurable targets
- Prefer explicit constraints over implied intent
- Keep scope boundaries visible
- Ask for feedback on unclear or high-risk sections

</workflow>

<prd_schema>

## PRD Structure

### 1. Executive Summary

- **Problem Statement**: 1-2 sentences
- **Proposed Solution**: 1-2 sentences
- **Success Criteria**: 3-5 measurable KPIs

### 2. User Experience

- **Personas**: Specific users and needs
- **User Stories**: `As a [user], I want [action] so that [benefit]`
- **Acceptance Criteria**: Testable done definitions for each story
- **Non-Goals**: Explicit exclusions for the current phase

### 3. Technical Specifications

- **Architecture**: Data flow and component interaction
- **Integration Points**: APIs, databases, auth, external systems
- **Security and Privacy**: Data handling and compliance constraints
- **Open Questions / TBDs**: Unresolved decisions with owner or next step

### 4. Risks and Rollout

- **Phasing**: MVP -> follow-up iterations
- **Technical Risks**: Probability, impact, mitigation

</prd_schema>

<constraints>

## Constraints

- Never draft a PRD without clarifying questions first when requirements are incomplete
- Every acceptance criterion must be testable
- Use numbers: `loads in <200ms`, not `loads quickly`
- If the stack is unknown, ask or label it `TBD`
- Stay inside requested scope; explicitly list non-goals

</constraints>

<examples>

## Example Acceptance Criteria

```text
As a team lead, I want to see average PR review times by repository so that I can identify review bottlenecks.

Acceptance Criteria:
- Dashboard shows average review time for the last 30 days
- Supports filtering by repository
- Refreshes hourly
- Loads in <2 seconds for up to 50 team members
```

## Example Risk Table

| Risk              | Probability | Impact | Mitigation                                  |
| ----------------- | ----------- | ------ | ------------------------------------------- |
| API rate limiting | Medium      | High   | Cache responses and batch requests          |
| Unclear scope     | High        | Medium | Lock non-goals and review with stakeholders |

</examples>
