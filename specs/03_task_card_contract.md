# Task Card Contract

## Goal

Define the required structure, path rules, and parse result for `projects/<project-id>/source/task_card.md`.

## Positioning

`task_card.md` is the formal execution entry contract. It describes task scope, explicit references, and delivery targets. It is not the place to replace business judgment or wiki source content.

## Required Sections

The following level-2 sections must exist and must be machine-parseable:

- `## Protocol`
- `## Task Goal`
- `## Required Inputs`
- `## Required Outputs`
- `## Constraints`
- `## Templates`
- `## Checks`
- `## Result Locations`
- `## Completion Criteria`

The following sections are recommended but optional:

- `## Task Scenario`
- `## Read Order`
- `## Knowledge`
- `## Wiki`
- `## Design Guidelines`
- `## Knowledge Consumption Policy`
- `## Platform Optimizations`
- `## Facts Output Requirements`
- `## Business Output Requirements`
- `## Experience Output Requirements`
- `## Notes`

## Protocol Fields

`## Protocol` must include:

- `Protocol Name`
- `Protocol Version`
- `Task ID`

It may additionally include:

- `Task Name`
- `Domain`

## Path Rules

- All paths must use repository-relative paths.
- Absolute paths are not allowed.
- URLs are not allowed in place of repository files.
- Every `Required Outputs` entry must stay under `projects/<project-id>/workspace/`.
- `Result Locations` must explicitly include both workspace viewing locations and final export locations.

## Knowledge Reference Rules

- `Knowledge`, `Wiki`, `Templates`, and `Checks` must be extractable item by item.
- Prefer file or stable index-page references over directory references.
- If a task must keep a broad source reference, it must also provide a narrowing policy in `## Knowledge Consumption Policy`.
- `Platform Optimizations` is supplementary only and cannot replace formal inputs, outputs, or knowledge references.

## Knowledge Consumption Policy

When `## Knowledge Consumption Policy` exists, it should be structured with bullet-based subsections:

- `Primary Knowledge Entry`
- `Fallback Source`
- `Fallback Conditions`
- `Disallowed Broad References`

## Parse Output

Execution must generate:

- `projects/<project-id>/runtime/task_card_resolved.json`

Minimum fields:

- `task_id`
- `protocol_name`
- `protocol_version`
- `task_name` (optional)
- `domain` (optional)
- `task_goal`
- `task_scenario` (optional)
- `execution_constraints`
- `read_order` (optional)
- `notes` (optional)
- `required_inputs`
- `required_outputs`
- `knowledge_refs`
- `wiki_refs`
- `template_refs`
- `check_refs`
- `primary_knowledge_entries`
- `fallback_source_refs`
- `fallback_conditions`
- `disallowed_broad_references`
- `reference_granularity`
- `has_directory_ref`
- `requires_narrowing`
- `result_locations`
- `completion_criteria`
- `facts_output_requirements` (optional — parsed from `## Facts Output Requirements` if present)
- `business_output_requirements` (optional — parsed from `## Business Output Requirements` if present)
- `experience_output_requirements` (optional — parsed from `## Experience Output Requirements` if present)
- `warnings`
- `errors`

## Runtime Semantic Fields

- `task_goal`: Parsed from `## Task Goal`; required; describes the purpose and expected result of the task.
- `task_scenario`: Parsed from `## Task Scenario`; optional; describes the current usage or business scenario.
- `execution_constraints`: Parsed from `## Constraints`; required; defines hard execution boundaries.
- `read_order`: Parsed from `## Read Order`; recommended; defines the preferred runtime consumption order.
- `notes`: Parsed from `## Notes`; optional; records supplementary human-facing instructions.

## Output Requirements

`## Facts Output Requirements`, `## Business Output Requirements`, and `## Experience Output Requirements` are optional sections. When present, they should reference their respective contract files (`specs/08_*`, `specs/09_*`, `specs/10_*`) and provide brief guidance. They should not enumerate exhaustive required subsections or prescribe ID numbering systems.

## Warning Conditions

The task card may still pass with warnings when:

- `## Wiki` is missing but `## Knowledge` exists.
- `## Read Order` is missing.
- `## Read Order` exists but cannot be parsed into readable items.
- A knowledge or wiki reference is directory-only or wildcard-based.
- `## Knowledge Consumption Policy` is missing while broad references are present.
- `## Platform Optimizations` exists but is empty.

## Failure Conditions

- `task_card.md` is missing.
- Any required section is missing.
- `Protocol Name`, `Protocol Version`, or `Task ID` is missing.
- `Required Outputs` is empty.
- Any output path is outside `projects/<project-id>/workspace/`.
- Any reference section exists but cannot be parsed into path entries.
- `Task Goal` exists but cannot be parsed into readable items.
- `Constraints` exists but cannot be parsed into readable items.
- `task_card_resolved.json` is not generated.
