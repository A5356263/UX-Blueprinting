# Knowledge Usage Guide

Use this guide when consultation or task shaping needs repository knowledge.

## Goal

Find the right knowledge for the current question without bulk-loading `knowledge/`.

## Core Rules

- Identify the question before reading knowledge.
- Start from navigation and summaries.
- Read detailed source material only when needed.
- If uncertain, state the uncertainty or confirm with the user.

## Entry Point

Start from:

```text
knowledge/wiki/index.md
```

Then narrow down through the current repo structure, such as:

- navigation pages
- route cards
- indexes
- summaries
- domain README files

Do not assume older structures are still valid. Trust the current repository layout.

## Scope Control

Never read the whole `knowledge/` tree by default just to save effort.

Shrink the search scope step by step based on:

- business objects
- user roles
- actions
- state changes
- exception cases
- module names
- page or flow names
- rules, permissions, approvals, configuration, feedback, or copy concerns

## Ambiguous Terms

If one phrase could point to several domains, explain the ambiguity in plain Chinese before overcommitting.

Example pattern:

- "I am currently interpreting this as configuration approval. If you mean contract approval or HR approval, the judgment would change."

Only ask for confirmation when the ambiguity materially changes the advice.

## Summary First, Raw Later

Prefer:

- summary files
- route cards
- module descriptions
- overview files

Read more detailed source material only when:

- the summary is insufficient
- evidence is needed
- the user explicitly asks for source-level traceability

## How to Use Knowledge in Replies

Use knowledge to improve judgment, not to mechanically quote repo file paths back at the user.

Prefer user-facing phrasing like:

- "Based on the current project knowledge, this looks more like a state explanation problem than only a button design problem."

Avoid file-dump phrasing unless the user asks for exact sources.
