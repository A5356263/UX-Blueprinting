# Knowledge Reference Contract

## Goal

Define how tasks reference `knowledge/wiki/`, `knowledge/raw/`, and other explicit knowledge assets, and how execution narrows broad references during context assembly.

## Knowledge Layer Responsibilities

- `knowledge/wiki/`: default consumption layer, especially index pages and summary pages.
- `knowledge/raw/`: source-of-truth layer for detailed fallback lookup.
- Task card and execution hub: decide what is consumed for the current task and how broad references are narrowed.
- Generation stages: consume assembled context only.
- Validate and coverage: expose broad-reference risk and fallback usage, but do not silently rewrite references.

## Default Consumption Order

1. `task_card.md`
2. Explicit wiki entry pages referenced by the task
3. Explicit summary pages referenced by the task
4. Explicit fallback raw sources under allowed conditions
5. Templates and checks

## Reference Rules

- Tasks must prefer file or stable index-page references.
- Directory references are considered broad references and must be narrowed before normal assembly whenever possible.
- Wildcard references are descriptive only and must not be copied into `context_bundle/` as raw patterns.
- A broad reference is acceptable only if the task card also defines a consumption policy that makes narrowing and fallback behavior explicit.

## Narrowing Rules

When a reference points to a directory, the execution hub must attempt narrowing in the following order:

1. Explicit `Primary Knowledge Entry` under the same directory
2. `README.md`
3. `index.md`
4. `*-index.md`
5. `*-domain-index.md`

If a stable entry is found, execution should copy that entry instead of copying the whole directory.

If no stable entry is found:

- ordinary mode: emit a warning and allow fallback directory copy
- strict mode: fail the assembly step

## Fallback Rules

Fallback to raw-source references is allowed only when the task card states a valid fallback condition, for example:

- summary page contains `[GAP]`
- summary page contains `[CONFLICT]`
- summary page does not cover the needed object, rule, path, or decision point

## Context Assembly Requirements

Context assembly must:

- read `task_card_resolved.json`
- record every explicit reference in `context_manifest.json`
- record narrowing decisions, fallback copies, and broad-reference warnings
- copy only resolved files, allowed fallback directories, templates, and checks into `projects/<project-id>/runtime/context_bundle/`
- generate `knowledge_usage_report.json` that distinguishes primary entries from fallback sources

## Required Manifest Fields

`context_manifest.json` must include at least:

- `references`
- `warnings`
- `knowledge_entry_mode`
- `strict_mode`
- `directory_refs_detected`
- `directory_refs_resolved_to_index`
- `directory_refs_fallback_copied`
- `narrowed_references`
- `facts_extraction_boundary`
- `business_judgment_boundary`
- `experience_translation_boundary`

## Required Usage Report Fields

`knowledge_usage_report.json` must include at least:

- `primary_entries_used`
- `fallback_sources_used`
- `narrowing_actions`
- `broad_reference_warnings`

## Failure Conditions

- A referenced path does not exist.
- A wildcard reference is treated as a direct copy target.
- A reference cannot be copied into `context_bundle/`.
- `context_manifest.json` is not generated.
- strict mode encounters an unresolved broad reference.

## Wiki 路由 Raw 消费

- wiki summary 负责导航与定位，不直接替代原文证据层。
- facts 阶段读取必要 wiki 用于术语和边界校准，默认不读取 raw。
- business 阶段应沿命中 summary 的 `source_refs` 精确读取 raw 文件。
- experience 阶段应沿命中 summary 与 guideline 的 `source_refs` 精确读取 raw 文件。
- raw 引用必须是文件路径，禁止目录级装配。
- `context_manifest.json` 应包含 `knowledge_consumption_plan`。
- `knowledge_usage_report.json` 应记录 `source_ref_chains`。
