---
name: grill-me
description: Pressure-test a plan, design, requirement, workflow, or implementation idea by interviewing the user one decision at a time until assumptions, dependencies, risks, and success criteria are explicit. Use when the user asks to "grill me", stress-test an idea, challenge a design, review a plan before execution, or wants structured questioning instead of immediate implementation.
---

# Grill Me

Drive toward shared understanding by asking sharp, sequential questions.

## Workflow

1. Read the user's plan, draft, or artifact closely.
2. Inspect the codebase or repo docs first for questions that can be answered locally.
3. Ask exactly one question at a time unless the user explicitly wants a batch.
4. Include a recommended answer with each question when a strong default exists.
5. Use the user's answer to choose the next branch of the decision tree.
6. Continue until scope, constraints, tradeoffs, and validation criteria are clear.

## Question Order

Ask in this rough order unless the user already settled a section:

1. Goal: what problem is being solved and for whom.
2. Scope: what is included, excluded, and deferred.
3. Inputs and dependencies: data, systems, people, approvals, assumptions.
4. Behavior: core flow, edge cases, failure handling, recovery.
5. Constraints: performance, security, policy, compatibility, timelines.
6. Success criteria: how the user will know the plan worked.

## Interaction Rules

- Prefer concrete, high-leverage questions over generic brainstorming.
- If the repo already answers something, state the finding and move on instead of asking.
- When the user gives a vague answer, narrow it with a more specific follow-up.
- Surface contradictions immediately and ask the user to resolve them.
- Do not start implementing changes unless the user explicitly switches from critique to execution.

## Recommended Question Style

Use a compact pattern:

```text
Question: ...
Recommended answer: ...
Why this matters: ...
```

Keep the tone direct but collaborative. The goal is not to "win"; the goal is to remove ambiguity.
