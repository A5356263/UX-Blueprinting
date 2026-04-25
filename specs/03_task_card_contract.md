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
- `## Facts Output Requirements`
- `## Business Output Requirements`
- `## Experience Output Requirements`

The following sections are recommended but optional:

- `## Task Scenario`
- `## Read Order`
- `## Knowledge`
- `## Wiki`
- `## Knowledge Consumption Policy`
- `## Platform Optimizations`
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
- `Result Locations` must explicitly include both `workspace` viewing locations and final export locations.

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

Expected semantics:

- `Primary Knowledge Entry` lists the preferred wiki or summary entry pages.
- `Fallback Source` lists raw-source directories or files that may be used only when narrowing fails or coverage is insufficient.
- `Fallback Conditions` states when fallback is allowed, such as `[GAP]`, `[CONFLICT]`, or uncovered details.
- `Disallowed Broad References` states broad-reference modes that must not be copied by default.

## Parse Output

Execution must generate:

- `projects/<project-id>/runtime/task_card_resolved.json`

Minimum fields:

- `task_id`
- `protocol_name`
- `protocol_version`
- `task_name`
- `domain`
- `task_goal`
- `task_scenario`
- `execution_constraints`
- `read_order`
- `notes`
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
- `facts_output_requirements`
- `business_output_requirements`
- `experience_output_requirements`
- `warnings`
- `errors`

## Runtime Semantic Fields

- `task_goal`: Parsed from `## Task Goal`; required; describes the purpose and expected result of the task.
- `task_scenario`: Parsed from `## Task Scenario`; optional; describes the current usage or business scenario.
- `execution_constraints`: Parsed from `## Constraints`; required; defines hard execution boundaries.
- `read_order`: Parsed from `## Read Order`; recommended; defines the preferred runtime consumption order.
- `notes`: Parsed from `## Notes`; optional; records supplementary human-facing instructions.

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
- Any output requirement section is missing required subsections.
- `task_card_resolved.json` is not generated.
