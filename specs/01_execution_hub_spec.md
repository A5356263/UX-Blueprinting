# Execution Hub Spec

## Goal

Define how the execution hub advances a task through the formal pipeline, while keeping task-card parsing, context assembly, generation, validation, and archive behavior aligned with the current contracts.

## Positioning

The execution hub is a lightweight orchestration layer. It is responsible for:

- progressing the task by fixed steps
- validating formal inputs and outputs
- exposing blockers and warnings explicitly
- writing stable runtime artifacts
- preserving stage boundaries

The execution hub is not responsible for:

- replacing business judgment
- replacing experience reasoning
- inventing new knowledge conclusions
- silently widening references for convenience

## Upstream Contracts

The execution hub must follow:

- `specs/03_task_card_contract.md`
- `specs/04_knowledge_reference_contract.md`
- `specs/05_output_contract.md`
- `specs/06_check_contract.md`
- `specs/07_wiki_contract.md`
- `specs/08_fact_extraction_contract.md`
- `specs/09_business_blueprint_contract.md`
- `specs/10_experience_blueprint_contract.md`
- `specs/11_repair_loop_contract.md`
- `specs/14_experience_preview_contract.md`

## Execution Object

Standard project layout:

```text
projects/<project-id>/
  source/
  workspace/
  runtime/
  exports/
```

## Unified Status Model

- `pending`: not started
- `running`: in progress
- `passed`: completed and valid
- `warning`: completed with warnings
- `failed`: blocked

## Failure Principles

- failures must not be swallowed silently
- missing required inputs must become explicit errors
- incomplete formal outputs must be treated as failures
- warnings cannot be reported as passed
- downstream steps must not bypass upstream blockers

## Step 1: Task Bootstrap

Create the minimum task directory structure and placeholder inputs.

## Step 2: Task Card Resolve

Parse `task_card.md` into `runtime/task_card_resolved.json`.

Execution must:

- parse required sections and protocol fields
- parse knowledge references and knowledge consumption policy
- classify references by granularity
- expose broad references as warnings instead of silently normalizing them away

## Step 3: Context Assembly

Assemble the minimum context snapshot from explicit references.

Execution must:

- consume `task_card_resolved.json`
- prefer file or stable index-page entries over directory copies
- attempt directory narrowing before copying broad references
- write `runtime/context_manifest.json`
- write `runtime/knowledge_usage_report.json`

Strict behavior:

- `python -m packages assemble <project-id> --strict` must fail on unresolved directory references
- `python -m packages run-main <project-id> --strict` must pass strict behavior into the assemble step

Ordinary behavior:

- unresolved directory references may still be copied
- the fallback must be recorded as a warning and as a fallback action

## Step 4: Fact Extraction

Generate `workspace/facts.md` from task inputs, using assembled knowledge as calibration only.

## Step 5: Business Blueprint Build

Generate `workspace/business_blueprint.md` from facts plus explicit business knowledge.

## Step 6: Experience Blueprint Build

Generate `workspace/experience_blueprint.md` from facts, business blueprint, and explicit guidance.

## Step 7: Stage Gates

Run `gate-facts`, `gate-business`, and `gate-experience` as separate formal checks.

## Step 8: Final Validation and Coverage

Validate:

- output existence
- section completeness
- stage-boundary compliance
- traceability
- coverage
- broad-reference risk visibility

Validate must report broad-reference issues such as:

- unresolved directory references
- fallback usage without stated fallback conditions
- broad references kept even though a stable index entry existed

Validate must not auto-fix any of the above.

## Step 9: Archive

Archive final deliverables only after validation and coverage status are acceptable under the current contracts.

## Recommended Commands

- `python -m packages assemble <project-id>`
- `python -m packages assemble <project-id> --strict`
- `python -m packages generate-facts <project-id>`
- `python -m packages generate-business <project-id>`
- `python -m packages generate-experience <project-id>`
- `python -m packages run-main <project-id>`
- `python -m packages run-main <project-id> --strict`
- `python -m packages run-main <project-id> --skip-preview`
- `python -m packages sample-check`
