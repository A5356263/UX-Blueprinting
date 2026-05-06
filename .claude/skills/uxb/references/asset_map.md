# UXB Asset Map

Use this guide to know where repository assets live and how to treat them.

## Principle

This file explains asset types and usage rules. It is not a promise to maintain a complete directory inventory.

Trust the current repository structure.

## Execution Hub

```text
packages/
```

This is the stable execution entrypoint for task creation, context assembly, generation, validation, repair, archive, and preview behavior.

The skill should call it, not duplicate it.

## Knowledge Base

```text
knowledge/
```

Use it for business and experience consultation.

Start from:

```text
knowledge/wiki/index.md
```

Prefer navigation, route cards, indexes, summaries, and README-style entry files before diving deeper.

## Formal Rules

```text
specs/
```

This is the source of truth for formal rule contracts. When formal outputs or stage boundaries matter, defer to `specs/`.

## Templates

```text
templates/
```

Use these as the formal artifact templates when generating facts, business, experience, and related outputs.

## Project Artifact Area

```text
projects/<project-id>/
```

This is where formal task inputs and outputs belong.

Typical structure:

```text
source/
workspace/
runtime/
exports/
```

The skill does not manage this area manually unless the task requires writing confirmed formal inputs there.
