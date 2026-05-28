---
name: grill-me
description: Pressure-test a plan, design, requirement, workflow, or implementation idea by interviewing the user one decision at a time until assumptions, dependencies, risks, and success criteria are explicit. Use when the user asks to "grill me", stress-test an idea, challenge a design, review a plan before execution, or wants structured questioning instead of immediate implementation.
---

# Grill Me

Interview the user relentlessly about every aspect of the plan until shared understanding is reached. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide a recommended answer.

## Process

1. Read the user's plan, draft, or material carefully first.
2. Check the repository and available resources — answer locally when possible instead of asking the user.
3. Default to one question at a time unless the user explicitly requests batch questioning.
4. If there is an obviously safer default option, include a recommended answer with each question.
5. Decide the next branch of questioning based on the user's previous answer.
6. Keep going until goals, scope, dependencies, constraints, trade-offs, and success criteria are all explicit.

## Questioning Order

If the user hasn't specified otherwise, follow this default order:

1. Goal — what problem, for whom.
2. Scope — what's in, what's out, what's deferred.
3. Inputs & dependencies — data, systems, roles, approvals, assumptions.
4. Behavior — core flows, edge cases, failure handling, recovery.
5. Constraints — performance, security, rules, compatibility, timeline.
6. Success criteria — how to know it's done right.

## Interaction Rules

- Prioritize questions that can change decisions — avoid open-ended brainstorming.
- If the answer is already in the codebase, state the conclusion and move on — don't re-ask.
- When the user's answer is too vague, narrow the scope immediately and ask more specifically.
- If contradictions surface, point them out right away and ask the user to resolve.
- Do not start implementing until the user explicitly switches from questioning to execution.

## Question Format

Use this compact structure by default:

```text
Question: ...
Recommended answer: ...
Why this matters: ...
```

Be direct but collaborative. The goal is not to win a debate — it's to make ambiguity explicit.
