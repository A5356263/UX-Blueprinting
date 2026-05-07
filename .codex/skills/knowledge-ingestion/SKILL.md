---
name: knowledge-ingestion
description: Safely merge new material into this repository's knowledge system without polluting the source of truth. Use when Codex needs to ingest help-center notes, product docs, requirement drafts, screenshots analysis, meeting notes, external references, or legacy .claude materials into `knowledge/`, `docs/`, `specs/`, `templates/`, or related project structures.
---

# Knowledge Ingestion

Ingest new material only after identifying where truth lives in this repo and what should remain as process residue instead of formal knowledge.

## Repository Truth Map

Use these defaults unless stronger local evidence in the target area says otherwise:

- `specs/`: formal execution contracts and normative rules.
- `knowledge/`: reusable business, product, design, and domain knowledge.
- `docs/`: explanatory notes, discussion, and runbooks; useful but usually less normative than `specs/`.
- `templates/`: reusable artifact templates, not raw facts.
- `projects/`: task-specific runtime and delivery artifacts.
- `.claude/`: legacy Claude-oriented materials; useful source input, not the canonical Codex layer.

Do not recreate a root `skills/` directory for repository logic. This repo already moved core behavior into `specs/`, `packages/`, `projects/`, `knowledge/`, and `templates/`.

## Ingestion Workflow

1. Read the target area before writing anything.
2. Identify the local contract from files such as `README.md`, `CLAUDE.md`, relevant `specs/`, nearby examples, and folder structure.
3. Classify the incoming material.
4. Decide whether to merge, create, stage for review, or reject.
5. Write the smallest durable change that preserves provenance and avoids duplicating truth.
6. Update indexes, manifests, or logs only when the repo already uses them or the task clearly requires them.
7. Verify the destination still matches the surrounding structure and naming style.

## Classification Rules

Treat incoming content as one of these categories:

### 1. Durable knowledge

Good candidates for ingestion:

- stable business or product facts
- explicit rules, constraints, fields, states, dependencies
- reusable design or workflow knowledge
- durable summaries of authoritative source material

### 2. Process residue

Do not write these into canonical knowledge by default:

- crawl logs
- collection coverage reports
- browser steps
- temporary analysis notes
- tool failures
- execution transcripts

Keep them in process-log style locations when needed, or mention them in the final report without promoting them to truth.

### 3. Unresolved information

Preserve uncertainty explicitly:

- `[GAP]` for missing information
- `[CONFLICT]` for source disagreement
- `[QUESTION]` for issues requiring human confirmation

Do not silently fill these with guesses.

### 4. Noise

Usually reject:

- marketing filler
- footer/legal/contact boilerplate
- duplicated low-signal text
- content unrelated to the repo's knowledge scope

## Decision Rules

Prefer merge over sprawl.

Merge into an existing file when the new material extends or corrects an existing topic cleanly.

Create a new file only when:

- the topic is durable
- no existing file is the right home
- the content is large enough to stand on its own
- the new file fits the repo's current organization

Stage or defer when:

- ownership is unclear
- the source is incomplete
- multiple destinations are plausible
- the material is mostly process residue with a few useful facts mixed in

Reject when the content adds no lasting value.

## Project-Specific Guardrails

- Do not make `.claude/` the canonical instruction layer for Codex.
- Do not overwrite a stronger source in `specs/` with weaker notes from `docs/`, chat text, or collection output.
- Do not turn navigation files, summaries, or indexes into a second source of truth.
- Do not force every input into the same structure.
- Do not invent missing numbering, folders, or taxonomies just for neatness.

## Handling Help-Center Collection Output

If the input came from a collector or scraped documentation set:

- ingest article content, explicit rules, flows, fields, and dependencies
- keep `_collection`, coverage, failure, and crawl artifacts out of canonical knowledge
- keep partial collection gaps visible instead of pretending the source set is complete

## Output Checklist

Before finishing, confirm:

- the destination matches the local contract
- durable facts were separated from process residue
- uncertainty is explicitly marked
- no weaker source displaced a stronger one
- indexes or summaries were updated only if needed

Report what was merged, what was deferred, and any remaining `[GAP]`, `[CONFLICT]`, or `[QUESTION]` items.
